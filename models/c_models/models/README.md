# Model Training

A machine learning training pipeline that creates Random Forest regression models to predict UFO activity counts from social media data.

## Overview

This component trains separate Random Forest regression models for predicting Reddit and Twitter UFO-related activity counts. It loads training data from BigQuery, prepares features, splits the data, trains models, and saves them with timestamps for version control.

## Features

- **Automated Training Pipeline**: End-to-end model training workflow
- **Dual Target Models**: Separate models for Reddit and Twitter counts
- **Feature Engineering**: Automatic feature selection excluding target variables
- **Data Splitting**: 80/20 train/test split with configurable random state
- **Model Persistence**: Timestamped pickle files for version tracking
- **Comprehensive Logging**: Detailed training progress and model information
- **BigQuery Integration**: Direct data loading from cloud storage

## Algorithm Details

### Model Type
- **Random Forest Regressor** from scikit-learn
- **Ensemble Method**: Combines multiple decision trees for robust predictions
- **Default Parameters**: 100 estimators, random state for reproducibility

### Target Variables
- `reddit_count` - Number of UFO-related Reddit posts
- `twitter_count` - Number of UFO-related Twitter posts

### Feature Engineering
- **Automatic Selection**: Uses all columns except target variables and date
- **Excluded Columns**: `reddit_count`, `twitter_count`, `date`
- **Dynamic Features**: Adapts to any additional columns in the dataset

## Environment Variables

- `GOOGLE_CLOUD_PROJECT` - GCP project ID (required)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key (optional)
- `GOOGLE_CREDENTIALS_JSON` - JSON credentials as string (optional)

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your_project_id"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
   ```

3. Ensure the data_loader module is accessible (it's imported from parent directory)

## Usage

### Basic Training
Train both Reddit and Twitter models:
```bash
uv run python main.py
```

This will:
1. Load training data from `team-tinfoil.training_data.training_combined`
2. Train a Random Forest model for `reddit_count`
3. Train a Random Forest model for `twitter_count`
4. Save both models with timestamps to `trained_models/` directory

### Custom Training
You can modify the training parameters in `main.py`:
- Change the BigQuery table name
- Adjust the data limit
- Modify model parameters (n_estimators, random_state)

## Model Output

### File Naming Convention
Models are saved with the format:
```
trained_models/model_{target_name}_{YYYYMMDD_HHMMSS}.pkl
```

Examples:
- `model_reddit_count_20241215_143022.pkl`
- `model_twitter_count_20241215_143025.pkl`

### Model Structure
Each saved model contains:
- Trained Random Forest Regressor
- Feature names and structure
- Training parameters
- Ready for inference via pickle.load()

## Training Process

1. **Data Loading**: Fetches data from BigQuery using the data_loader module
2. **Feature Preparation**: Separates features from target variables
3. **Data Splitting**: Creates 80/20 train/test split
4. **Model Training**: Fits Random Forest on training data
5. **Model Persistence**: Saves model with timestamp to local directory

## Dependencies

### Core ML Dependencies
- **scikit-learn** - Random Forest implementation and train/test split
- **pandas** - Data manipulation and DataFrame operations
- **numpy** - Numerical computing (scikit-learn dependency)

### Cloud Dependencies
- **google-cloud-bigquery** - Data source integration
- **db-dtypes** - BigQuery data type handling

### Development Dependencies
- **python-dotenv** - Environment variable loading
- **ruff** - Code formatting and linting

## Data Requirements

### Input Data Format
The training data should be a BigQuery table with:
- `reddit_count` column (target variable)
- `twitter_count` column (target variable)
- `date` column (excluded from features)
- Additional feature columns (automatically included)

### Data Quality
- No missing values in target columns
- Numeric features for model training
- Sufficient data volume for meaningful training (recommended: 100+ rows)

## Model Performance

### Evaluation
The current implementation focuses on training and saving models. For evaluation:
- Models are trained on 80% of data
- 20% is held out for testing (not currently used for evaluation)
- Consider adding evaluation metrics in future iterations

### Hyperparameter Tuning
Current default parameters:
- `n_estimators=100` - Number of trees in the forest
- `random_state=42` - For reproducible results
- `test_size=0.2` - 20% of data for testing

## Integration

This training component integrates with:
- **Data Loader**: Uses `data_loader.py` for BigQuery connectivity
- **Inference Service**: Trained models are loaded by the inference API
- **Model Storage**: Models can be uploaded to GCS for cloud deployment

## Troubleshooting

### Common Issues
1. **BigQuery Connection**: Ensure GCP credentials are properly configured
2. **Data Access**: Verify table permissions and project access
3. **Feature Columns**: Check that target columns exist in the dataset
4. **Memory Issues**: Reduce data limit if training fails on large datasets

### Logging
The training process provides detailed logging:
- Data loading progress
- Model training status
- File save confirmations
- Error messages with context
