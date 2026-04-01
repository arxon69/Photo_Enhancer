# PhotoEnhancer - Django Application
# ===================================

FROM python:3.12-slim-bookworm AS builder

# Build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# PRODUCTION IMAGE
# =============================================================================

FROM python:3.12-slim-bookworm AS production

# Security: Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

# Copy application code
COPY --chown=django:django . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--access-logfile", "-", "--error-logfile", "-", "photo_enhancer.wsgi:application"]

# =============================================================================
# DEVELOPMENT IMAGE
# =============================================================================

FROM production AS development

# Switch back to root for development
USER root

# Install development tools
RUN pip install --no-cache-dir \
    django-debug-toolbar \
    pytest \
    pytest-django \
    black \
    flake8 \
    isort

USER django

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
