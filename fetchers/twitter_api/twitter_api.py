import json
import os
from datetime import UTC, datetime

import tweepy
from dotenv import load_dotenv
from flask import Flask, jsonify
from google.cloud import storage

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

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
        most_recent = resp.data[-2]
        data = [{"date": most_recent["start"], "count": most_recent["tweet_count"]}]
    
    response_data = {
        "query": query,
        "data": data,
        "total_days": len(data),
        "extraction_date": datetime.now(UTC).isoformat().replace('+00:00', 'Z')
    }
    
    # Upload to GCS with date-based filename (overwrites previous day's file)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"twitter_ufo_data_{date_str}.json"
    upload_to_gcs(response_data, filename)
    
    return jsonify(response_data)

@app.route('/health')
def health():
    return {"status": "ok"}

def upload_to_gcs(data, filename):
    """Upload data to Google Cloud Storage as JSON"""
    try:
        # Set the service account key path
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keys/key.json'
        
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
        
        print(f"Successfully uploaded {filename} to GCS bucket: twitter_api_bucket/raw/")
        return True
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        return False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)