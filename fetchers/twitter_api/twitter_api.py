
import os
import tweepy
import pandas as pd
from datetime import datetime
from flask import Flask, render_template_string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Twitter client
client = tweepy.Client(bearer_token=os.environ["X_BEARER"])

def get_twitter_data():
    """Fetch Twitter data and return as DataFrame"""
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
    """Home page showing Twitter data"""
    df, filename = get_twitter_data()
    
    if df.empty:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Twitter UFO Data</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>Twitter UFO Data</h1>
            <p class="error">Error fetching data. Please check your Twitter API credentials.</p>
        </body>
        </html>
        """)
    
    # Convert DataFrame to HTML table
    table_html = df.to_html(classes='table table-striped', table_id='twitter-data', escape=False)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Twitter UFO Data</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .table { border-collapse: collapse; width: 100%; }
            .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .table th { background-color: #f2f2f2; }
            .table tr:nth-child(even) { background-color: #f9f9f9; }
            h1 { color: #333; }
            .info { background-color: #e7f3ff; padding: 10px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Twitter UFO Data</h1>
        <div class="info">
            <p><strong>Query:</strong> #ufo OR #alien OR #uap OR #ufosightings OR "ufo sighting" OR "alien sighting" OR "uap sighting"</p>
            <p><strong>Language:</strong> English only</p>
            <p><strong>Excludes:</strong> Retweets</p>
            <p><strong>Data saved to:</strong> {{ filename }}</p>
        </div>
        {{ table|safe }}
    </body>
    </html>
    """, table=table_html, filename=filename)

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
    app.run(host='0.0.0.0', port=port, debug=True)