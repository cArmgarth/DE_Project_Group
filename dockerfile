# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv (Python package manager)
RUN pip install uv

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY main.py ./
COPY fetchers/ ./fetchers/

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Run the application
CMD ["uv", "run", "python", "main.py"]
