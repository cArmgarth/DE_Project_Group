import os

import altair as alt
import pandas as pd
import streamlit as st
from google.cloud import bigquery

# Create API client based on environment.
if "K_SERVICE" in os.environ:
    # Running on Google Cloud, use Application Default Credentials.
    client = bigquery.Client()
else:
    # Running locally, use service account info from st.secrets.
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


st.set_page_config(layout="wide")

predictions = run_query("""
    SELECT
        date,
        rfr_pred_reddit_count AS `RandomForestRegressor Reddit`,
        rfr_pred_twitter_count AS `RandomForestRegressor Twitter`,
        true_reddit_count AS `True Reddit count`,
        elastic_reddit_count AS `ElasticNet Reddit`,
        elastic_twitter_count AS `ElasticNet Twitter`,
        true_twitter_count AS `True Twitter count`
    FROM `team-tinfoil.predictions_stg.predictions_2models`
    """)

nasa_data = run_query("SELECT * FROM `team-tinfoil.stg_data.nasa_stg_data`")

pred_df = pd.DataFrame(predictions)
nasa_df = pd.DataFrame(nasa_data)

# Render frontend
st.title("TEAM-TINFOIL PREDICTS")

st.write("""Vi ger er inte bara en, utan två, handgjorda, state-of-the-art och
            glutenfria AI-modeller som tillsammans kan förutsäga aktiviteten
            hos UFO-entusiaster på Twitter och Reddit!
            Möjligheterna att utnyttja denna information är såklart oändliga,
            men främst tänkta att användas som beslutsunderlag för
            hur mycket aluminiumfolie som ska tillverkas och säljas
            under de närmaste dagarna.
            Använd informationen ansvarsfullt...
            """)

st.header("Predictions")
col1, col2 = st.columns(2)
with col1:
    st.write(":red[Reddit]")
    st.line_chart(
        data=pred_df,
        x="date",
        y=["RandomForestRegressor Reddit",
            "ElasticNet Reddit", "True Reddit count"],
        y_label="Reddit posts",
        color=["#ff4500", "#cc241d", "#98971a"],
    )
with col2:
    st.write(":blue[Twitter]")
    st.line_chart(
        data=pred_df,
        x="date",
        y=["RandomForestRegressor Twitter",
            "ElasticNet Twitter", "True Twitter count"],
        y_label="Tweets",
        color=["#458588", "#268bd2", "#98971a"],
    )

st.header("Nasa data")
nasa_df["date"] = pd.to_datetime(nasa_df["date"]).dt.date
date_options = sorted(nasa_df["date"].unique())
selected_date = st.select_slider("Select a date:", options=date_options)
filtered = nasa_df[nasa_df["date"] == selected_date]

# numeric_cols should contain your 19 metrics
numeric_cols = [col for col in nasa_df if col != "date"]

# prepare max values across whole dataset for fixed scales
max_vals = nasa_df[numeric_cols].max()

# build grid
rows, cols_per_row = 3, 7
total_slots = rows * cols_per_row

# fill slots
slot = 0
for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        if slot < len(numeric_cols):
            metric = numeric_cols[slot]
            max_val = max_vals[metric]

            chart = (
                alt.Chart(filtered)  # filtered is the single selected date
                .mark_bar()
                .encode(
                    x=alt.X("date:O", axis=None),
                    y=alt.Y(metric, scale=alt.Scale(domain=[0, max_val])),
                )
                .properties(title=metric)
            )
            cols[col_idx].altair_chart(chart, use_container_width=True)

        else:
            # leftover slots → display numbers instead of charts
            if slot == len(numeric_cols):
                reddit_pred = pred_df.loc[
                    pred_df["date"] == selected_date, "RandomForestRegressor Reddit"
                ]
                result = reddit_pred.squeeze() if not reddit_pred.empty else None
                cols[col_idx].metric("Predicted Reddit posts", result)
            elif slot == len(numeric_cols) + 1:
                twitter_pred = pred_df.loc[
                    pred_df["date"] == selected_date, "RandomForestRegressor Twitter"
                ]
                result = twitter_pred.squeeze() if not twitter_pred.empty else None
                cols[col_idx].metric("Predicted Tweets", result)

        slot += 1
