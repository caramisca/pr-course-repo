FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY leader.py .
COPY follower.py .

# Expose port
EXPOSE 5000

# Command will be specified in docker-compose.yml
