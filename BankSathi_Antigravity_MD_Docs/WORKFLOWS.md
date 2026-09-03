# User Workflows

## Workflow A — Onboarding

```text
Register
  ↓
Create accessibility profile
  ↓
Choose "With Help" or "By Myself"
  ↓
If helper → invite helper
  ↓
Set transaction limits/preferences
  ↓
Dashboard
```

## Workflow B — Send money

```text
User says/types:
"Send ₹5,000 to Ravi"
        ↓
Intent extraction
        ↓
Validate beneficiary + amount
        ↓
Risk engine
        ↓
LOW / MEDIUM / HIGH / CRITICAL
        ↓
Helper guidance OR AI companion
        ↓
Transaction story
        ↓
User-only final confirmation
        ↓
Mock bank
        ↓
Success / failure
        ↓
Audit + notification
```

## Workflow C — Trusted Circle Second Opinion

```text
Risk engine flags transaction (MEDIUM / HIGH)
        ↓
Privacy-safe alert generated for Trusted Circle member (e.g. daughter)
        ↓
Daughter views privacy-safe summary:
- Amount: ₹5,000
- Recipient: Ravi Kumar
- Risk Level: MEDIUM
- Reasons: Higher than recent average
        ↓
Daughter submits advisory second opinion:
[Looks Expected] OR [I Don't Recognize This]
        ↓
User sees advisory response:
"Your daughter marked this transaction as expected."
        ↓
User retains sole authorization authority:
[CONFIRM PAYMENT] or [CANCEL]
        ↓
User confirms on own device
        ↓
Mock banking completes transfer
```

Trusted Circle Notification Example:

```text
🔔 BankSathi Alert

Mom is attempting to send ₹5,000 to Ravi Kumar.
Risk: MEDIUM
Reason: Amount is higher than her recent payments.

[Looks Expected]   [I Don't Recognize This]
```

Never display OTP, PIN, passwords, banking credentials, or full account secrets. No screen sharing is used.

## Workflow D — AI companion

If no helper is available:

```text
User input
   ↓
AI conversation
   ↓
Risk explanation
   ↓
Confirmation questions
   ↓
Final confirmation screen
```

The AI is a guide, not the transaction authority.

## Workflow E — Community session

```text
Browse sessions
   ↓
Join secure room
   ↓
Verified host explains a banking task
   ↓
Users follow privately
   ↓
AI safety checks remain active
   ↓
Session summary
   ↓
Rating/feedback
```

The supplied concept describes 30–45 minute moderated sessions with private user banking screens. [Source: supplied BankSathi report]
