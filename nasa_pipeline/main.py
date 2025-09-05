import requests
import os
from datetime import datetime, timedelta, date
from google.cloud import bigquery
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

TODAY = date.today().strftime("%Y-%m-%d")
YESTERDAY = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
NOW = datetime.now()
API_KEY = os.environ("NASA_API")


class DataPipeline:
    def __init__(self):
        """Initialize the data pipeline with BigQuery client and configuration"""
        self.client = bigquery.Client()
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        self.dataset_id = os.environ.get("BQ_DATASET_ID", "raw_data")
        self.table_id = os.environ.get("BQ_TABLE_ID", "nasa_data")

        logger.info("Pipeline initialized for NASA data collection.")

    def fetch_data(self):
        """Fetch data from NASA's API"""

        url = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {
            "start_date": YESTERDAY,
            "end_date": YESTERDAY,
            "api_key": API_KEY,
        }

        try:
            logger.info("Fetching data from NASA API...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            near_earth_objects = data.get("near_earth_objects", {}).get(YESTERDAY, [])

            for record in near_earth_objects:
                record["fetched_at"] = NOW.isoformat()

            logger.info(f"Successfully fetched {len(near_earth_objects)} record(s)")
            return near_earth_objects
        except requests.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            raise

    def write_to_bigquery(self, data):
        """Write data to nasa_table in BigQuery"""
        if not data:
            logger.info("No data to write to BigQuery.")
            return

        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)

        try:
            df = pd.DataFrame(data)
            logger.info(f"Prepared {len(df)} record(s) for storage")

            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                autodetect=False,  # Set to True to handle schema detection
            )

            logger.info("Writing data to BigQuery")
            job = self.client.load_table_from_dataframe(
                df,
                table_ref,
                job_config=job_config,
            )

            job.result()

            table = self.client.get_table(table_ref)
            logger.info(f"Write complete! Table now has {table.num_rows} total rows")

        except Exception as e:
            logger.error(f"Error uploading to BigQuery: {e}")
            raise

    def run_pipeline(self):
        """Execute the complete data pipeline"""
        try:
            logger.info("=" * 50)
            logger.info("Staring NASA Data Pipeline")
            logger.info("=" * 50)

            data = self.fetch_data()

            self.write_to_bigquery(data)

            logger.info("=" * 50)
            logger.info("Pipeline completed Successfully!")
            logger.info("=" * 50)
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run_pipeline()
