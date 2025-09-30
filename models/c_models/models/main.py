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


def load_training_data(table_name: str, limit: int = 1000):
    """Load training data from BigQuery."""

    df = load_data_from_bigquery(table_name, limit=limit)
    logger.info(f"Loaded {len(df)} rows")
    return df


def prepare_features_and_target(df, target_col):
    """Prepare features and target variable for training."""

    exclude_cols = ['reddit_count', 'twitter_count', 'date']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    X = df[feature_cols]
    y = df[target_col]
    return X, y, feature_cols


def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into training and testing sets."""

    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def train_model(X_train, y_train, target_name, n_estimators=100, random_state=42):
    """Train a RandomForestRegressor model."""

    logger.info(f"Training model for {target_name}...")
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
    model.fit(X_train, y_train)
    return model


def save_model(model, target_name, model_dir='trained_models'):
    """Save the trained model to a pickle file."""
    # Create directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f'{model_dir}/model_{target_name}_{timestamp}.pkl'
    
    # Save model
    with open(model_filename, 'wb') as f:
        pickle.dump(model, f)
    
    logger.info(f"Model saved to '{model_filename}'")
    return model_filename


def train_single_model(df, target_col):
    """Train a single model for the specified target column."""
    # Prepare features and target
    X, y, feature_cols = prepare_features_and_target(df, target_col)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Train model
    model = train_model(X_train, y_train, target_col)
    
    # Save model
    model_filename = save_model(model, target_col)
    
    return model, model_filename


def main():
    """Main function to orchestrate the training process."""
    # Load data
    df = load_training_data("team-tinfoil.training_data.training_combined", limit=1000)
    
    # Train reddit_count model
    reddit_model, reddit_filename = train_single_model(df, 'reddit_count')
    logger.info(f"Reddit model trained and saved to '{reddit_filename}'")
    
    # Train twitter_count model
    twitter_model, twitter_filename = train_single_model(df, 'twitter_count')
    logger.info(f"Twitter model trained and saved to '{twitter_filename}'")
    
    logger.info("Both models trained successfully!")
    logger.debug(f"Reddit model: {reddit_model}")
    logger.debug(f"Twitter model: {twitter_model}")


if __name__ == "__main__":
    main()

