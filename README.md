# smartSalud_V2

WhatsApp bot for medical appointment confirmations - Clean architecture rebuild.

## 🎯 Features

- ✅ WhatsApp webhook (Twilio)
- ✅ NLP intent detection (Groq + regex fallback)
- ✅ CONFIRM/CANCEL appointments
- ✅ Google Calendar synchronization
- ✅ Scheduled daily reminders
- ✅ Monitoring dashboard
- ✅ Admin REST API

## 🏗️ Architecture

```
smartSalud_V2/
├── src/
│   ├── whatsapp/       # WhatsApp integration
│   ├── calendar/       # Google Calendar
│   ├── nlp/            # NLP with Groq
│   ├── database/       # SQLAlchemy models
│   ├── scheduler/      # APScheduler tasks
│   └── monitoring/     # Dashboard
├── tests/              # Unit + integration tests
└── docker/             # Docker Compose
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Local Development

1. **Clone and setup**:
```bash
cd smartSalud_V2
cp .env.example .env
# Edit .env with your credentials
```

2. **Start services**:
```bash
cd docker
docker-compose up -d
```

3. **Install dependencies**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Run migrations**:
```bash
alembic upgrade head
```

5. **Start API**:
```bash
uvicorn src.api.main:app --reload
```

6. **Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Dashboard: http://localhost:8000/dashboard

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires API keys)
pytest tests/integration/ -v

# Coverage
pytest --cov=src --cov-report=html
```

## 📝 Environment Variables

See [.env.example](.env.example) for all required variables:

- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `GROQ_API_KEY`: Groq API key
- `TWILIO_ACCOUNT_SID`: Twilio credentials
- `GOOGLE_CALENDAR_CREDENTIALS_FILE`: OAuth2 token

## 🔧 Development

### Code Quality

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📦 Deployment

### Railway

1. Connect GitHub repository
2. Add environment variables
3. Deploy automatically on push to main

### Docker

```bash
docker build -t smartsalud-v2 -f docker/Dockerfile .
docker run -p 8000:8000 --env-file .env smartsalud-v2
```

## 📊 Monitoring

- Dashboard: `/dashboard`
- Health check: `/health`
- Logs: Structured JSON with structlog

## 🤝 Contributing

This is a clean rebuild from scratch. NO code migrated from v1.

## 📄 License

Proprietary - CESFAM Futrono

## 🔗 Links

- [Architecture Documentation](ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
