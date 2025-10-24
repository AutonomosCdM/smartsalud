# Dockerfile for smartSalud V2 Backend API
FROM python:3.13-slim

WORKDIR /app

# Set PYTHONPATH so Python can find the src module
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set PORT env var)
EXPOSE 8080

# Run migrations and start server
# Railway provides $PORT environment variable
CMD alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}
