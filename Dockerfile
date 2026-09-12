# Use an official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition and install
COPY pyproject.toml poetry.lock* requirements.txt* /app/

# Fallback install if using requirements.txt or pip directly
RUN pip install --no-cache-dir uvicorn fastapi sqlalchemy alembic psycopg2-binary passlib[bcrypt] python-jose[cryptography] pydantic httpx pytest pytest-asyncio

# Copy application code
COPY . /app/

# Expose Uvicorn port
EXPOSE 8000

# Start Uvicorn server
CMD ["python", "-m", "uvicorn", "apps.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]