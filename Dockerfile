# Dockerfile for smartSalud V2 Backend API
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run migrations and start server
CMD alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port 8001
