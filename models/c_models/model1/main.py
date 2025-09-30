import logging
import os
import pickle
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_loader'))

from data_loader import load_data_from_bigquery
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load data from data_loader
df = load_data_from_bigquery("team-tinfoil.training_data.training_combined", limit=1000)

logger.info(f"Loaded {len(df)} rows")

# Prepare features and targets
exclude_cols = ['reddit_count', 'twitter_count', 'date']
feature_cols = [col for col in df.columns if col not in exclude_cols]
X = df[feature_cols]
y = df[['reddit_count', 'twitter_count']]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train models
models = {}
for target in ['reddit_count', 'twitter_count']:
    logger.info(f"Training model for {target}...")
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train[target])
    models[target] = model

# Create trained_models directory if it doesn't exist
os.makedirs('trained_models', exist_ok=True)

# Generate filename with today's date and time
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
model_filename = f'trained_models/model_{timestamp}.pkl'

# Save models
model_data = {
    'models': models,
    'feature_cols': feature_cols,
    'target_cols': ['reddit_count', 'twitter_count']
}

with open(model_filename, 'wb') as f:
    pickle.dump(model_data, f)

logger.info(f"Models saved to '{model_filename}'")
logger.info("Model data includes:")
logger.info(f"  - {len(models)} trained models")
logger.info(f"  - Feature columns: {feature_cols}")
logger.info(f"  - Target columns: {['reddit_count', 'twitter_count']}")

logger.debug(f"Trained models: {models}")

