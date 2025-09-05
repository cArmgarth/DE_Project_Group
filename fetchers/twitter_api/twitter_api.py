
import os
import tweepy
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = tweepy.Client(bearer_token=os.environ["X_BEARER"])

query = '(#ufo OR #alien OR #uap OR #ufosightings OR "ufo sighting" OR "alien sighting" OR "uap sighting") lang:en -is:retweet'

# Get tweet counts only
resp = client.get_recent_tweets_count(
    query=query,
    granularity="day"   
)

# Create hist_data folder if it doesn't exist
os.makedirs("hist_data", exist_ok=True)

# Generate timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"hist_data/tweet_counts_{timestamp}.csv"

# Prepare data for CSV
data = [{"start": c["start"], "count": c["tweet_count"]} for c in resp.data]
df = pd.DataFrame(data)

# Save to CSV
df.to_csv(filename, index=False)

# Output raw data
for c in resp.data:
    print(f"{c['start']} - {c['tweet_count']}")

print(f"\nData saved to: {filename}")