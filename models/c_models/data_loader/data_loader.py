import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def load_data_from_bigquery(table_id: str, project_id: str = None, limit: int = None, credentials_path: str = None):
    """
    Load data from BigQuery table for model training.
    
    Args:
        table_id: Full table ID (project.dataset.table) or just table name
        project_id: Google Cloud project ID (optional, uses env var if not provided)
        limit: Maximum number of rows to return (optional)
        credentials_path: Path to service account JSON file (optional)
    
    Returns:
        pandas.DataFrame: The loaded data
    """
    # Get project ID
    if not project_id:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            raise ValueError("Project ID must be provided or set in GOOGLE_CLOUD_PROJECT environment variable")
    
    # Initialize credentials
    credentials = None
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
    elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        credentials = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    elif os.getenv('GOOGLE_CREDENTIALS_JSON'):
        import json
        credentials_json = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
        credentials = service_account.Credentials.from_service_account_info(credentials_json)
    
    # Initialize BigQuery client
    if credentials:
        client = bigquery.Client(project=project_id, credentials=credentials)
    else:
        client = bigquery.Client(project=project_id)
    
    # Build query
    query = f"SELECT * FROM `{table_id}`"
    if limit:
        query += f" LIMIT {limit}"
    
    # Execute query and return DataFrame
    return client.query(query).to_dataframe()


if __name__ == "__main__":
    # Example usage
    table_id = "team-tinfoil.training_data.training_combined"
    df = load_data_from_bigquery(table_id, limit=1000)
    print(f"Loaded {len(df)} rows")
    print(df)
