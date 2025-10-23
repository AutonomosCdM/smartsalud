# smartSalud_V2 Architecture

## Design Principles

1. **Clean Architecture**: Modular separation of concerns
2. **No Legacy Code**: Built from scratch, zero migration from v1
3. **Simple First**: Only essential features, no over-engineering
4. **Async-First**: All I/O is async for scalability
5. **Test-Driven**: 80%+ coverage target

## System Components

### 1. WhatsApp Module (`src/whatsapp/`)

**Responsibility**: Receive and send WhatsApp messages

**Files**:
- `routes.py`: FastAPI webhook endpoint (POST /api/webhook/whatsapp)
- `handlers.py`: Intent-specific logic (CONFIRM, CANCEL)
- `service.py`: Twilio API wrapper
- `templates.py`: Spanish message templates

**Flow**:
```
Twilio → POST /api/webhook/whatsapp
    → NLP detect intent
    → Route to handler
    → Update DB + Calendar
    → Respond via TwiML
```

### 2. NLP Module (`src/nlp/`)

**Responsibility**: Intent detection with fallback

**Files**:
- `service.py`: Groq API + circuit breaker
- `intents.py`: Intent enum (CONFIRM, CANCEL, UNKNOWN)
- `patterns.py`: Regex patterns for fallback

**Strategy**:
- Primary: Groq API (llama-3.3-70b) - 0.8-0.95 confidence
- Fallback: Regex patterns - 0.7 confidence
- Circuit breaker: Auto-recovery with exponential backoff

### 3. Database Module (`src/database/`)

**Responsibility**: Data persistence

**Files**:
- `models.py`: SQLAlchemy models (Patient, Appointment, Interaction)
- `repository.py`: CRUD operations
- `connection.py`: Async engine + session factory

**Schema**:
```
Patient (1) → (N) Appointment
Patient (1) → (N) Interaction
Appointment (1) → (N) Interaction
```

**NO calcom_uid** - completely clean schema

### 4. Calendar Module (`src/calendar/`)

**Responsibility**: Google Calendar sync

**Files**:
- `service.py`: Calendar CRUD operations
- `colors.py`: Status → color mappings

**Color Coding**:
- Yellow (#FBD75B): PENDING
- Green (#7AE7BF): CONFIRMED
- Red (#F06292): CANCELLED

### 5. Scheduler Module (`src/scheduler/`)

**Responsibility**: Automated tasks

**Files**:
- `tasks.py`: APScheduler setup
- `reminders.py`: Daily reminder logic

**Schedule**:
- Daily at 9:00 AM: Find appointments for tomorrow → send reminders

### 6. Monitoring Module (`src/monitoring/`)

**Responsibility**: Health metrics

**Files**:
- `dashboard.py`: GET /dashboard endpoint

**Metrics**:
- Total messages today
- Confirmation rate
- Groq vs Regex usage
- Error rate

### 7. Core Module (`src/core/`)

**Responsibility**: Shared utilities

**Files**:
- `config.py`: Pydantic Settings (env vars)
- `exceptions.py`: Custom exceptions with context

## Data Flow

### Confirmation Flow
```
1. Patient sends "Confirmo" via WhatsApp
    ↓
2. Twilio → POST /api/webhook/whatsapp
    ↓
3. NLP detects Intent.CONFIRM (0.9 confidence)
    ↓
4. CONFIRM handler:
   - Get patient by phone
   - Get pending appointment
   - Update status → CONFIRMED
   - Update calendar color → green
   - Log interaction
    ↓
5. Respond: "✅ Tu cita ha sido CONFIRMADA..."
```

### Cancellation Flow
```
1. Patient sends "Cancelo" via WhatsApp
    ↓
2. Twilio → POST /api/webhook/whatsapp
    ↓
3. NLP detects Intent.CANCEL (0.85 confidence)
    ↓
4. CANCEL handler:
   - Get patient by phone
   - Get pending appointment
   - Update status → CANCELLED
   - Update calendar color → red
   - Log interaction
    ↓
5. Respond: "❌ Tu cita ha sido CANCELADA..."
```

### Daily Reminder Flow
```
1. APScheduler triggers at 9:00 AM
    ↓
2. Query appointments for tomorrow with status=PENDING
    ↓
3. For each appointment:
   - Format reminder message
   - Send via WhatsApp service
   - Log interaction
    ↓
4. Log summary: X reminders sent
```

## Database Schema

```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    appointment_date TIMESTAMP NOT NULL,
    doctor_name VARCHAR(200) NOT NULL,
    specialty VARCHAR(100),
    status VARCHAR(20) NOT NULL,  -- PENDING/CONFIRMED/CANCELLED/COMPLETED/NO_SHOW
    calendar_event_id VARCHAR(255) UNIQUE,  -- Google Calendar ID
    notes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_appointments_date_status ON appointments(appointment_date, status);

CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    message_from VARCHAR(20) NOT NULL,
    message_to VARCHAR(20) NOT NULL,
    message_body TEXT NOT NULL,
    detected_intent VARCHAR(50),
    confidence_score INTEGER,
    twilio_message_sid VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_interactions_created_at ON interactions(created_at DESC);
```

## API Endpoints

### Core
- `GET /` - Root info
- `GET /health` - Health check
- `GET /dashboard` - Monitoring metrics

### WhatsApp
- `POST /api/webhook/whatsapp` - Twilio webhook

### Admin (Future)
- `POST /api/patients` - Create patient
- `POST /api/appointments` - Create appointment
- `GET /api/appointments` - List appointments
- `GET /api/stats` - Statistics

## Security

- Environment variables for secrets
- No hardcoded credentials
- Database credentials not in code
- Twilio webhook signature verification (future)
- HTTPS only in production

## Performance

- Async I/O throughout
- Connection pooling (10 base + 5 overflow)
- Connection pre-ping (Railway safety)
- Redis for caching/state
- Groq timeout: 5s with fallback

## Error Handling

- Custom exceptions with context
- Structured logging (JSON in prod)
- Graceful degradation (regex fallback)
- Never expose internal errors to users

## Testing Strategy

- Unit tests: Individual functions
- Integration tests: Real APIs (Groq, Twilio, Calendar)
- E2E tests: Full webhook flow
- Fixtures: Synthetic data

## Deployment

- Local: Docker Compose
- Production: Railway
- Database: PostgreSQL managed
- Redis: Redis managed
- Logs: Structured JSON
- Monitoring: Dashboard + Railway metrics

## Future Enhancements

- Multi-language support (English)
- Voice messages support
- Image/attachment support
- Patient portal
- Doctor dashboard
- Analytics/reporting
- A/B testing NLP models
