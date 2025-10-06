# Reddit API Fetcher

A Flask-based microservice that fetches UFO-related posts from Reddit's r/ufo subreddit and uploads keyword count data to Google Cloud Storage.

## Overview

This service monitors the r/ufo subreddit for posts containing UFO-related keywords, counts occurrences by date, and stores the aggregated data in Google Cloud Storage in NDJSON format.

## Features

- Fetches recent posts from r/ufo subreddit using PRAW (Python Reddit API Wrapper)
- Analyzes post titles for UFO-related keywords
- Aggregates keyword counts by date
- Uploads data to Google Cloud Storage bucket (`reddit_api_bucket/raw/`)
- Provides health check endpoint
- Handles authentication for both local and GCP environments
- Structured logging for monitoring

## API Endpoints

- `GET /` - Fetches Reddit UFO data and uploads to GCS
- `GET /health` - Health check endpoint

## Environment Variables

- `REDDIT_CLIENT_ID` - Reddit API client ID (required)
- `REDDIT_CLIENT_SECRET` - Reddit API client secret (required)
- `PORT` - Port to run the service on (default: 8080)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account key (for local development)

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   export REDDIT_CLIENT_ID="your_reddit_client_id"
   export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
   ```

3. For local development, place your GCP service account key as `keys/key.json`

## Usage

Run the service:
```bash
uv run python reddit_api.py
```

The service will:
1. Fetch the latest 100 posts from r/ufo subreddit
2. Count UFO-related keywords in post titles by date
3. Upload the aggregated data to GCS bucket `reddit_api_bucket/raw/` with filename format `reddit_raw_data_YYYYMMDD.json`
4. Return the data and upload status as JSON

## Data Format

Data is stored in NDJSON format with each line containing a JSON object with the following structure:
- `date` - Date of the posts (YYYY-MM-DD)
- `count` - Number of keyword occurrences for that date
- `extraction_date` - Date when data was extracted
- `query` - Array of keywords searched for

## Keywords

The service searches for the following keywords in post titles:
- "sighting"
- "ufo" 
- "alien"
- "encounter"

## Dependencies

- Flask - Web framework
- praw - Python Reddit API Wrapper
- google-cloud-storage - GCS client
- python-dotenv - Environment variable loading

## Reddit API Setup

To use this service, you need to create a Reddit app:
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Note down the client ID and secret for environment variables
