# Model Inference Script

This script loads trained models from a Google Cloud Storage (GCS) bucket, creates predictions on data from a BigQuery table, and uploads the results to another GCS bucket.

## Features

- Loads `.pkl` model files from GCS bucket
- Automatically detects Reddit and Twitter count models
- Loads data from BigQuery for inference
- Generates predictions using the loaded models
- Uploads results with predictions to GCS as CSV files
- Comprehensive logging and error handling

## Environment Variables

Create a `.env` file in the inference directory with the following variables:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=team-tinfoil
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# GCS Bucket Configuration
GCS_MODEL_BUCKET=your-models-bucket
GCS_OUTPUT_BUCKET=your-predictions-bucket

# BigQuery Configuration
BIGQUERY_TABLE=team-tinfoil.training_data.training_combined

# Inference Configuration
INFERENCE_LIMIT=100
```

### Environment Variable Descriptions

- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account JSON key file
- `GCS_MODEL_BUCKET`: GCS bucket containing your trained `.pkl` model files
- `GCS_OUTPUT_BUCKET`: GCS bucket where predictions will be uploaded
- `BIGQUERY_TABLE`: Full BigQuery table ID (project.dataset.table)
- `INFERENCE_LIMIT`: Maximum number of rows to process for inference (optional)

## Usage

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your environment variables in a `.env` file

3. Run the inference script:
   ```bash
   python main.py
   ```

## Model Requirements

The script expects model files in the GCS bucket with names containing:
- `reddit_count` for Reddit count prediction model
- `twitter_count` for Twitter count prediction model

Example model filenames:
- `model_reddit_count_20250930_094042.pkl`
- `model_twitter_count_20250930_094042.pkl`

## Output

The script generates CSV files with:
- All original data from BigQuery
- Additional columns with predictions:
  - `reddit_count_prediction`
  - `twitter_count_prediction`

Files are named with timestamps: `model_predictions_YYYYMMDD_HHMMSS.csv`

## Error Handling

The script includes comprehensive error handling for:
- Missing GCS buckets or model files
- BigQuery connection issues
- Authentication problems
- Model loading failures
- Data processing errors

Check the logs for detailed error messages and troubleshooting information.
