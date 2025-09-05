import os
import tweepy
import pandas as pd
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Twitter client
bearer_token = os.environ.get("X_BEARER")
if bearer_token:
    client = tweepy.Client(bearer_token=bearer_token)
else:
    client = None

@app.route('/')
def home():
    """Show Twitter data as JSON"""
    if not client:
        return jsonify({
            "error": "Twitter API not configured. X_BEARER environment variable missing.",
            "data": []
        })
    
    try:
        # Simple query for UFO tweets
        query = '#ufo OR #alien lang:en -is:retweet'
        resp = client.get_recent_tweets_count(query=query, granularity="day")
        
        # Convert to simple list
        data = [{"date": c["start"], "count": c["tweet_count"]} for c in resp.data]
        
        return jsonify({
            "query": query,
            "data": data,
            "total_days": len(data)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch data: {str(e)}",
            "data": []
        })

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)