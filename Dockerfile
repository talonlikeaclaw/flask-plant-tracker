# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  libc6-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/app/static/uploads/plants
RUN mkdir -p /app/instance

# Initialize the database
RUN python -c "from app import create_app, db; \
  app = create_app(); \
  app.app_context().push(); \
  db.create_all()"

# Set appropriate permissions
RUN adduser --disabled-password --gecos "" appuser && \
  chown -R appuser:appuser /app
USER appuser

# Set a secure secret key
ENV SECRET_KEY="replace_this_with_a_proper_secret_key_in_production"

# Expose port
EXPOSE 5000

# Command to run the application with increased timeout
CMD ["gunicorn", "--workers=2", "--timeout=120", "--bind", "0.0.0.0:5000", "run:app"]
