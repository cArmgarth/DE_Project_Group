# Twitter API Fetcher

A Flask-based microservice that fetches UFO-related tweet counts from Twitter's API and uploads the data to Google Cloud Storage.

## Overview

This service monitors Twitter for tweets containing UFO-related hashtags, counts daily occurrences, and stores the aggregated data in Google Cloud Storage in NDJSON format.

## Features

- Fetches tweet counts from Twitter API using Tweepy
- Searches for UFO-related hashtags (#ufo, #alien) in English tweets
- Excludes retweets to get original content only
- Aggregates tweet counts by date
- Uploads data to Google Cloud Storage bucket (`twitter_api_bucket/raw/`)
- Provides health check endpoint
- Handles authentication for both local and GCP environments
- Structured logging for monitoring

## API Endpoints

- `GET /` - Fetches Twitter UFO data and uploads to GCS
- `GET /health` - Health check endpoint

## Environment Variables

- `X_BEARER` - Twitter API Bearer Token (required)
- `PORT` - Port to run the service on (default: 8080)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account key (for local development)

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   export X_BEARER="your_twitter_bearer_token"
   ```

3. For local development, place your GCP service account key as `keys/key.json`

## Usage

Run the service:
```bash
uv run python twitter_api.py
```

The service will:
1. Query Twitter for tweets containing #ufo or #alien hashtags (English only, excluding retweets)
2. Get the most recent complete day's tweet count data
3. Upload the data to GCS bucket `twitter_api_bucket/raw/` with filename format `twitter_raw_data_YYYYMMDD.json`
4. Return the data and upload status as JSON

## Data Format

Data is stored in NDJSON format with each line containing a JSON object with the following structure:
- `date` - Date of the tweets (YYYY-MM-DD) in Stockholm timezone
- `count` - Number of tweets for that date
- `extraction_date` - Date when data was extracted
- `query` - Search query used

## Search Query

The service searches for tweets matching:
- `#ufo OR #alien lang:en -is:retweet`
- English language only
- Excludes retweets
- Uses hashtags for UFO-related content

## Dependencies

- Flask - Web framework
- tweepy - Twitter API client
- google-cloud-storage - GCS client
- python-dotenv - Environment variable loading

## Twitter API Setup

To use this service, you need a Twitter API Bearer Token:
1. Go to https://developer.twitter.com/
2. Create a new project/app
3. Generate a Bearer Token
4. Set the `X_BEARER` environment variable with your token

## Timezone Handling

The service converts Twitter API timestamps to Stockholm timezone (UTC+1/UTC+2) for consistent date formatting across all fetchers in the project.
