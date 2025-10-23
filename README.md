# smartSalud_V2

WhatsApp appointment system for CESFAM - Booking + Google Calendar sync.

## Setup (5 minutes)

```bash
cd smartSalud_V2
cp .env.example .env  # Edit with your credentials

# Start services
cd docker && docker-compose up -d && cd ..

# Install & run migrations
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
PYTHONPATH=$PWD ./venv/bin/alembic upgrade head

# Start API
PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001
```

**Access**: [http://localhost:8001](http://localhost:8001) | Docs: `/docs` | Dashboard: `/dashboard`

## What It Does

- Patient books appointment via WhatsApp (Twilio)
- NLP detects intent (Groq LLM + fallback regex)
- System creates appointment in DB
- Automatically syncs to doctor's Google Calendar
- Doctor confirms/cancels from calendar or WhatsApp

## Key Commands

```bash
# Tests
PYTHONPATH=$PWD ./venv/bin/pytest tests/unit/ -v

# Create migration
PYTHONPATH=$PWD ./venv/bin/alembic revision --autogenerate -m "description"

# Format code
black src/ tests/
ruff check src/ tests/
```

## Configuration

Edit `.env` with:

- `DATABASE_URL` - PostgreSQL connection
- `GROQ_API_KEY` - LLM for NLP
- `TWILIO_ACCOUNT_SID` - WhatsApp bot
- `GOOGLE_CALENDAR_CREDENTIALS_FILE` - Calendar sync

See `.env.example` for all variables.

## Reference

- **Development guide**: [.claude/CLAUDE.md](.claude/CLAUDE.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Performance**: [docs/SCALABILITY_ANALYSIS.md](docs/SCALABILITY_ANALYSIS.md)

## Status

✅ Phase 1 complete: Booking + one-way calendar sync working
⏳ Next: WhatsApp integration, admin dashboard

## License

Proprietary - CESFAM Futrono
