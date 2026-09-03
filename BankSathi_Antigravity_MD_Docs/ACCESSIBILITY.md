# Accessibility Requirements

Accessibility is a core product requirement, not a cosmetic feature.

## Visual

- scalable text
- high contrast
- large touch targets
- minimal visual clutter
- clear focus states
- no color-only status indicators

## Screen reader

Every actionable element must have an accessible label.

Bad:
```text
icon only
```

Good:
```text
"Send money"
```

## Motor

- large buttons
- forgiving tap targets
- minimal precision gestures
- keyboard accessibility on web
- avoid time-limited interactions

## Hearing

Never depend only on audio.

Provide:
- text captions
- visual status
- written confirmation

## Cognitive

Use:
- one task per screen
- simple language
- explicit progress
- transaction stories
- confirmation summaries
- predictable navigation

## Voice

Example:

```text
User: "Send five thousand to Ravi."

AI:
"You want to send ₹5,000 to Ravi.
This is higher than your usual amount.
Would you like me to explain why?"
```

## Adaptive profile

Example:

```json
{
  "font_scale": 1.6,
  "high_contrast": true,
  "screen_reader": true,
  "language": "ta",
  "speech_rate": 0.8,
  "confirmation_mode": "double"
}
```

The supplied concept proposes preferences such as text size, contrast, speech speed, language, confirmation mode, and fraud-protection level. [Source: supplied BankSathi report]
