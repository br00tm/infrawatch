# Workers Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Suppress debconf warnings
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r celery && useradd -r -g celery celery

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R celery:celery /app

# Switch to non-root user
USER celery

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD celery -A celery_app inspect ping || exit 1

# Default command (can be overridden)
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
