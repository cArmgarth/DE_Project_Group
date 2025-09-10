import logging
import os
from datetime import datetime

import praw
from dotenv import load_dotenv
from flask import Flask, jsonify

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
            "error": "Twitter API not configured. One or more of environment variables missing (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, user agent)",
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
    
    # End of TODO - everything between is subject to change, this is simply for testing
    
    return jsonify(posts_data)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)