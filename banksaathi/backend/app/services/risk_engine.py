"""
Deterministic Risk Engine

Pure business logic for risk scoring and explainability.

CRITICAL SAFETY RULES (ADR-006, AI_ENGINE.md, SECURITY.md):
- Deterministic rules only — the LLM NEVER modifies or overrides risk results
- Configurable thresholds and weights from Settings
- Returns transparent, human-readable and machine-readable reasons
- Frontend inputs for risk are NEVER trusted

Policy:
  0–24   → LOW
  25–49  → MEDIUM
  50–74  → HIGH
  75+    → CRITICAL (blocked)
"""
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum

from app.config import Settings, get_settings


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskContext:
    """Input context for deterministic risk assessment."""
    amount: Decimal
    average_amount: Decimal | None = None
    beneficiary_is_new: bool = False
    is_unusual_time: bool = False
    is_untrusted_device: bool = False
    daily_spent_so_far: Decimal = Decimal("0.00")
    daily_limit: Decimal | None = None


@dataclass
class RiskDecision:
    """Output decision from risk assessment."""
    score: int
    level: RiskLevel
    reasons: list[str] = field(default_factory=list)
    is_blocked: bool = False


class RiskEngine:
    """
    Evaluates transaction risk based on configurable weights and thresholds.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def evaluate(self, ctx: RiskContext) -> RiskDecision:
        score = 0
        reasons: list[str] = []

        daily_limit = ctx.daily_limit or Decimal(str(self.settings.daily_transaction_limit))
        remaining_daily_limit = daily_limit - ctx.daily_spent_so_far

        # 1. Daily limit check (Critical violation)
        if ctx.amount > remaining_daily_limit:
            return RiskDecision(
                score=100,
                level=RiskLevel.CRITICAL,
                reasons=[
                    f"Amount exceeds remaining daily limit of INR {remaining_daily_limit:.2f}."
                ],
                is_blocked=True,
            )

        # 2. Amount deviation check
        if ctx.average_amount and ctx.average_amount > 0:
            if ctx.amount > (ctx.average_amount * 2):
                score += self.settings.risk_weight_amount_deviation
                reasons.append(
                    f"Amount (INR {ctx.amount}) is significantly higher than your recent average (INR {ctx.average_amount})."
                )

        # 3. New beneficiary check
        if ctx.beneficiary_is_new:
            score += self.settings.risk_weight_new_beneficiary
            reasons.append("New beneficiary with no previous transfer history.")

        # 4. Unusual time check
        if ctx.is_unusual_time:
            score += self.settings.risk_weight_unusual_time
            reasons.append("Transaction initiated at an unusual time.")

        # 5. Untrusted device check
        if ctx.is_untrusted_device:
            score += self.settings.risk_weight_untrusted_device
            reasons.append("Transaction initiated from an unrecognized or untrusted device.")

        # Cap score at 100
        score = min(score, 100)

        # Determine Risk Level from configurable thresholds
        if score >= self.settings.risk_threshold_critical:
            level = RiskLevel.CRITICAL
            is_blocked = True
        elif score >= self.settings.risk_threshold_high:
            level = RiskLevel.HIGH
            is_blocked = False
        elif score >= self.settings.risk_threshold_medium:
            level = RiskLevel.MEDIUM
            is_blocked = False
        else:
            level = RiskLevel.LOW
            is_blocked = False

        if not reasons:
            reasons.append("Normal transaction parameters within standard patterns.")

        return RiskDecision(
            score=score,
            level=level,
            reasons=reasons,
            is_blocked=is_blocked,
        )
