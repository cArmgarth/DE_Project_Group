# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN pip install uv
RUN uv pip install --no-cache-dir --system -r pyproject.toml

# Copy the rest of the application code
COPY main.py .

# Set environment variables for the pipeline
# These should be configured in the deployment environment
ENV GCP_PROJECT_ID=""
ENV BQ_DATASET_ID="raw_data"
ENV BQ_TABLE_ID="nasa_data"
ENV NASA_API=""

# Command to run the application
CMD ["python", "main.py"]
