# BigQuery Data API

A Flask API that connects to BigQuery and provides data and plot information as JSON.

## Features

- **BigQuery Integration**: Fetches data directly from your BigQuery tables
- **JSON API**: Returns data and plot information as JSON
- **Plot Generation**: Creates Plotly.js plot data for frontend consumption
- **Error Handling**: Graceful error handling with informative messages

## Environment Variables

Configure these environment variables for your deployment:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_TABLE=team-tinfoil.predictions_data.predict_this
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json  # For local development only
```

## Local Development

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export BIGQUERY_TABLE=team-tinfoil.predictions_data.predict_this
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   ```

3. **Run the application:**
   ```bash
   uv run python main.py
   ```

4. **View your plot:**
   - Open your browser and go to: http://localhost:8080/
   - The plot will display directly in your browser!

## Deployment

### Using Cloud Build

1. **Commit and push your code to GitHub**
2. **Trigger Cloud Build:**
   ```bash
   gcloud builds submit --config frontend/flask_app/cloudbuild.yaml .
   ```

3. **Access your deployed service:**
   The Cloud Run URL will be provided after deployment.

## How It Works

### GET /
**Main route** - Displays your BigQuery data as an interactive plot directly in the browser.

**What happens:**
1. Fetches data from your BigQuery table
2. Creates a Plotly interactive plot (time series or bar chart)
3. Generates complete HTML page with the plot
4. Displays directly in browser - no HTML files needed!

**Features:**
- Interactive zoom, pan, hover
- Responsive design
- Auto-detects best plot type for your data
- Error handling with clear messages

## Features

### Automatic Plot Generation
- **Time Series**: Automatically detects date columns and numeric values
- **Bar Charts**: Uses the first column as x-axis, numeric columns as y-axis
- **Responsive**: Plots automatically resize based on screen size

### Data Visualization
- **Interactive**: Hover over data points for detailed information
- **Multiple Series**: Support for multiple data series on the same plot
- **Auto-refresh**: Page refreshes every 5 minutes to show latest data

### Error Handling
- Graceful error handling for BigQuery connection issues
- User-friendly error messages in the UI
- Fallback displays when no data is available

## Customization

### Adding New Plot Types
1. Create a new function in `main.py` (e.g., `create_scatter_plot()`)
2. Add the plot to the template in `index.html`
3. Create an API endpoint for the new plot type

### Styling
- Modify `templates/base.html` for global styles
- Update Bootstrap classes in `templates/index.html`
- Customize Plotly themes in the plot creation functions

## Requirements

- Python 3.13+
- Flask 2.3+
- Google Cloud BigQuery client
- Plotly for Python
- Pandas for data manipulation
