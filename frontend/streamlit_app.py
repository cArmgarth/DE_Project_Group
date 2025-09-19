import streamlit as st
from google.cloud import bigquery

# Create API client.
credentials_dict = st.secrets["BIGQUERY_CREDENTIALS_TOML"]
client = bigquery.Client.from_service_account_info(credentials_dict)


# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows


rows = run_query(
    "SELECT * FROM `team-tinfoil.training_data.training_combined` LIMIT 10"
)

# Print results.
st.write("Behold, the :rainbow[secrets of the stars!!!]")
for row in rows:
    st.write(row)
