# ElasticNet Regression Model

A machine learning model that uses ElasticNet regression to predict UFO activity counts (Reddit and Twitter) based on NASA Near Earth Object data.

## Overview

This component implements an ElasticNet regression model with hyperparameter tuning to predict social media UFO activity. It uses a MultiOutputRegressor to simultaneously predict both Reddit and Twitter counts based on asteroid and comet data from NASA.

## Features

- **ElasticNet Regression**: Combines L1 (Lasso) and L2 (Ridge) regularization
- **Multi-Output Prediction**: Simultaneously predicts Reddit and Twitter counts
- **Hyperparameter Tuning**: Grid search with cross-validation for optimal parameters
- **Feature Scaling**: StandardScaler preprocessing for numerical stability
- **Model Persistence**: Saves trained model using joblib
- **Comprehensive Evaluation**: MSE scoring and test set validation

## Algorithm Details

### Model Type
- **ElasticNet Regression** from scikit-learn
- **MultiOutputRegressor**: Handles multiple target variables
- **Pipeline**: Combines preprocessing and modeling steps

### Target Variables
- `reddit_count` - Number of UFO-related Reddit posts
- `twitter_count` - Number of UFO-related Twitter posts

### Features
- NASA Near Earth Object data including:
  - Velocity metrics (avg, max, min relative velocity)
  - Distance metrics (avg, max, min miss distance)
  - Diameter estimates (avg, max, min estimated diameter)
  - Magnitude data (avg, max, min absolute magnitude)
  - Object counts (total asteroids, hazardous asteroids, sentry objects)

### Hyperparameter Tuning
The model optimizes:
- `alpha`: Regularization strength [0.001, 0.01, 0.1, 1, 10]
- `l1_ratio`: Mix of L1/L2 regularization [0.2, 0.5, 0.8]
- `fit_intercept`: Whether to fit intercept [True, False]

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Ensure data file is available:
   ```bash
   # The model expects data/local_copy.csv
   # This should contain NASA NEO data with social media counts
   ```

## Usage

### Training the Model
Run the training script:
```bash
uv run python model.py
```

This will:
1. Load data from `data/local_copy.csv`
2. Split data into train/test sets (80/20)
3. Perform grid search with 3-fold cross-validation
4. Train the best model on full training set
5. Evaluate on test set
6. Save the trained model as `model.joblib`

### Model Output
The script outputs:
- Best hyperparameters found
- Best cross-validation score (negative MSE)
- Test set MSE
- Saves trained model to `model.joblib`

## Data Format

### Input Data
The model expects a CSV file with columns:
- `date`: Date of observation
- `reddit_count`: Target variable - Reddit post count
- `twitter_count`: Target variable - Twitter post count
- NASA NEO features (velocity, distance, diameter, magnitude, counts)

### Data Preprocessing
- **Feature Selection**: Drops `date`, `reddit_count`, `twitter_count` from features
- **Target Variables**: Uses `reddit_count` and `twitter_count` as targets
- **Scaling**: StandardScaler applied to all features
- **Train/Test Split**: 80/20 split with random_state=4333

## Model Performance

### Evaluation Metrics
- **Cross-Validation**: 3-fold CV with negative MSE scoring
- **Test Set**: Mean Squared Error on held-out test data
- **Grid Search**: Exhaustive search over parameter combinations

### Hyperparameter Search
The model tests 30 different parameter combinations:
- 5 alpha values × 3 l1_ratio values × 2 intercept options = 30 combinations

## Dependencies

### Core ML Dependencies
- **scikit-learn** - ElasticNet, MultiOutputRegressor, GridSearchCV
- **pandas** - Data manipulation and CSV loading
- **joblib** - Model serialization and persistence

### Visualization Dependencies
- **matplotlib** - Plotting and visualization (if needed)

## Model Architecture

```python
Pipeline([
    ("scaler", StandardScaler()),
    ("model", MultiOutputRegressor(ElasticNet(max_iter=10000)))
])
```

### Key Components
1. **StandardScaler**: Normalizes features to zero mean, unit variance
2. **MultiOutputRegressor**: Wraps ElasticNet for multiple targets
3. **ElasticNet**: Linear regression with combined L1/L2 regularization
4. **GridSearchCV**: Finds optimal hyperparameters

## ElasticNet Details

### Regularization
- **L1 (Lasso)**: Promotes sparsity, feature selection
- **L2 (Ridge)**: Prevents overfitting, handles multicollinearity
- **Combined**: Balances both effects based on l1_ratio

### Advantages
- Handles correlated features well
- Automatic feature selection
- Robust to outliers
- Good for high-dimensional data

## Integration

This model integrates with:
- **Data Pipeline**: Uses NASA NEO data as input
- **Model Comparison**: Can be compared with Random Forest models
- **Prediction System**: Trained model can be used for inference

## File Structure

```
elasticnet_regression/
├── data/
│   └── local_copy.csv          # Training data
├── model.py                    # Training script
├── model.joblib               # Trained model (generated)
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

## Usage Example

```python
import joblib
import pandas as pd

# Load trained model
model = joblib.load("model.joblib")

# Load new data
new_data = pd.read_csv("new_data.csv")
X_new = new_data.drop(columns=["date", "reddit_count", "twitter_count"])

# Make predictions
predictions = model.predict(X_new)
print(f"Predicted Reddit count: {predictions[0][0]}")
print(f"Predicted Twitter count: {predictions[0][1]}")
```

## Troubleshooting

### Common Issues
1. **Data Format**: Ensure CSV has required columns
2. **Missing Values**: Check for NaN values in features
3. **Memory Issues**: Reduce data size if grid search fails
4. **Convergence**: Increase max_iter if model doesn't converge

### Performance Tips
- Use more CV folds for better parameter estimation
- Increase max_iter for better convergence
- Consider feature engineering for better performance
- Monitor training time vs. model performance trade-offs
