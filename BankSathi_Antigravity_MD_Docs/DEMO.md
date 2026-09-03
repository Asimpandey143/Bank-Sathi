# Hackathon Demo Script

## Demo scenario

Persona:

> An elderly user wants to send ₹5,000 to Ravi.

### Step 1 — Dashboard

Show:

```text
Welcome, Meena

[Check Balance]
[Send Money]
[Pay Bills]
[Request Help]
```

### Step 2 — Voice

Say:

> "Send five thousand rupees to Ravi."

Show structured interpretation:

```text
Transfer
₹5,000
Ravi Kumar
```

### Step 3 — Risk detection

Show:

```text
MEDIUM RISK

Usual payment: ₹1,500
Current payment: ₹5,000

Reason:
Amount is significantly higher than recent behavior.
```

### Step 4 — Trusted Circle Notification (Daughter)

BankSathi flags ₹5,000 as MEDIUM risk and sends a privacy-safe notification to Meena's daughter (Ananya).

Daughter's Dashboard shows:
```text
🔔 BankSathi Alert

Mom is attempting to send ₹5,000 to Ravi Kumar.
Risk: MEDIUM
Reason: Amount is higher than her recent payments.

[Looks Expected]   [I Don't Recognize This]
```

Daughter taps: **[Looks Expected]**

Emphasize:
> "The daughter provides a second opinion, but never sees OTP or PIN and CANNOT approve or execute the transaction."

### Step 5 — User Review with Second Opinion

Meena sees on her screen:
```text
Trusted Circle Second Opinion:
Your daughter marked this transaction as expected.
You remain responsible for the final decision.

You are sending ₹5,000 to Ravi Kumar
[CONFIRM]  [CANCEL]
```

### Step 6 — User confirmation

Meena (the authenticated user) makes the final authorization and taps Confirm.

### Step 7 — Mock banking

Show:

```text
Processing...
```

Then:

```text
Transaction Successful

₹5,000 sent to Ravi Kumar
Reference: DEMO-123456
```

### Step 8 — Audit

Show:

```text
Risk assessed
User confirmed
Transaction executed
Helper notified
```

## Wow moments

1. Natural voice → structured banking intent.
2. AI explains unusual behavior.
3. Human helper guides without account access.
4. Accessibility adapts the UI.
5. User remains the final authority.

## Important wording

Do not claim:

- "This prevents all fraud."
- "This is RBI-approved."
- "This is a production banking system."

Say:

> "This prototype demonstrates a safer interaction model for accessible digital banking."
