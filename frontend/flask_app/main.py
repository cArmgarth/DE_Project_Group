import json
import logging
import os

import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import plotly.utils
from dotenv import load_dotenv
from flask import Flask
from google.cloud import bigquery
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_bigquery_client():
    """Initialize BigQuery client with authentication."""

    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )
        client = bigquery.Client(credentials=credentials, project=project_id)
    else:
        # Use default credentials (for Cloud Run)
        client = bigquery.Client(project=project_id)
    
    return client

def fetch_data_from_bigquery(table_id=None, limit=100):
    """Fetch data from BigQuery table."""

    try:
        client = get_bigquery_client()
        
        if not table_id:
            table_id = os.getenv('BIGQUERY_TABLE')
        
        query = f"""
        SELECT *
        FROM `{table_id}`
        LIMIT {limit}
        """
        
        logger.info(f"Fetching data from {table_id}")
        df = client.query(query).to_dataframe()
        logger.info(f"Retrieved {len(df)} rows")
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def create_time_series_plot(df, date_column='date', value_columns=None):
    """Create a time series plot from DataFrame."""

    if df.empty:
        return None
    
    # Auto-detect date and value columns if not specified
    if date_column not in df.columns:
        # Find the first date-like column
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                date_column = col
                break
    
    if value_columns is None:
        # Find numeric columns (excluding date column)
        value_columns = [col for col in df.columns 
                        if col != date_column and pd.api.types.is_numeric_dtype(df[col])]
    
    fig = go.Figure()
    
    # Add traces for each value column
    for col in value_columns:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_column],
                y=df[col],
                mode='lines+markers',
                name=col.replace('_', ' ').title(),
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title="Team Tinfoil's Super Mega Prediction Data",
        xaxis_title='Date',
        yaxis_title='Values',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_bar_plot(df, x_column=None, y_columns=None):
    """Create a bar plot from DataFrame."""

    if df.empty:
        return None
    
    # Auto-detect columns if not specified
    if x_column is None:
        x_column = df.columns[0]  # Use first column as x-axis
    
    if y_columns is None:
        # Find numeric columns (excluding x column)
        y_columns = [col for col in df.columns 
                    if col != x_column and pd.api.types.is_numeric_dtype(df[col])]
    
    fig = go.Figure()
    
    # Add traces for each y column
    for col in y_columns:
        if col in df.columns:
            fig.add_trace(go.Bar(
                x=df[x_column],
                y=df[col],
                name=col.replace('_', ' ').title()
            ))
    
    fig.update_layout(
        title='Bar Chart Data from BigQuery',
        xaxis_title=x_column.replace('_', ' ').title(),
        yaxis_title='Values',
        barmode='group',
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    """Main route - displays interactive plot directly in browser."""

    try:
        df = fetch_data_from_bigquery()
        
        if df.empty:
            return "No data found in BigQuery table", 404
        
        # Create plot (prefer time series, fallback to bar chart)
        plot_json = create_time_series_plot(df)
        if not plot_json:
            plot_json = create_bar_plot(df)
        
        if not plot_json:
            return "Could not create plot", 500
        
        # Convert to Plotly figure
        fig = go.Figure(json.loads(plot_json))
        
        # Generate HTML string directly
        html_string = pio.to_html(fig, include_plotlyjs=True, full_html=True)
        
        # Return HTML directly
        return html_string
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}")
        return f"Error creating plot: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)