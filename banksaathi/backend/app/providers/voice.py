"""
Voice Provider Abstraction & Implementation

Architecture: Provider Pattern (ADR-008)
Provides speech synthesis (TTS) and transcription (STT) capabilities.
In browser: Uses Web Speech API (SpeechRecognition + SpeechSynthesis).
On backend: MockVoiceProvider formats spoken guidance and accessibility descriptions.
"""
from decimal import Decimal
from typing import Protocol


class VoiceProvider(Protocol):
    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """Transcribe spoken audio to text."""
        ...

    async def synthesize(self, text: str, language: str = "en", speech_rate: float = 1.0) -> dict:
        """Synthesize text to speech metadata / audio payload."""
        ...


class MockVoiceProvider:
    """
    Mock voice provider for hackathon prototype.
    Generates standardized audio summaries, screen reader text, and visual captions.
    """

    def generate_transaction_speech_summary(
        self,
        amount: Decimal,
        currency: str,
        beneficiary_name: str,
        risk_level: str,
        risk_reasons: list[str] | None = None,
    ) -> dict:
        """
        Generate spoken narration text and visual synchronized captions for accessibility.
        Complies with WCAG AAA captioning and audio guidance requirements.
        """
        curr_label = "rupees" if currency.upper() == "INR" else currency

        # 1. Main spoken script
        narration = f"Please confirm your payment of {amount:,.2f} {curr_label} to {beneficiary_name}."

        # 2. Risk explanation in clear, non-jargon language
        if risk_level == "CRITICAL":
            risk_guidance = "Warning: This transaction has been stopped for your security."
        elif risk_level in ("HIGH", "MEDIUM"):
            risk_guidance = f"Note: The security level is {risk_level.title()} because this amount is higher than your usual payments."
        else:
            risk_guidance = "Everything looks normal."

        action_prompt = "Press the large green button to confirm, or press cancel to go back."

        full_speech = f"{narration} {risk_guidance} {action_prompt}"

        return {
            "speech_text": full_speech,
            "caption_text": f"Sending ₹{amount:,.2f} to {beneficiary_name}. ({risk_level} Risk). {risk_guidance}",
            "language": "en-IN",
            "confirm_prompt": "Confirm payment",
            "cancel_prompt": "Cancel payment",
        }


_mock_voice_instance = MockVoiceProvider()


def get_voice_provider() -> MockVoiceProvider:
    return _mock_voice_instance
