# Frontend Architecture

## User app

Recommended:
- React + TypeScript for fastest hackathon web prototype
- responsive mobile-first layout

Alternative:
- Flutter if the team already has Flutter experience

## Screens

```text
/onboarding
/profile/accessibility
/dashboard
/transactions
/transactions/new
/transactions/:id
/helper
/community
/settings
```

## Main dashboard

Show only essential actions:

```text
Welcome, User

[Check Balance]
[Send Money]
[Pay Bills]
[Request Help]
[Community Session]
```

## Send-money screen

Two input modes:

```text
VOICE
"Send ₹5,000 to Ravi"

TEXT
[ Type what you want to do... ]
```

After parsing:

```text
You want to send

₹5,000
to Ravi Kumar

[Edit]
[Continue]
```

## Risk screen

```text
MEDIUM RISK

This amount is higher than your usual payment.

Usual: ₹1,500
Current: ₹5,000

[Confirm with me]
[Cancel]
```

## Helper screen

Never show secrets.

```text
Helping: Demo User

Current step:
Verify transaction

Intent:
₹5,000 → Ravi Kumar

Risk:
MEDIUM

Suggested guidance:
"Please ask the user to verify the amount."

[Pause]
```

## Design principles

- one primary action
- large controls
- simple language
- no unnecessary animation
- visible cancellation
- voice + text parity
- keyboard support
- screen-reader labels
