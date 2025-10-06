# NASA API Fetcher

A Flask-based microservice that fetches Near Earth Object (NEO) data from NASA's API and uploads it to Google Cloud Storage.

## Overview

This service collects asteroid and comet data from NASA's Near Earth Object Web Service API for the previous day and stores it in Google Cloud Storage in NDJSON format.

## Features

- Fetches NEO data from NASA API for the previous day
- Uploads data to Google Cloud Storage bucket (`nasa_api_bucket/raw/`)
- Provides health check endpoint
- Handles authentication for both local and GCP environments
- Structured logging for monitoring

## API Endpoints

- `GET /` - Fetches NASA NEO data and uploads to GCS
- `GET /health` - Health check endpoint

## Environment Variables

- `NASA_API` - NASA API key (required)
- `PORT` - Port to run the service on (default: 8080)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account key (for local development)

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   export NASA_API="your_nasa_api_key"
   ```

3. For local development, place your GCP service account key as `credentials.json`

## Usage

Run the service:
```bash
uv run python nasa_api.py
```

The service will:
1. Fetch NEO data for yesterday from NASA API
2. Upload the data to GCS bucket `nasa_api_bucket/raw/` with filename format `nasa_raw_dataYYYYMMDD.json`
3. Return the data and upload status as JSON

## Data Format

Data is stored in NDJSON format with each line containing a JSON object representing a Near Earth Object with the following structure:
- Object properties from NASA API
- Additional `date` field added for tracking

## Dependencies

- Flask - Web framework
- requests - HTTP client
- google-cloud-storage - GCS client
- python-dotenv - Environment variable loading
