import json
import logging
import os
from datetime import datetime, timedelta, timezone

import tweepy
from dotenv import load_dotenv
from flask import Flask, jsonify
from google.cloud import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Stockholm timezone (UTC+1 in winter, UTC+2 in summer)
stockholm_tz = timezone(timedelta(hours=1))

# Initialize Twitter client
bearer_token = os.environ.get("X_BEARER")
client = tweepy.Client(bearer_token=bearer_token) if bearer_token else None

@app.route('/')
def home():
    """Show Twitter data as JSON"""
    if not client:
        return jsonify({
            "error": "Twitter API not configured. X_BEARER environment variable missing.",
            "data": []
        })
    

    # Simple query for UFO tweets - get only today's data
    query = '#ufo OR #alien lang:en -is:retweet'
    
    # Get recent tweet counts (last 7 days)
    resp = client.get_recent_tweets_count(query=query, granularity="day")
    
    # Get the most recent complete day of data
    # This ensures we don't get partial data for "today"
    data = []
    if resp.data:
        # Get the most recent day (last in the list)
        most_recent = resp.data[-1]
        
        # Convert API date to Stockholm timezone and format as date only
        api_date = datetime.fromisoformat(most_recent["start"].replace('Z', '+00:00'))
        stockholm_date = api_date.astimezone(stockholm_tz)
        formatted_date = stockholm_date.strftime("%Y-%m-%d")
        
        data = [{"date": formatted_date, "count": most_recent["tweet_count"]}]
    
    # Get current Stockholm time
    stockholm_time = datetime.now(stockholm_tz)
    
    response_data = {
        "query": query,
        "data": data,
        "total_days": len(data),
        "extraction_date": stockholm_time.strftime("%Y-%m-%d")
    }
    
    # Upload to GCS with date-based filename (overwrites previous day's file)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"twitter_raw_data_{date_str}.json"
    upload_success = upload_to_gcs(response_data, filename)
    
    # Add upload status to response
    response_data["upload_status"] = "success" if upload_success else "failed"
    
    return jsonify(response_data)


@app.route('/health')
def health():
    return {"status": "ok"}


def upload_to_gcs(data, filename):
    """Upload data to Google Cloud Storage as JSON"""
    try:
        # Only set service account key if running locally (file exists)
        # On GCP, use default credentials
        if os.path.exists('keys/key.json'):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keys/key.json'
            logger.info("Using local service account key")
        else:
            logger.info("Using default GCP credentials")
        
        client = storage.Client()
        bucket = client.bucket('twitter_api_bucket')
        
        # Create blob with filename in /raw folder
        blob = bucket.blob(f"raw/{filename}")
        
        # Convert to NDJSON format with extraction_date and query
        ndjson_data = ""
        for item in data.get("data", []):
            # Add extraction_date and query to each record
            record = {
                **item,
                "extraction_date": data.get("extraction_date"),
                "query": data.get("query")
            }
            ndjson_data += json.dumps(record) + "\n"
        
        # Upload NDJSON data
        blob.upload_from_string(
            ndjson_data,
            content_type='application/x-ndjson'
        )
        
        logger.info(f"Successfully uploaded {filename} to GCS bucket: twitter_api_bucket/raw/")
        return True
    except Exception as e:
        logger.error(f"Error uploading to GCS: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)