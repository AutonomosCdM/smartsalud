# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Objetivo del Proyecto

Sistema WhatsApp de confirmación de citas médicas con arquitectura limpia, modular y escalable.

## 📁 Estructura de Carpetas Completa

```
smartSalud_V2/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app + router registration
│   │   └── dependencies.py      # Dependency injection
│   │
│   ├── whatsapp/
│   │   ├── routes.py            # Webhook endpoint (1 archivo, ~100 líneas)
│   │   ├── handlers.py          # CONFIRM/CANCEL handlers (~150 líneas)
│   │   ├── service.py           # Twilio API calls
│   │   └── templates.py         # Message templates español
│   │
│   ├── calendar/
│   │   ├── service.py           # Google Calendar operations
│   │   └── colors.py            # Status → color mapping
│   │
│   ├── nlp/
│   │   ├── service.py           # Groq + regex con circuit breaker
│   │   ├── intents.py           # Intent enum (CONFIRM, CANCEL, UNKNOWN)
│   │   └── patterns.py          # Regex patterns español chileno
│   │
│   ├── database/
│   │   ├── models.py            # Patient, Appointment, Interaction
│   │   ├── repository.py        # CRUD operations
│   │   └── connection.py        # Async engine + session factory
│   │
│   ├── scheduler/
│   │   ├── tasks.py             # APScheduler daily reminders
│   │   └── reminders.py         # Logic para enviar confirmaciones
│   │
│   ├── monitoring/
│   │   └── dashboard.py         # Simple /dashboard endpoint con métricas
│   │
│   └── core/
│       ├── config.py            # Pydantic Settings (env vars)
│       └── exceptions.py        # Custom exceptions
│
├── tests/
│   ├── unit/                    # NLP, handlers, repository
│   ├── integration/             # Groq, Twilio, Calendar
│   └── fixtures/                # Synthetic patients/appointments
│
├── alembic/
│   ├── env.py                   # Alembic async config
│   └── versions/
│       └── 001_initial_schema.py
│
├── docker/
│   ├── Dockerfile               # Python 3.11 slim
│   └── docker-compose.yml       # PostgreSQL + Redis + API
│
├── .env.example
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

## 🗄️ Modelos de Base de Datos

### Patient

```python
id, rut (unique), phone (unique), first_name, last_name, email, created_at, updated_at
```

### Appointment

```python
id, patient_id (FK), appointment_date, doctor_name, specialty,
status (enum), calendar_event_id, notes, created_at, updated_at
```

**Status enum**: PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW

### Interaction (audit log)

```python
id, patient_id (FK), appointment_id (FK nullable), message_from, message_to,
message_body, detected_intent, confidence_score, twilio_message_sid (unique), created_at
```

## ⚙️ Funcionalidades V2

### Core (Must Have)

- **WhatsApp Webhook**: Recibir mensajes → NLP → CONFIRM/CANCEL → responder
- **NLP con Circuit Breaker**: Groq primary, regex fallback, auto-recovery exponencial
- **Google Calendar Sync**: Crear eventos + actualizar colores por status
- **PostgreSQL Async**: Pool pre-ping, transacciones explícitas

### Opcionales (Must Have)

- **Scheduled Reminders**: Tarea diaria envía confirmaciones a citas de mañana
- **Monitoring Dashboard**: GET /dashboard con métricas básicas (mensajes, tasa confirmación, errores)
- **API REST Admin**: POST /api/patients, POST /api/appointments, GET /api/stats

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI (async), Python 3.11
- **Database**: PostgreSQL 15, SQLAlchemy 2.0 (async), Alembic
- **Cache**: Redis (conversation state + task queue)
- **NLP**: Groq API + regex fallback
- **WhatsApp**: Twilio API
- **Calendar**: Google Calendar API
- **Scheduler**: APScheduler
- **Logging**: Structlog (JSON logs)
- **Testing**: Pytest, Pytest-asyncio
- **Deploy**: Docker + Railway

## 📋 Plan de Implementación (Fases)

### Fase 1: Foundation (Día 1)

- Crear estructura de carpetas
- Setup Docker Compose (PostgreSQL + Redis)
- Modelos SQLAlchemy + Alembic initial migration
- Config con Pydantic Settings
- FastAPI main.py básico con health endpoint

### Fase 2: Core WhatsApp (Día 2)

- WhatsApp webhook endpoint
- NLP service (Groq + regex + circuit breaker)
- CONFIRM handler (DB + Calendar)
- CANCEL handler (DB + Calendar)
- Tests unitarios

### Fase 3: Calendar Integration (Día 3)

- Google Calendar service
- Crear eventos
- Actualizar colores por status
- OAuth2 flow setup
- Tests integración

### Fase 4: Scheduler + Reminders (Día 4)

- APScheduler setup
- Daily reminder task
- Template de mensaje recordatorio
- Tests scheduled tasks

### Fase 5: Monitoring + Admin API (Día 5)

- Dashboard endpoint con métricas
- Admin REST API (CRUD pacientes/citas)
- Stats endpoint
- Documentación OpenAPI

### Fase 6: Testing + Deploy (Día 6)

- Tests E2E completos
- Docker build + optimize
- Deploy Railway
- Smoke tests producción

## Essential Commands

### Development Setup

```bash
# Start infrastructure (PostgreSQL + Redis)
cd docker && docker-compose up -d postgres redis

# Install dependencies (Python 3.11+)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with actual credentials

# Run migrations
alembic upgrade head

# Start API (with hot reload)
uvicorn src.api.main:app --reload
```

### Testing

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires API keys in .env)
pytest tests/integration/ -v

# With coverage report
pytest --cov=src --cov-report=html
pytest --cov=src --cov-report=term-missing

# Single test file
pytest tests/unit/test_nlp.py -v

# Single test function
pytest tests/unit/test_nlp.py::test_intent_detection -v
```

### Code Quality

```bash
# Format code (auto-fix)
black src/ tests/

# Lint (auto-fix where possible)
ruff check --fix src/ tests/

# Type checking
mypy src/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Database Migrations

```bash
# Create new migration (auto-detect model changes)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Docker Operations

```bash
# Start all services (DB + Redis + API)
cd docker && docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild API container
docker-compose up -d --build api

# Access database
docker exec -it smartsalud_v2_db psql -U smartsalud_user -d smartsalud_v2
```

## Architecture Principles

### Clean Architecture

- **Modular separation**: Cada dominio (whatsapp, nlp, calendar, database) es autocontenido
- **Dependency injection**: Services reciben dependencias, no las crean
- **No circular imports**: Dirección clara de dependencias (api → handlers → services → database)
- **Separación clara**: WhatsApp / Calendar / NLP / Database son módulos independientes

### Async-First

- ALL database operations use SQLAlchemy async
- ALL I/O operations (Groq, Twilio, Google Calendar) are async
- Connection pooling configured (10 base + 5 overflow)
- Use `asyncpg` driver (NOT psycopg2)

### Error Handling Strategy

- Custom exceptions in `src/core/exceptions.py` with context
- Structured logging with `structlog` (JSON in production, console in dev)
- Graceful degradation: NLP uses regex fallback if Groq fails
- NEVER expose internal errors to WhatsApp users

### Module Structure Pattern

Each module follows this pattern:

```
src/{module}/
├── routes.py      # FastAPI endpoints (if public)
├── handlers.py    # Business logic
├── service.py     # External API wrapper
└── models.py      # Data models (optional)
```

## Key Implementation Details

### Database

- **Models**: SQLAlchemy ORM in `src/database/models.py`
- **Connection**: Async engine in `src/database/connection.py` with pre-ping (Railway safety)
- **Clean schema**: Simple relational design
- **Indexes**: Defined on `appointment_date + status`, `interactions.created_at`

### NLP Intent Detection

- **Primary**: Groq API (llama-3.3-70b-versatile) with 5s timeout
- **Fallback**: Regex patterns if Groq fails
- **Circuit breaker**: Auto-recovery with exponential backoff
- **Intents**: CONFIRM, CANCEL, UNKNOWN
- **Confidence**: Groq 0.8-0.95, Regex 0.7
- Location: `src/nlp/`

### WhatsApp Integration

- **Webhook**: POST /api/webhook/whatsapp (Twilio)
- **Response**: TwiML format with Spanish templates
- **Flow**: Receive → NLP → Handler → Update DB/Calendar → Respond
- **Templates**: All user-facing messages in Spanish (español chileno)
- Location: `src/whatsapp/`

### Google Calendar

- **OAuth2**: token.json required for authentication
- **Color coding**:
  - Yellow (#FBD75B): PENDING
  - Green (#7AE7BF): CONFIRMED
  - Red (#F06292): CANCELLED
- **Sync**: Update calendar color when appointment status changes
- Location: `src/calendar/`

### Scheduler

- **Engine**: APScheduler (NOT Celery)
- **Daily reminder**: 9:00 AM (configurable in .env)
- **Logic**: Find PENDING appointments for tomorrow → send WhatsApp reminders
- Location: `src/scheduler/`

## Configuration

All config in `src/core/config.py` using Pydantic Settings:

- Loads from `.env` file
- Validates on startup (e.g., DATABASE_URL must have +asyncpg)
- Access via `from src.core.config import settings`

### Critical Environment Variables

- `DATABASE_URL`: Must use `postgresql+asyncpg://` (NOT postgresql://)
- `GROQ_API_KEY`: Must start with `gsk_`
- `TWILIO_ACCOUNT_SID`: Must match pattern `AC[a-f0-9]{32}`
- `TWILIO_CONTENT_SID_CONFIRMATION`: Must match pattern `HX[a-f0-9]{32}`

## Testing Strategy

- **Unit tests**: Mock external APIs (Groq, Twilio, Calendar)
- **Integration tests**: Real API calls (requires keys)
- **E2E tests**: Full webhook flow
- **Fixtures**: Use pytest fixtures for synthetic data
- **Async tests**: Use `@pytest.mark.asyncio` decorator
- **Target**: 80%+ coverage

## 🚀 Deployment Strategy

### Local Development

```bash
docker-compose up  # PostgreSQL + Redis + API
```

### Production (Railway)

- PostgreSQL managed
- Redis managed
- API container
- Environment variables via Railway dashboard
- Automatic deploy on push to main

## ✅ Criterios de Éxito

- ✅ Recibe mensaje WhatsApp → responde en <3s
- ✅ NLP accuracy >90% (CONFIRM/CANCEL)
- ✅ Fallback automático si Groq falla
- ✅ Google Calendar sync funciona
- ✅ Reminders diarios se envían
- ✅ Dashboard muestra métricas en tiempo real
- ✅ Tests >80% coverage

## Common Gotchas

- **Database URL**: Railway/Production URLs need `?ssl=require` but keep `+asyncpg`
- **Async/Await**: ALL database and I/O operations must use `await`
- **Sessions**: Use `async with get_session() as session:` pattern
- **Imports**: Use absolute imports: `from src.core.config import settings`
- **Spanish messages**: All user-facing messages in Spanish (templates in `src/whatsapp/templates.py`)

## API Endpoints

### Core

- `GET /`: Root info
- `GET /health`: Health check (used by Railway)
- `GET /docs`: Swagger UI (dev only)

### WhatsApp

- `POST /api/webhook/whatsapp`: Twilio webhook

### Monitoring

- `GET /dashboard`: Monitoring metrics

### Admin (Future)

- `POST /api/patients`: Create patient
- `POST /api/appointments`: Create appointment
- `GET /api/appointments`: List appointments
- `GET /api/stats`: Statistics

## Development Workflow

1. **New feature**: Create module in `src/{feature}/`
2. **Database changes**: Update models → create Alembic migration
3. **Add endpoint**: Create route → add to `src/api/main.py`
4. **Test**: Write unit tests → run pytest
5. **Code quality**: Run black + ruff + mypy before commit
6. **Deploy**: Push to main → Railway auto-deploy

## Performance

- Async I/O throughout
- Connection pooling (10 base + 5 overflow)
- Connection pre-ping (Railway safety)
- Redis for caching/state
- Groq timeout: 5s with fallback

## Security

- Environment variables for secrets
- No hardcoded credentials
- Database credentials not in code
- Twilio webhook signature verification (future)
- HTTPS only in production
