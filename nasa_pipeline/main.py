import requests
import json
import os
from datetime import datetime, timedelta, date
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

TODAY = date.today().strftime("%Y-%m-%d")
YESTERDAY = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
NOW = datetime.now().strftime("%Y-%m-%d")


class DataPipeline:
    def __init__(self):
        """Initialize the data pipeline with BigQuery client and configuration"""
        self.client = bigquery.Client()
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        self.dataset_id = os.environ.get("BQ_DATASET_ID", "raw_data")
        self.table_id = os.environ.get("BQ_TABLE_ID", "nasa_data")

        logger.info("Pipeline initialized for NASA data collection.")

    def fetch_data(self):
        """ "Fetch data from NASA's API"""
        try:
            logger.info("Fetching data from NASA API...")
            response = requests.get()
        except:
            pass


def main():
    print("Hello from nasa-pipeline!")


if __name__ == "__main__":
    main()
