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

def create_separate_plots(df, date_column='date'):
    """Create separate plots for Reddit and Twitter data showing both actual and predicted values."""

    if df.empty:
        return None
    
    # Auto-detect date column if not specified
    if date_column not in df.columns:
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                date_column = col
                break
    
    # Find all reddit and twitter columns
    reddit_cols = []
    twitter_cols = []
    
    for col in df.columns:
        if col != date_column and pd.api.types.is_numeric_dtype(df[col]):
            col_lower = col.lower()
            if 'reddit' in col_lower:
                reddit_cols.append(col)
            elif 'twitter' in col_lower:
                twitter_cols.append(col)
    
    # Create subplots side by side (1 row, 2 columns)
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('<b>Reddit</b>', '<b>Twitter</b>'),
        horizontal_spacing=0.1,
        shared_yaxes=False
    )
    
    # Colors for both plots
    colors = ['#ffffff', '#00ff00', '#ff1493']  # White, Neon Green, Neon Pink
    
    # Define standard names for legend
    legend_names = ['True Value', 'Random Forrest Regressor', 'Elastic Net Regressor']
    
    # Add all Reddit columns
    for i, col in enumerate(reddit_cols):
        color = colors[i % len(colors)]
        symbol = 'circle' if 'true' in col.lower() else 'diamond'
        
        fig.add_trace(
            go.Scatter(
                x=df[date_column],
                y=df[col],
                mode='lines+markers',
                name=legend_names[i % len(legend_names)],
                line=dict(color=color, width=3),
                marker=dict(size=7, symbol=symbol),
                legendgroup="shared",
                showlegend=True
            ),
            row=1, col=1
        )
    
    # Add all Twitter columns (hide legend for these)
    for i, col in enumerate(twitter_cols):
        color = colors[i % len(colors)]
        symbol = 'circle' if 'true' in col.lower() else 'diamond'
        
        fig.add_trace(
            go.Scatter(
                x=df[date_column],
                y=df[col],
                mode='lines+markers',
                name=legend_names[i % len(legend_names)],
                line=dict(color=color, width=3),
                marker=dict(size=7, symbol=symbol),
                legendgroup="shared",
                showlegend=False
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="<b>Team Tinfoil's Super Mega Prediction Data - True vs Predicted Values</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=18, color="white"),
            y=0.95,
            yanchor='top'
        ),
        showlegend=True,
        template='plotly_dark',
        hovermode='x unified',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="white"
        ),
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#2d2d2d',
        autosize=True,
        margin=dict(t=120, b=80, l=40, r=40),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(size=14)
        )
    )
    
    # Update axes
    fig.update_xaxes(title_text="<b>Date</b>", row=1, col=1)
    fig.update_xaxes(title_text="<b>Date</b>", row=1, col=2)
    fig.update_yaxes(title_text="<b>Reddit Count</b>", row=1, col=1)
    fig.update_yaxes(title_text="<b>Twitter Count</b>", row=1, col=2)
    
    
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
        
        # Create separate plots for Reddit and Twitter
        plot_json = create_separate_plots(df)
        if not plot_json:
            # Fallback to single plot if separate plots fail
            plot_json = create_bar_plot(df)
        
        if not plot_json:
            return "Could not create plot", 500
        
        # Convert to Plotly figure
        fig = go.Figure(json.loads(plot_json))
        
        # Generate HTML string directly with responsive config
        html_string = pio.to_html(
            fig, 
            include_plotlyjs=True, 
            full_html=True,
            config={
                'responsive': True,
                'displayModeBar': True,
                'fillFrame': True
            }
        )
        
        # Add custom CSS for full viewport
        custom_css = """
        <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
        }
        .plotly-graph-div {
            width: 100vw !important;
            height: 100vh !important;
        }
        </style>
        """
        
        # Insert CSS into the HTML
        html_string = html_string.replace('<head>', f'<head>{custom_css}')
        
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