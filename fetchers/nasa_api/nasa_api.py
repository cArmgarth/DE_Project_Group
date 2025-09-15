import json
import logging
import os
from datetime import date, datetime, timedelta, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from google.cloud import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Stockholm timezone (UTC+1 in winter, UTC+2 in summer)
stockholm_tz = timezone(timedelta(hours=1))

TODAY = date.today().strftime("%Y-%m-%d")
YESTERDAY = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
NOW = datetime.now()
API_KEY = os.environ.get("NASA_API")


@app.route("/")
def home():
    """Collect NASA Data"""

    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        "start_date": YESTERDAY,
        "end_date": YESTERDAY,
        "api_key": API_KEY,
    }

    try:
        logger.info("Fetching data from NASA")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        # Unpack the topmost dict
        near_earth_objects_by_date = data.get("near_earth_objects", {})

        todays_space_rocks = []
        for date_key, objects in near_earth_objects_by_date.items():
            for obj in objects:
                obj["date"] = date_key  # Adds date back in
                todays_space_rocks.append(obj)

        logger.info(
            "Successfully fetched information about %s space rocks",
            len(todays_space_rocks),
        )
    except requests.RequestException as e:
        logger.error("Houston, we have a problem: %s", e)

    # Upload to GCS with date-based filename (overwrites previous day's file)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"nasa_raw_data{date_str}.json"
    upload_success = upload_to_gcs(todays_space_rocks, filename)

    # Add upload status to response
    response_data = {
        "data": todays_space_rocks,
        "upload_status": "success" if upload_success else "failed",
    }

    return jsonify(response_data)


@app.route("/health")
def health():
    return {"status": "ok"}


def upload_to_gcs(data: list[dict], filename: str) -> bool:
    """Upload data to Google Cloud Storage as NDJSON"""
    try:
        # Only set service account key if running locally (file exists)
        # On GCP, use default credentials
        if os.path.exists("credentials.json"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
            logger.info("Using local service account key")
        else:
            logger.info("Using default GCP credentials")

        client = storage.Client()
        bucket = client.bucket("nasa_api_bucket")

        # Create blob with filename in /raw folder
        blob = bucket.blob(f"raw/{filename}")

        # Convert to NDJSON format
        ndjson_data = "\n".join(json.dumps(item) for item in data) + "\n"

        # Upload NDJSON data
        blob.upload_from_string(ndjson_data, content_type="application/x-ndjson")

        logger.info(
            "Successfully uploaded %s to GCS bucket: nasa_api_bucket/raw/", filename
        )
        return True
    except Exception as e:
        logger.error("Error uploading to GCS: %s", e)
        import traceback

        logger.error("Traceback: %s", traceback.format_exc())
        return False



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
