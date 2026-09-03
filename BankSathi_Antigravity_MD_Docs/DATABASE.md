# Database Design

Use PostgreSQL.

## users

```text
id UUID PK
phone_hash VARCHAR UNIQUE
name VARCHAR
role VARCHAR
created_at TIMESTAMPTZ
```

Do not store Aadhaar numbers in the MVP.

## accessibility_profiles

```text
user_id UUID PK/FK
language VARCHAR
font_scale NUMERIC
high_contrast BOOLEAN
screen_reader BOOLEAN
speech_rate NUMERIC
confirmation_mode VARCHAR
fraud_protection VARCHAR
```

## beneficiaries

```text
id UUID PK
user_id UUID FK
display_name VARCHAR
masked_account VARCHAR
trust_level VARCHAR
first_seen_at TIMESTAMPTZ
last_used_at TIMESTAMPTZ
```

## transactions

```text
id UUID PK
user_id UUID FK
beneficiary_id UUID FK
amount NUMERIC(12,2)
currency VARCHAR(3)
intent VARCHAR
status VARCHAR
risk_score INTEGER
risk_level VARCHAR
risk_reasons JSONB
bank_reference VARCHAR NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

## trusted_circle_members

```text
id UUID PK
user_id UUID FK
trusted_person_id UUID FK
relationship VARCHAR
status VARCHAR (PENDING, ACTIVE, REVOKED)
permissions JSON
created_at TIMESTAMPTZ
verified_at TIMESTAMPTZ NULL
revoked_at TIMESTAMPTZ NULL
```

## trusted_circle_notifications

```text
id UUID PK
transaction_id UUID FK
trusted_circle_member_id UUID FK
risk_level VARCHAR
risk_reasons JSON
amount_display VARCHAR
beneficiary_display VARCHAR
status VARCHAR (PENDING, RESPONDED, EXPIRED)
created_at TIMESTAMPTZ
expires_at TIMESTAMPTZ
```

## trusted_circle_responses

```text
id UUID PK
notification_id UUID FK
responder_id UUID FK
response VARCHAR (LOOKS_EXPECTED, NOT_RECOGNIZED, REQUEST_USER_VERIFICATION)
comment TEXT NULL
created_at TIMESTAMPTZ
```

## community_sessions

```text
id UUID PK
host_id UUID FK
topic VARCHAR
scheduled_at TIMESTAMPTZ
status VARCHAR
max_participants INTEGER
created_at TIMESTAMPTZ
```

## audit_events

```text
id UUID PK
actor_user_id UUID
event_type VARCHAR
resource_type VARCHAR
resource_id UUID
metadata JSONB
created_at TIMESTAMPTZ
```

Never store:
- OTP
- PIN
- passwords in plaintext
- bank login credentials
- raw authentication secrets
