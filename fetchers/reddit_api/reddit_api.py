import json
import logging
import os
from datetime import datetime, timedelta, timezone

import praw
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

# Initialize reddit client
client_id = os.environ.get("REDDIT_CLIENT_ID")
client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
user_agent = "ufo_activity_tracker"
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
) if (client_id and client_secret) else None

@app.route("/")
def home():
    """Show reddit data as JSON"""
    if not reddit:
        return jsonify({
            "error": "Reddit API not configured. One or more of environment variables missing (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, user agent)",
            "data": []
        })
    
    # Keywords to look for
    keywords = ["sighting", "ufo", "alien", "encounter"]

    # Subreddit
    subreddit = reddit.subreddit("ufo")

    # Get recent data
    # TODO: get data for the last 24 hours rather than the last 100 posts
    resp = subreddit.new(limit=100)

    # Collect data from the posts
    posts_data = {}
    
    for post in resp:
        # Convert timestamp to date in the proper timezone and format as date only
        post_date = datetime.fromtimestamp(post.created_utc).date()
        post_date_as_str = str(post_date)

        # Count keywords in title
        title_lower = post.title.lower()
        keyword_count = sum(1 for k in keywords if k in title_lower)

        # Append data
        if post_date_as_str in posts_data:
           posts_data[post_date_as_str] += keyword_count
        else:
           posts_data[post_date_as_str] = keyword_count
    data = [{"date": date, "count": count} for date, count in posts_data.items()]
    # End of TODO - everything between is subject to change, this is simply for testing

    # Get current Stockholm time
    stockholm_time = datetime.now(stockholm_tz)
    extraction_date = stockholm_time.strftime("%Y-%m-%d")

    # Most recent day's data
    # TODO: yes
    # data = []

    # Prepare data for GCS bucket
    response_data = {
        "query":    keywords,                   # TODO: potentially add actual query here somehow?
        "data":     data,                       # TODO: fix time zone stuff and make the proper data object above
        "total_days":       len(posts_data),    # TODO: perhaps not necessary since we only want one day? Take look
        "extraction_date":  extraction_date
    }
    

    # Upload to GCS with date-based filename (overwrites previous day's file)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"reddit_raw_data_{date_str}.json"
    upload_success = upload_to_gcs(response_data, filename)
        
    # Add upload status to response
    response_data["upload_status"] = "success" if upload_success else "failed"
        
    return jsonify(response_data)


@app.route("/health")
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
        bucket = client.bucket("reddit_api_bucket")
        
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
        
        logger.info(f"Successfully uploaded {filename} to GCS bucket: reddit_api_bucket/raw/")
        return True
    except Exception as e:
        logger.error(f"Error uploading to GCS: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)