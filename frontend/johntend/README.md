# Frontend

A web-based dashboard for visualizing UFO activity data from multiple sources, featuring both Streamlit and Flask applications for data exploration and interactive plotting.

## Overview

This frontend component provides two different interfaces for exploring and visualizing UFO-related data collected from NASA, Reddit, and Twitter APIs. The data is stored in BigQuery and visualized through interactive plots showing true values vs. machine learning predictions.

## Components

### 1. Streamlit App (`streamlit_app.py`)
- Simple data exploration interface
- Displays raw data from BigQuery
- Uses Streamlit secrets for authentication
- Cached queries for performance

### 2. Flask App (`flask_app/main.py`)
- Advanced interactive plotting dashboard
- Side-by-side comparison of Reddit and Twitter data
- True values vs. ML model predictions visualization
- Responsive full-screen interface

## Features

- **Data Visualization**: Interactive plots comparing actual vs. predicted values
- **Multi-Source Data**: Displays data from Reddit, Twitter, and NASA sources
- **ML Model Results**: Shows Random Forest and Elastic Net regression predictions
- **Responsive Design**: Full-screen, mobile-friendly interface
- **Real-time Data**: Fetches latest data from BigQuery
- **Authentication**: Secure BigQuery integration

## Environment Variables

### Flask App
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key (local development)
- `BIGQUERY_TABLE` - BigQuery table ID (optional, defaults to env var)
- `PORT` - Port to run Flask app (default: 8080)
- `FLASK_DEBUG` - Enable debug mode (default: False)

### Streamlit App
- Uses Streamlit secrets for BigQuery credentials
- Configure in `.streamlit/secrets.toml`

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. For Flask app, set up environment variables:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your_project_id"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
   export BIGQUERY_TABLE="your_project.dataset.table"
   ```

3. For Streamlit app, configure secrets:
   ```bash
   mkdir -p .streamlit
   # Create .streamlit/secrets.toml with BigQuery credentials
   ```

## Usage

### Flask App
Run the interactive dashboard:
```bash
uv run python flask_app/main.py
```

Access at `http://localhost:8080` for full-screen interactive plots.

### Streamlit App
Run the data exploration interface:
```bash
uv run streamlit run streamlit_app.py
```

Access at `http://localhost:8501` for the Streamlit interface.

## Data Visualization

The Flask app creates sophisticated visualizations showing:
- **Reddit Data**: UFO-related post counts over time
- **Twitter Data**: UFO-related tweet counts over time
- **Model Predictions**: Random Forest and Elastic Net regression results
- **True vs. Predicted**: Side-by-side comparison of actual and predicted values

## Plot Features

- Dark theme with neon colors (green, pink)
- Interactive hover tooltips
- Zoom and pan capabilities
- Responsive design for all screen sizes
- Legend showing model types
- Date-based x-axis with proper formatting

## Dependencies

- **Flask** - Web framework for dashboard
- **Streamlit** - Data exploration interface
- **Plotly** - Interactive plotting library
- **Pandas** - Data manipulation
- **Google Cloud BigQuery** - Data source
- **python-dotenv** - Environment variable loading

## BigQuery Integration

Both apps connect to BigQuery using:
- Service account authentication (local development)
- Default credentials (Cloud Run deployment)
- Cached queries for performance optimization
- Error handling for connection issues

## Security

- Service account keys stored securely
- Environment variables for sensitive data
- Streamlit secrets for production deployment
- No hardcoded credentials in code
