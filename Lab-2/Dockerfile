# Lab 2 - Multithreaded HTTP Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY client.py .
COPY test_concurrent.py .
COPY test_rate_limit.py .

# Create collection directory structure
RUN mkdir -p /app/collection

# Expose port
EXPOSE 8080

# Default command (can be overridden in docker-compose)
CMD ["python", "server.py", "/app/collection"]
