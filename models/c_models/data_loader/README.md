# BigQuery Data Loader

Simple script to load data from BigQuery tables for model training.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set environment variable:
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
```

## Usage

```python
from data_loader import load_data_from_bigquery

# Load data from BigQuery table
df = load_data_from_bigquery("your-project.your_dataset.your_table", limit=1000)

# Use the data for model training
print(f"Loaded {len(df)} rows")
print(df.head())
```

That's it! The function returns a pandas DataFrame ready for model training.
