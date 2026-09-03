# Product Requirements Document — BankSathi

## 1. Problem

Digital banking can become difficult or intimidating for elderly users and people with disabilities. The challenge is not only interface complexity; users may need trusted guidance while retaining control of their money.

## 2. Product vision

BankSathi turns banking into a simple, supported, and safe experience by combining:

- accessible interaction
- conversational AI
- deterministic fraud/risk checks
- trusted human guidance
- cognitive-friendly transaction explanations

The supplied concept explicitly frames the solution around a verified assistance network and an AI mediator, with the safety principle of shared guidance rather than shared access. [Source: supplied BankSathi report]

## 3. Target users

### Primary
- elderly digital-banking users
- visually impaired users
- users with motor disabilities
- users with hearing disabilities
- users who benefit from cognitive simplification

### Secondary
- trusted circle members (e.g., daughter, son, spouse, parent)
- community volunteers
- accessibility/community organizations

## 4. User stories

### User
- As a user, I want to send money by speaking naturally.
- As a user, I want the system to explain unusual transactions.
- As a user, I want a trusted person to give a second opinion without giving them account control.
- As a user, I want large text/high contrast/voice assistance.
- As a user, I want to cancel a transaction at any point before final confirmation.

### Trusted Circle Member
- As a trusted circle member, I want to receive privacy-safe risk notifications for unusual transactions.
- As a trusted circle member, I want to provide an advisory second opinion ("Looks Expected" or "I Don't Recognize This").
- As a trusted circle member, I must never see OTP/PIN, passwords, or approve/execute transactions.
- As a trusted circle member, I will not engage in screen sharing or remote control.

## 5. MVP acceptance criteria

A demo user can say:

> Send ₹5,000 to Ravi.

The system:
1. extracts amount and beneficiary
2. checks beneficiary history
3. calculates risk (e.g., MEDIUM)
4. explains unusual amount
5. triggers risk-based notification to Trusted Circle member (e.g., daughter)
6. receives advisory second opinion from Trusted Circle ("Looks Expected")
7. shows a final confirmation and advisory summary on the user's device
8. executes only after user confirmation
9. records an audit event
10. shows success/failure
8. executes only after user confirmation
9. records an audit event
10. shows success/failure

## 6. Risk levels

- LOW → normal confirmation
- MEDIUM → additional explanation + double confirmation
- HIGH → step-up authentication simulation
- CRITICAL → block transaction and alert user

These levels are product policy, not LLM decisions.

## 7. Out of scope for hackathon MVP

- real bank/UPI money movement
- real Aadhaar/PAN storage
- production KYC
- production fraud guarantees
- production biometric implementation
- production voice-cloning of family members
- autonomous transaction approval

## 8. Success metrics

Prototype metrics:
- intent extraction accuracy
- risk-rule latency
- transaction completion rate
- confirmation error rate
- helper session latency
- accessibility task completion
- test coverage
