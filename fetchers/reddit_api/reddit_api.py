import praw
import os
import pandas as pd
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Authenticate
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="ufo_activity_tracker"
)

subreddit = reddit.subreddit("ufo")

# Collect data from posts
posts_data = []
keywords = ["sighting", "ufo", "alien", "encounter"]

for post in subreddit.new(limit=100):
    # Convert timestamp to date
    post_date = datetime.fromtimestamp(post.created_utc).date()
    
    # Count keyword matches in title
    title_lower = post.title.lower()
    keyword_count = sum(1 for k in keywords if k in title_lower)
    
    posts_data.append({
        'date': post_date,
        'count': keyword_count
    })

# Create DataFrame
df = pd.DataFrame(posts_data)

# Group by date and sum the counts
daily_counts = df.groupby('date')['count'].sum().reset_index()
daily_counts = daily_counts.sort_values('date')

print("Daily UFO-related post counts on Reddit:")
print(daily_counts)

