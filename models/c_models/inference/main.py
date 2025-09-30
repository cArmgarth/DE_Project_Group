import json
import logging
import os
import pickle
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, Response, jsonify
from google.cloud import bigquery, storage
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_models_from_gcs():
    """Load models from GCS bucket."""

    bucket_name = os.getenv('GCS_MODEL_BUCKET')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    # Setup credentials
    credentials = None
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )
    
    # Initialize storage client
    storage_client = storage.Client(project=project_id, credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    
    models = {}
    
    # List and load all .pkl files from the c_models folder
    blobs = bucket.list_blobs(prefix="c_models/")

    for blob in blobs:
        if blob.name.endswith('.pkl'):
            logger.info(f"Loading model: {blob.name}")
            
            # Download and load model
            model_data = blob.download_as_bytes()
            model = pickle.loads(model_data)
            
            # Identify model type by filename
            if 'reddit' in blob.name.lower():
                models['reddit'] = model
                logger.info(f"✓ Loaded Reddit model from {blob.name}")
            elif 'twitter' in blob.name.lower():
                models['twitter'] = model
                logger.info(f"✓ Loaded Twitter model from {blob.name}")
    
    logger.info(f"Loaded {len(models)} models: {list(models.keys())}")
    return models

def load_data_from_bigquery():
    """Load data from BigQuery."""

    table_id = os.getenv('BIGQUERY_TABLE')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    limit = int(os.getenv('INFERENCE_LIMIT', '100'))
    
    # Setup credentials
    credentials = None
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )
    
    # Initialize BigQuery client
    bigquery_client = bigquery.Client(project=project_id, credentials=credentials)
    
    # Query data
    query = f"SELECT * FROM `{table_id}` LIMIT {limit}"
    df = bigquery_client.query(query).to_dataframe()
    
    logger.info(f"Loaded {len(df)} rows from BigQuery")
    return df

def prepare_features(df):
    """Prepare features by excluding target columns."""
    exclude_cols = ['reddit_count', 'twitter_count', 'date']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    return df[feature_cols]

def upload_to_gcs(data, bucket_name, filename):
    """Upload data to GCS bucket as NDJSON."""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    # Setup credentials
    credentials = None
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )
    
    # Initialize storage client
    storage_client = storage.Client(project=project_id, credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    
    # Convert data to NDJSON string
    if isinstance(data, dict):
        ndjson_content = json.dumps(data)
    else:
        ndjson_content = data
    
    # Upload to GCS
    blob = bucket.blob(filename)
    blob.upload_from_string(ndjson_content, content_type='application/x-ndjson')
    
    gcs_path = f"gs://{bucket_name}/{filename}"
    logger.info(f"Uploaded predictions to {gcs_path}")
    return gcs_path

@app.route('/predict', methods=['GET'])
def predict():
    """Main prediction endpoint."""
    try:
        logger.info("Starting inference...")
        
        # Load models from GCS
        models = load_models_from_gcs()
        
        # Load data from BigQuery
        df = load_data_from_bigquery()
        
        # Prepare features
        features = prepare_features(df)
        
        # Make predictions
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Create single row with all predictions
        result = {
            'date': date_str,
            'reddit_count': None,
            'twitter_count': None
        }
        
        for model_name, model in models.items():
            pred = model.predict(features)
            # Convert to integers and ensure non-negative values
            pred_ints = [max(0, int(round(p))) for p in pred]
            
            # Take the first prediction value (assuming single row input)
            pred_value = pred_ints[0] if pred_ints else 0
            
            if model_name == 'reddit':
                result['reddit_count'] = pred_value
            elif model_name == 'twitter':
                result['twitter_count'] = pred_value
            
            logger.info(f"{model_name} prediction: {pred_value}")
        
        # Return single NDJSON line
        ndjson_line = json.dumps(result)
        return Response(ndjson_line, mimetype='application/x-ndjson')
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        error_line = json.dumps({'error': str(e)})
        return Response(error_line, mimetype='application/x-ndjson'), 500

@app.route('/predict-and-upload', methods=['GET'])
def predict_and_upload():
    """Make predictions and upload to GCS bucket."""
    try:
        logger.info("Starting inference and upload...")
        
        # Load models from GCS
        models = load_models_from_gcs()
        
        # Load data from BigQuery
        df = load_data_from_bigquery()
        
        # Prepare features
        features = prepare_features(df)
        
        # Make predictions
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Create single row with all predictions
        result = {
            'date': date_str,
            'reddit_count': None,
            'twitter_count': None
        }
        
        for model_name, model in models.items():
            pred = model.predict(features)
            # Convert to integers and ensure non-negative values
            pred_ints = [max(0, int(round(p))) for p in pred]
            
            # Take the first prediction value (assuming single row input)
            pred_value = pred_ints[0] if pred_ints else 0
            
            if model_name == 'reddit':
                result['reddit_count'] = pred_value
            elif model_name == 'twitter':
                result['twitter_count'] = pred_value
            
            logger.info(f"{model_name} prediction: {pred_value}")
        
        # Upload to GCS
        output_bucket = os.getenv('GCS_OUTPUT_BUCKET', 'your-predictions-bucket')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"c_models/predictions/predictions_{timestamp}.ndjson"
        
        gcs_path = upload_to_gcs(result, output_bucket, filename)
        
        return jsonify({
            'status': 'success',
            'message': 'Predictions uploaded to GCS',
            'gcs_path': gcs_path,
            'predictions': result
        })
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Inference API is running'})

if __name__ == '__main__':
    logger.info("Starting Flask inference app...")
    app.run(host='0.0.0.0', port=8080)