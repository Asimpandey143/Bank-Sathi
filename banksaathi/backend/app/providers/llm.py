"""
LLM Provider Abstraction & Implementations

Architecture: Provider Pattern (ADR-007, AI_ENGINE.md)
Provides natural language intent parsing with guaranteed deterministic fallback.

SAFETY RULES:
- LLM output is untrusted input — always parsed into IntentResponse with Pydantic
- The LLM NEVER interacts directly with the BankingProvider or executes transactions
- Mandatory deterministic fallback ensures offline demo reliability
"""
from decimal import Decimal
import re
from typing import Protocol

from app.config import Settings, get_settings
from app.schemas.ai import IntentResponse

# Common number word mapping for Indian English / conversational banking
WORD_TO_NUM: dict[str, int] = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000, "lakh": 100000, "crore": 10000000,
}


def parse_spoken_number(text: str) -> Decimal | None:
    """
    Parse numbers from digits (5000, 5k, 5,000) or words ('five thousand').
    """
    # 1. Match '5k' or '5.5k'
    k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", text, re.IGNORECASE)
    if k_match:
        val = float(k_match.group(1)) * 1000
        return Decimal(f"{val:.2f}")

    # 2. Match standard digits (comma-formatted or plain digits)
    # Note: (?:,\d{3})+ ensures comma-grouped numbers are matched, else \d+ matches full number
    digit_match = re.search(
        r"(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE,
    )
    if digit_match:
        raw = digit_match.group(1).replace(",", "")
        try:
            num = float(raw)
            if num > 0:
                return Decimal(f"{num:.2f}")
        except ValueError:
            pass

    # 3. Match word-based numbers e.g. "five thousand", "two hundred fifty"
    words = re.findall(r"\b[a-z]+\b", text.lower())
    current = 0
    total = 0
    found_number = False

    for word in words:
        if word in WORD_TO_NUM:
            found_number = True
            val = WORD_TO_NUM[word]
            if val in (100, 1000, 100000, 10000000):
                current = max(1, current) * val
                total += current
                current = 0
            else:
                current += val

    total += current
    if found_number and total > 0:
        return Decimal(f"{total:.2f}")

    return None


class LLMProvider(Protocol):
    async def parse_intent(self, text: str) -> IntentResponse:
        """Parse natural language into structured banking intent."""
        ...


class MockIntentProvider:
    """
    Deterministic NLP intent parser.
    Fulfills the mandatory fallback requirement for hackathon demo reliability.
    """

    async def parse_intent(self, text: str) -> IntentResponse:
        cleaned = text.strip()
        lower = cleaned.lower()

        # 1. Balance check
        if any(phrase in lower for phrase in ("balance", "how much money", "account balance", "check funds")):
            return IntentResponse(
                intent="CHECK_BALANCE",
                confidence=0.98,
                clarification_needed=False,
            )

        # 2. Transaction list / history
        if any(phrase in lower for phrase in ("transactions", "recent payments", "history", "statement", "passbook")):
            return IntentResponse(
                intent="LIST_TRANSACTIONS",
                confidence=0.96,
                clarification_needed=False,
            )

        # 3. Help request
        if any(phrase in lower for phrase in ("help", "assist", "support", "call helper", "need someone")):
            return IntentResponse(
                intent="HELP",
                confidence=0.95,
                clarification_needed=False,
            )

        # 4. Cancel
        if lower in ("cancel", "stop", "abort", "nevermind", "go back"):
            return IntentResponse(
                intent="CANCEL",
                confidence=0.99,
                clarification_needed=False,
            )

        # 5. Bill Payment
        if "bill" in lower or any(b in lower for b in ("electricity", "water", "gas", "recharge", "broadband")):
            amount = parse_spoken_number(cleaned)
            # Find bill type
            bill_name = "Utility Bill"
            for b in ("electricity", "water", "gas", "mobile recharge", "broadband"):
                if b in lower:
                    bill_name = f"{b.capitalize()} Bill"
                    break

            return IntentResponse(
                intent="PAY_BILL",
                amount=amount,
                currency="INR",
                beneficiary_name=bill_name,
                confidence=0.92 if amount else 0.75,
                clarification_needed=amount is None,
                clarification_question="What is the bill amount?" if amount is None else None,
            )

        # 6. Money Transfer ("send 5000 to Ravi", "pay Ravi 5k", "transfer 1500 to Priya Sharma")
        if any(w in lower for w in ("send", "transfer", "pay", "give")):
            amount = parse_spoken_number(cleaned)

            # Extract beneficiary name:
            # Look for pattern: "to [Name]" or "pay [Name] [amount]"
            beneficiary = None
            to_match = re.search(r"\bto\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)", cleaned, re.IGNORECASE)
            if to_match:
                cand = to_match.group(1).strip()
                # Strip leading verb if user says "want to pay Ravi"
                cand = re.sub(r"^(?:pay|send|transfer|give)\s+", "", cand, flags=re.IGNORECASE).strip()
                words = cand.lower().split()
                if (
                    cand.lower() not in ("rupees", "inr", "money", "the", "bill", "my", "account")
                    and not all(w in WORD_TO_NUM or w.isdigit() for w in words)
                ):
                    beneficiary = cand

            if not beneficiary:
                pay_match = re.search(r"\b(?:pay|send|transfer|give)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\b", cleaned, re.IGNORECASE)
                if pay_match:
                    cand = pay_match.group(1).strip()
                    words = cand.lower().split()
                    if (
                        cand.lower() not in ("rupees", "inr", "money", "the", "bill", "my", "account", "to")
                        and not all(w in WORD_TO_NUM or w.isdigit() for w in words)
                    ):
                        beneficiary = cand

            # Check confidence and missing info
            clarification_needed = False
            clarification_q = None

            if not beneficiary and not amount:
                return IntentResponse(
                    intent="TRANSFER",
                    confidence=0.60,
                    clarification_needed=True,
                    clarification_question="Who would you like to send money to and how much?",
                )
            elif not beneficiary:
                clarification_needed = True
                clarification_q = f"How much is ₹{amount}. Who would you like to send this to?"
            elif not amount:
                clarification_needed = True
                clarification_q = f"How much money would you like to send to {beneficiary}?"

            return IntentResponse(
                intent="TRANSFER",
                amount=amount,
                currency="INR",
                beneficiary_name=beneficiary,
                confidence=0.96 if (beneficiary and amount) else 0.70,
                clarification_needed=clarification_needed,
                clarification_question=clarification_q,
            )

        # 7. Fallback for unparseable input
        return IntentResponse(
            intent="UNKNOWN",
            confidence=0.30,
            clarification_needed=True,
            clarification_question="I didn't quite catch that. You can say 'Send ₹5,000 to Ravi' or 'Check balance'.",
        )


class GeminiLLMProvider:
    """
    Adapter for Google Gemini LLM API with guaranteed fallback to MockIntentProvider.
    """

    def __init__(self, api_key: str, fallback: MockIntentProvider | None = None) -> None:
        self.api_key = api_key
        self.fallback = fallback or MockIntentProvider()

    async def parse_intent(self, text: str) -> IntentResponse:
        if not self.api_key:
            return await self.fallback.parse_intent(text)

        try:
            # If google-genai is available, use it with structured schema
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = (
                f"You are BankSathi's banking intent extractor. Extract structured banking intent from this user text: '{text}'.\n"
                "Return the intent (CHECK_BALANCE, TRANSFER, PAY_BILL, LIST_TRANSACTIONS, HELP, CANCEL, UNKNOWN), "
                "amount (numeric decimal or null), currency ('INR'), beneficiary_name (string or null), "
                "confidence (float between 0 and 1)."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=IntentResponse,
                ),
            )
            if response.text:
                import json
                data = json.loads(response.text)
                return IntentResponse.model_validate(data)
        except Exception:
            # Any failure falls back to deterministic parser for 100% hackathon reliability
            pass

        return await self.fallback.parse_intent(text)


# Provider factory
def get_llm_provider(settings: Settings | None = None) -> LLMProvider:
    s = settings or get_settings()
    if s.llm_provider == "gemini" and s.llm_api_key:
        return GeminiLLMProvider(api_key=s.llm_api_key)
    return MockIntentProvider()
