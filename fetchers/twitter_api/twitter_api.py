
import os
import tweepy
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Twitter client
bearer_token = os.environ.get("X_BEARER")
if not bearer_token:
    print("Warning: X_BEARER environment variable not set. Twitter API will not work.")
    client = None
else:
    client = tweepy.Client(bearer_token=bearer_token)

def get_twitter_data():
    """Fetch Twitter data and return as DataFrame"""
    if not client:
        print("Twitter client not initialized. Check X_BEARER environment variable.")
        return pd.DataFrame(), None
    
    query = '(#ufo OR #alien OR #uap OR #ufosightings OR "ufo sighting" OR "alien sighting" OR "uap sighting") lang:en -is:retweet'
    
    try:
        # Get tweet counts only
        resp = client.get_recent_tweets_count(
            query=query,
            granularity="day"   
        )
        
        # Prepare data for DataFrame
        data = [{"start": c["start"], "count": c["tweet_count"]} for c in resp.data]
        df = pd.DataFrame(data)
        
        # Create hist_data folder if it doesn't exist
        os.makedirs("hist_data", exist_ok=True)
        
        # Generate timestamped filename and save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hist_data/tweet_counts_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        return df, filename
    except Exception as e:
        print(f"Error fetching Twitter data: {e}")
        return pd.DataFrame(), None

@app.route('/')
def home():
    """Home page showing Twitter data as JSON"""
    df, filename = get_twitter_data()
    
    if df.empty:
        return jsonify({
            "status": "error",
            "message": "Error fetching data. Please check your Twitter API credentials.",
            "data": [],
            "query": "(#ufo OR #alien OR #uap OR #ufosightings OR \"ufo sighting\" OR \"alien sighting\" OR \"uap sighting\") lang:en -is:retweet"
        })
    
    # Convert DataFrame to JSON
    data = df.to_dict('records')
    
    return jsonify({
        "status": "success",
        "message": "Twitter UFO data retrieved successfully",
        "data": data,
        "count": len(data),
        "query": "(#ufo OR #alien OR #uap OR #ufosightings OR \"ufo sighting\" OR \"alien sighting\" OR \"uap sighting\") lang:en -is:retweet",
        "language": "English only",
        "excludes": "Retweets",
        "filename": filename
    })

@app.route('/api/data')
def api_data():
    """API endpoint returning raw data as JSON"""
    df, _ = get_twitter_data()
    return df.to_json(orient='records')

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return {"status": "ok", "message": "Twitter API Flask app is running!"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)