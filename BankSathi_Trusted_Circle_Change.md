# BankSathi — Trusted Circle & Risk-Based Verification Change

## 1. Purpose

This document supersedes the previous Helper/Screen-Sharing design.

**Remove screen sharing from BankSathi completely.**

BankSathi must NOT require or implement phone-screen sharing between the user and a helper.

The new model is:

> **Trusted Circle + Risk-Based Verification + Second Opinion + User-Only Authorization**

A trusted person such as a daughter, son, spouse, parent, or another verified person can receive a safe transaction notification and provide a second opinion.

The trusted person NEVER gets control of the user's money.

---

# 2. Core Product Principle

## Shared guidance, not shared access

The Trusted Circle member can:

- receive selected transaction-risk notifications
- view a privacy-safe transaction summary
- see why BankSathi considers a transaction unusual
- indicate whether the transaction looks expected
- report that they do not recognize the transaction
- request that the user verify the transaction
- communicate guidance to the user

The Trusted Circle member CANNOT:

- approve a transaction
- execute a transaction
- modify the amount
- modify the beneficiary
- enter OTP
- enter UPI PIN
- enter passwords
- access banking credentials
- access the user's private authentication information
- remotely control the user's device
- screen-share with the user as part of the BankSathi flow

**Only the authenticated user can make the final authorization decision.**

---

# 3. Remove Screen Sharing

The following must be removed from:

- frontend
- backend
- API
- database
- architecture
- workflows
- tests
- documentation
- demo

Remove concepts such as:

```text
screen sharing
remote screen viewing
remote control
screen capture
helper screen session
live screen session
```

Do NOT implement WebRTC or another screen-sharing mechanism for the Trusted Circle feature.

The helper interaction is notification-based.

---

# 4. Rename Helper Concept

Prefer the product term:

## Trusted Circle

A Trusted Circle contains people explicitly trusted by the user.

Examples:

```text
Daughter
Son
Spouse
Parent
Trusted Friend
Verified Community Volunteer
```

The existing internal class/service name `Helper` may be retained temporarily if changing it would create unnecessary migration work, but all new product-facing terminology should use **Trusted Circle**.

Recommended backend naming:

```text
TrustedCircleMember
TrustedCircleService
TrustedCircleNotification
VerificationResponse
```

---

# 5. Risk-Based Notification

Do NOT notify the Trusted Circle for every transaction.

The Risk Engine determines whether additional verification is useful.

Example:

```text
LOW
    ↓
No Trusted Circle notification
    ↓
User confirms normally
```

```text
MEDIUM
    ↓
Optional Trusted Circle notification
    ↓
Second opinion
    ↓
User decides
```

```text
HIGH
    ↓
Trusted Circle notification
    ↓
Second opinion
    ↓
User reviews risk explanation
    ↓
User decides
```

```text
CRITICAL
    ↓
Transaction temporarily blocked according to policy
    ↓
User + Trusted Circle alerted
    ↓
Additional verification
    ↓
User resolves/continues according to security policy
```

The exact thresholds and behavior must follow `AI_ENGINE.md`, `SECURITY.md`, and `PRD.md`.

---

# 6. Trusted Circle Notification

A notification should contain enough information to help the trusted person assess the situation without exposing secrets.

Example:

```text
🔔 BankSathi Alert

A trusted family member is attempting a transaction.

Amount: ₹5,000
Recipient: Ravi Kumar

Risk: MEDIUM

Why?
• Amount is significantly higher than recent transactions.
• Recipient is known.
• Device is trusted.

Does this look expected?

[ Looks Expected ]

[ I Don't Recognize This ]
```

The notification must never contain:

```text
OTP
UPI PIN
Password
Banking credentials
Full authentication secrets
Sensitive account credentials
```

Avoid exposing full account numbers.

Use masked identifiers where necessary.

---

# 7. Second Opinion Model

The Trusted Circle member does NOT "approve" the transaction.

Use language such as:

```text
Looks Expected
I Don't Recognize This
Ask User to Verify
Contact User
```

Never use:

```text
Approve Transaction
Authorize Payment
Execute Payment
Confirm Payment
```

The trusted person's response is an advisory signal only.

---

# 8. Example End-to-End Flow

## Scenario

User wants to send ₹5,000 to Ravi.

### Step 1 — User

```text
"Send ₹5,000 to Ravi."
```

### Step 2 — AI Intent Layer

Produces structured intent:

```json
{
  "intent": "TRANSFER",
  "amount": "5000.00",
  "beneficiary_name": "Ravi"
}
```

### Step 3 — Backend validation

Validate:

```text
user
amount
beneficiary
transaction limits
state
```

### Step 4 — Risk Engine

Example:

```text
Risk: MEDIUM

Reasons:
- Amount is higher than user's recent average.
- Beneficiary is known.
- Device is trusted.
```

### Step 5 — User receives explanation

```text
This payment is larger than your usual transfers.

₹5,000
to Ravi Kumar

Would you like a trusted person to check this?
```

### Step 6 — Trusted Circle notification

Daughter receives:

```text
BankSathi Alert

Mom is attempting to send ₹5,000 to Ravi Kumar.

Risk: MEDIUM

Reason:
The amount is higher than her recent payments.

[Looks Expected]
[I Don't Recognize This]
```

### Step 7 — Daughter responds

Example:

```text
Looks Expected
```

This does NOT approve the payment.

### Step 8 — User sees

```text
Your daughter marked this transaction as expected.

You are still responsible for the final decision.

₹5,000
→ Ravi Kumar

[CONFIRM]
[CANCEL]
```

### Step 9 — User confirms

Only the user can trigger final authorization.

### Step 10 — UPI/Banking provider

The user completes the private authentication in the appropriate banking/UPI interface.

The Trusted Circle member never receives:

```text
OTP
UPI PIN
password
authentication secret
```

### Step 11 — Result

BankSathi records the transaction result and audit event.

---

# 9. Suspicious Transaction Flow

If the daughter selects:

```text
I Don't Recognize This
```

BankSathi should NOT automatically transfer control to the daughter.

Instead:

```text
Daughter
   ↓
"I Don't Recognize This"
   ↓
BankSathi records advisory response
   ↓
User receives warning
   ↓
User reviews transaction
   ↓
User may cancel
```

Example user message:

```text
⚠️ Your trusted contact does not recognize this payment.

They recommend that you verify the recipient and amount before continuing.

₹50,000
→ Unknown Recipient

[Cancel]
[Review Again]
```

For CRITICAL transactions, the Risk Engine policy may temporarily block execution.

---

# 10. Trusted Circle Permissions

Permissions must be explicit.

Example:

```json
{
  "receive_risk_notifications": true,
  "view_transaction_summary": true,
  "provide_second_opinion": true,
  "contact_user": true,
  "execute_transaction": false,
  "approve_transaction": false,
  "modify_transaction": false,
  "view_credentials": false,
  "view_otp": false,
  "view_upi_pin": false,
  "remote_control": false,
  "screen_share": false
}
```

The backend must enforce these permissions.

Never rely only on frontend restrictions.

---

# 11. Privacy Model

Only expose the minimum information necessary.

Trusted Circle members should receive:

```text
Amount
Masked/appropriate beneficiary identity
Risk level
Risk explanation
Advisory actions
```

Do not expose:

```text
Password
OTP
UPI PIN
Bank credentials
Authentication secrets
Unnecessary account information
```

The exact data visibility policy must be centralized in the backend.

---

# 12. API Changes

Replace screen-sharing/session APIs with Trusted Circle APIs.

Recommended endpoints:

```text
POST   /trusted-circle/invite
GET    /trusted-circle/members
POST   /trusted-circle/members/{id}/accept
DELETE /trusted-circle/members/{id}

GET    /trusted-circle/notifications
GET    /trusted-circle/notifications/{id}

POST   /trusted-circle/notifications/{id}/response
```

Transaction-related internal flow:

```text
Transaction
    ↓
RiskEngine
    ↓
VerificationPolicy
    ↓
TrustedCircleNotificationService
    ↓
Notification
```

The response endpoint must only record an advisory decision.

It must NEVER execute a transaction.

---

# 13. Database Changes

Recommended entities:

```text
trusted_circle_members
trusted_circle_notifications
trusted_circle_responses
```

Example:

### trusted_circle_members

```text
id
user_id
trusted_person_id
relationship
status
permissions
created_at
verified_at
revoked_at
```

### trusted_circle_notifications

```text
id
transaction_id
trusted_circle_member_id
risk_level
risk_reasons
amount_display
beneficiary_display
status
created_at
expires_at
```

### trusted_circle_responses

```text
id
notification_id
responder_id
response
comment
created_at
```

Responses:

```text
LOOKS_EXPECTED
NOT_RECOGNIZED
REQUEST_USER_VERIFICATION
```

---

# 14. Notification Security

Notifications must be:

```text
authenticated
authorized
time-limited
audited
privacy-safe
```

A Trusted Circle member must only receive notifications for users who explicitly verified them.

Revoked Trusted Circle members must immediately lose access to future notifications.

Expired notifications must not be actionable.

---

# 15. Audit Logging

Record:

```text
Trusted Circle member added
Trusted Circle member verified
Trusted Circle member revoked
Risk notification generated
Notification delivered
Notification viewed
Second opinion submitted
User viewed second opinion
User cancelled transaction
User confirmed transaction
```

Do not log secrets.

Never log:

```text
OTP
UPI PIN
password
authentication token
```

---

# 16. Frontend Changes

Remove all screen-sharing UI.

Remove buttons such as:

```text
Share Screen
Start Screen Share
View User Screen
Remote Control
```

Replace with:

```text
Trusted Circle
Request Verification
Notify Trusted Person
Trusted Person Response
```

## User UI

Example:

```text
Transaction Review

₹5,000
to Ravi Kumar

⚠️ Medium Risk

This is higher than your usual transfer.

[Ask Trusted Person]
[Continue Without Help]
[Cancel]
```

After response:

```text
Trusted Circle Response

Your daughter marked this transaction
as expected.

This is only a second opinion.
You remain responsible for the final decision.

[CONFIRM]
[CANCEL]
```

---

# 17. Trusted Circle Dashboard

A trusted person should have a simple dashboard:

```text
Trusted Circle
────────────────────────

🔔 1 transaction needs attention

₹5,000 → Ravi Kumar
Risk: Medium

[Review]
```

Review screen:

```text
Transaction Review

Amount: ₹5,000
Recipient: Ravi Kumar

Why BankSathi flagged it:
• Higher than usual amount
• Known recipient
• Trusted device

[Looks Expected]
[I Don't Recognize This]
```

Keep the interface intentionally simple.

---

# 18. Accessibility

Trusted Circle interactions must support:

```text
large text
screen readers
high contrast
large buttons
simple language
voice/read-aloud where appropriate
clear risk descriptions
```

Avoid complicated financial terminology.

Instead of:

```text
Anomalous transaction detected
```

say:

```text
This payment is different from your usual payments.
```

---

# 19. AI Restrictions

The LLM may:

```text
understand user intent
explain risk
generate simple explanations
help communicate transaction context
```

The LLM must NOT:

```text
approve transactions
execute transactions
override risk policy
change transaction amount
change beneficiary
interpret Trusted Circle advice as authorization
```

Architecture:

```text
LLM
 ↓
Structured Intent
 ↓
Backend Validation
 ↓
Risk Engine
 ↓
Trusted Circle Verification
 ↓
USER FINAL DECISION
 ↓
Payment Provider
```

Never:

```text
LLM → Payment Provider
```

Never:

```text
Trusted Circle → Payment Provider
```

---

# 20. Mock Provider for Hackathon

Do not depend on real UPI integration for the core demonstration.

Use:

```text
MockBankingProvider
MockNotificationProvider
MockVoiceProvider
```

The payment architecture should remain provider-agnostic so real integrations can be added later.

The demo should simulate the private UPI authorization step without collecting real PINs or credentials.

---

# 21. Testing Requirements

Add tests proving:

### Trusted Circle

```text
✓ user can add trusted person
✓ trusted person must be verified
✓ user can revoke trusted person
✓ revoked person receives no new notifications
✓ notification is privacy-safe
```

### Permissions

```text
✓ trusted person cannot approve
✓ trusted person cannot execute
✓ trusted person cannot modify amount
✓ trusted person cannot modify beneficiary
✓ trusted person cannot access credentials
✓ trusted person cannot access OTP
✓ trusted person cannot access UPI PIN
✓ screen-sharing endpoints do not exist
```

### Risk

```text
✓ LOW does not unnecessarily notify
✓ MEDIUM follows notification policy
✓ HIGH notifies according to policy
✓ CRITICAL follows blocking/escalation policy
```

### Advisory response

```text
✓ Looks Expected is recorded
✓ I Don't Recognize This is recorded
✓ advisory response cannot execute payment
✓ user sees trusted person's response
✓ user remains final decision-maker
```

### End-to-end

```text
User
 ↓
Natural language request
 ↓
Intent extraction
 ↓
Risk assessment
 ↓
Trusted Circle notification
 ↓
Second opinion
 ↓
User review
 ↓
User confirmation
 ↓
Mock payment provider
 ↓
Audit
```

---

# 22. Demo Story

The primary hackathon demo should be:

## "A daughter protects her mother without getting access to her bank account."

Flow:

```text
Mother:
"Send ₹5,000 to Ravi."

        ↓

BankSathi:
"This amount is higher than your usual payment."

        ↓

BankSathi:
"Would you like your trusted daughter to check this?"

        ↓

Daughter receives notification.

        ↓

Daughter sees:
₹5,000 → Ravi
Medium Risk
Reason: Higher than usual

        ↓

Daughter:
"Looks Expected"

        ↓

Mother sees:
"Your daughter thinks this looks expected."

        ↓

Mother:
CONFIRM

        ↓

Private UPI authentication

        ↓

Payment completed
```

Then demonstrate the suspicious case:

```text
₹50,000 → New Recipient

        ↓

HIGH/CRITICAL

        ↓

Daughter:
"I Don't Recognize This"

        ↓

Mother:
"Your trusted person does not recognize this payment."

        ↓

Mother cancels.
```

This demonstrates both:

```text
ASSISTANCE
+
FRAUD PREVENTION
```

without giving the trusted person financial control.

---

# 23. Architectural Principle

The final architecture must enforce this boundary:

```text
                 USER
                  │
                  ▼
             BankSathi
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   Risk Engine        Trusted Circle
        │                   │
        │             Second Opinion
        │                   │
        └─────────┬─────────┘
                  ▼
           USER DECISION
                  │
                  ▼
          Payment Provider
```

The Trusted Circle is an **advisory layer**, not an authorization layer.

---

# 24. Implementation Instruction for Antigravity

Before coding this change:

1. Read ALL existing `.md` files.
2. Read this document completely.
3. Identify every existing reference to:
   - screen sharing
   - remote control
   - helper session
   - helper approval
   - helper transaction access
4. Create a migration/change checklist.
5. Update documentation first.
6. Then update backend architecture.
7. Then database/API.
8. Then frontend.
9. Then tests.
10. Then demo.

Do not leave old screen-sharing behavior partially implemented.

If any existing Markdown file contradicts this change, treat this document as the explicit latest product decision and update the affected documentation consistently.

---

# 25. Definition of Done

This change is complete only when:

```text
✓ Screen sharing removed
✓ Remote control removed
✓ Trusted Circle implemented
✓ Risk-based notifications implemented
✓ Second-opinion responses implemented
✓ User remains final authority
✓ Sensitive credentials never exposed
✓ Backend enforces permissions
✓ Advisory responses cannot execute payments
✓ Audit logging implemented
✓ Accessibility maintained
✓ Tests updated
✓ Demo updated
✓ All .md documentation updated
```

## Final Product Statement

> **BankSathi gives families a safe way to help vulnerable users make better financial decisions—without giving family members access to their money.**

The trusted person provides a second opinion.

**The user always remains in control.**
