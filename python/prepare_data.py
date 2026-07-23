from pathlib import Path

import duckdb
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
CURATED_DIR = PROJECT_DIR / "data" / "curated"
DB_PATH = PROJECT_DIR / "marketing_analytics.duckdb"
CURATED_DIR.mkdir(parents=True, exist_ok=True)

customers = pd.read_csv(RAW_DIR / "customers.csv")
campaigns = pd.read_excel(RAW_DIR / "campaigns.xlsx")
events = pd.read_json(
    RAW_DIR / "campaign_events.json",
    lines=True,
)
transactions = pd.read_csv(RAW_DIR / "transactions.csv")

campaigns["start_date"] = pd.to_datetime(
    campaigns["start_date"],
    errors="coerce",
)
campaigns["end_date"] = pd.to_datetime(
    campaigns["end_date"],
    errors="coerce",
)
transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce",
)

assert customers["customer_id"].is_unique
assert campaigns["campaign_id"].is_unique
assert transactions["transaction_id"].is_unique
assert not events.duplicated(
    subset=["campaign_id", "customer_id"]
).any()
assert set(events["customer_id"]) <= set(customers["customer_id"])
assert set(events["campaign_id"]) <= set(campaigns["campaign_id"])

tables = {
    "customers": customers,
    "campaigns": campaigns,
    "campaign_events": events,
    "transactions": transactions,
}

connection = duckdb.connect(str(DB_PATH))
for table_name, dataframe in tables.items():
    connection.register("source_df", dataframe)
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM source_df
        """
    )

sql_path = PROJECT_DIR / "sql" / "02_campaign_performance.sql"
connection.execute(sql_path.read_text(encoding="utf-8"))
campaign_performance = connection.execute(
    """
    SELECT *
    FROM campaign_performance
    ORDER BY net_revenue DESC
    """
).df()
connection.close()

campaign_performance.to_csv(
    CURATED_DIR / "campaign_performance.csv",
    index=False,
)
campaign_performance.to_parquet(
    CURATED_DIR / "campaign_performance.parquet",
    index=False,
)

print("Data validation passed.")
print(campaign_performance)
