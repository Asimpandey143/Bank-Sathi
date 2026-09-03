# Environment Configuration

Create `.env` locally from `.env.example`.

Example:

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://banksaathi:banksaathi@postgres:5432/banksaathi
REDIS_URL=redis://redis:6379/0
JWT_SECRET=replace-me
LLM_PROVIDER=mock
VOICE_PROVIDER=mock
BANK_PROVIDER=mock
```

## Rules

- `.env` is never committed.
- `.env.example` contains placeholders only.
- No real credentials in source code.
- No secrets in screenshots or demo recordings.
