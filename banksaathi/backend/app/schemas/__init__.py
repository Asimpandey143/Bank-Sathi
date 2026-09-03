"""
Pydantic schemas for BankSathi API.

These are the API contract. Models here define what the client sends and receives.

SECURITY RULES:
- Never expose hashed_password in any response schema
- Never accept risk_score or approved flags from client
- Client-provided risk data is always ignored (SECURITY.md)
"""
from .user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    AccessibilityPreferencesUpdate,
    AccessibilityProfileResponse,
)
from .beneficiary import BeneficiaryCreate, BeneficiaryResponse
from .transaction import (
    TransactionDraftCreate,
    TransactionResponse,
    TransactionConfirmRequest,
)
from .helper import (
    HelperInvitationCreate,
    HelperInvitationResponse,
    HelperSessionCreate,
    HelperSessionResponse,
    HelperAbstractedView,
)
from .community import (
    CommunitySessionCreate,
    CommunitySessionResponse,
)
from .audit import AuditEventResponse
from .ai import IntentRequest, IntentResponse

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "AccessibilityPreferencesUpdate",
    "AccessibilityProfileResponse",
    "BeneficiaryCreate",
    "BeneficiaryResponse",
    "TransactionDraftCreate",
    "TransactionResponse",
    "TransactionConfirmRequest",
    "HelperInvitationCreate",
    "HelperInvitationResponse",
    "HelperSessionCreate",
    "HelperSessionResponse",
    "HelperAbstractedView",
    "CommunitySessionCreate",
    "CommunitySessionResponse",
    "AuditEventResponse",
    "IntentRequest",
    "IntentResponse",
]
