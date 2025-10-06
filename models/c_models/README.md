# C-Models

A comprehensive machine learning pipeline for predicting UFO activity based on social media data, featuring data loading, model training, and inference services.

## Overview

This component provides a complete ML workflow for predicting Reddit and Twitter UFO-related activity counts using Random Forest regression models. The pipeline includes data extraction from BigQuery, model training, and a Flask-based inference API for real-time predictions.

## Architecture

The c_models system consists of three main components:

### 1. Data Loader (`data_loader/`)
- **Purpose**: Loads training data from BigQuery
- **Features**: Flexible authentication, configurable queries, error handling
- **Dependencies**: Google Cloud BigQuery, pandas, python-dotenv

### 2. Model Training (`models/`)
- **Purpose**: Trains Random Forest regression models
- **Features**: Automated training pipeline, model persistence, timestamped saves
- **Dependencies**: scikit-learn, pandas, numpy, BigQuery integration

### 3. Inference Service (`inference/`)
- **Purpose**: Serves trained models via REST API
- **Features**: Model loading from GCS, real-time predictions, GCS upload
- **Dependencies**: Flask, Google Cloud Storage, scikit-learn

## Features

- **Automated Training**: End-to-end model training pipeline
- **Model Persistence**: Timestamped model saves with pickle serialization
- **Cloud Integration**: Seamless BigQuery and GCS integration
- **REST API**: Flask-based inference service with health checks
- **Flexible Authentication**: Multiple credential sources (env vars, service accounts)
- **Error Handling**: Comprehensive logging and error management
- **Scalable**: Designed for cloud deployment with Docker support

## Environment Variables

### Data Loader
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key
- `GOOGLE_CREDENTIALS_JSON` - JSON credentials as string

### Model Training
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key

### Inference Service
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key
- `GCS_MODEL_BUCKET` - GCS bucket containing trained models
- `GCS_OUTPUT_BUCKET` - GCS bucket for prediction outputs
- `BIGQUERY_TABLE` - BigQuery table for inference data
- `INFERENCE_LIMIT` - Number of rows to process (default: 100)

## Setup

1. Install dependencies for each component:
   ```bash
   # Data loader
   cd data_loader && uv sync
   
   # Model training
   cd models && uv sync
   
   # Inference service
   cd inference && uv sync
   ```

2. Set up environment variables:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your_project_id"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
   export GCS_MODEL_BUCKET="your_models_bucket"
   export GCS_OUTPUT_BUCKET="your_predictions_bucket"
   export BIGQUERY_TABLE="your_project.dataset.table"
   ```

## Usage

### 1. Data Loading
Load data from BigQuery:
```bash
cd data_loader
uv run python data_loader.py
```

### 2. Model Training
Train Random Forest models for Reddit and Twitter counts:
```bash
cd models
uv run python main.py
```

This will:
- Load training data from BigQuery
- Train separate models for `reddit_count` and `twitter_count`
- Save models with timestamps to `trained_models/` directory
- Upload models to GCS bucket

### 3. Model Inference
Start the inference service:
```bash
cd inference
uv run python main.py
```

#### API Endpoints

- `GET /` - Health check
- `GET /predict` - Make predictions (returns NDJSON)
- `GET /predict-and-upload` - Make predictions and upload to GCS

#### Example Usage
```bash
# Health check
curl http://localhost:8080/

# Get predictions
curl http://localhost:8080/predict

# Get predictions and upload to GCS
curl http://localhost:8080/predict-and-upload
```

## Model Details

### Algorithm
- **Random Forest Regressor** from scikit-learn
- **Target Variables**: `reddit_count`, `twitter_count`
- **Features**: All columns except target variables and date
- **Preprocessing**: Automatic feature selection, train/test split (80/20)

### Model Persistence
- Models saved as pickle files with timestamps
- Format: `model_{target_name}_{YYYYMMDD_HHMMSS}.pkl`
- Stored in `trained_models/` directory and GCS bucket

### Prediction Output
```json
{
  "date": "2024-01-15",
  "reddit_count": 42,
  "twitter_count": 18
}
```

## Data Flow

1. **Training Phase**:
   - Load data from BigQuery → Train models → Save to local/GCS

2. **Inference Phase**:
   - Load models from GCS → Load features from BigQuery → Make predictions → Return/Upload results

## Dependencies

### Core Dependencies
- **scikit-learn** - Machine learning algorithms
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **Flask** - Web framework for inference API

### Cloud Dependencies
- **google-cloud-bigquery** - BigQuery integration
- **google-cloud-storage** - GCS integration
- **google-auth** - Authentication
- **db-dtypes** - BigQuery data types

### Development Dependencies
- **python-dotenv** - Environment variable loading
- **ruff** - Code formatting and linting

## Deployment

The inference service includes Docker support:
- `Dockerfile` for containerization
- `cloudbuild.yaml` for Google Cloud Build
- Environment-based configuration
- Health check endpoints for monitoring

## Monitoring

- Comprehensive logging throughout the pipeline
- Health check endpoints for service monitoring
- Error handling with detailed error messages
- Timestamped model saves for version tracking
