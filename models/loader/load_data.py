import pandas as pd
from google.cloud import bigquery


def fetch_data(project_id: str, query: str) -> pd.DataFrame:
    client = bigquery.Client(project=project_id)
    df = client.query(query).to_dataframe()
    return df


if __name__ == "__main__":
    # Example usage
    project_id = "team-tinfoil"
    query = """
    SELECT *
    FROM `team-tinfoil.training_data.training_combined`
    LIMIT 100
    """
    df = fetch_data(project_id, query)
    df.to_csv("data/local_copy.csv")
