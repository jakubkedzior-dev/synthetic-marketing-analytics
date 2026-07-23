from pathlib import Path

import duckdb
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
DATABASE_PATH = PROJECT_DIR / "marketing_analytics.duckdb"


customers = pd.read_csv(
    RAW_DATA_DIR / "customers.csv",
)

campaigns = pd.read_excel(
    RAW_DATA_DIR / "campaigns.xlsx",
    sheet_name="Campaigns",
)

campaign_events = pd.read_json(
    RAW_DATA_DIR / "campaign_events.json",
    lines=True,
)

transactions = pd.read_csv(
    RAW_DATA_DIR / "transactions.csv",
)


customers["registration_date"] = pd.to_datetime(
    customers["registration_date"],
    errors="coerce",
)

customers["loyalty_join_date"] = pd.to_datetime(
    customers["loyalty_join_date"],
    errors="coerce",
)

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
assert customers["customer_id"].notna().all()

assert campaigns["campaign_id"].is_unique
assert campaigns["campaign_id"].notna().all()

assert transactions["transaction_id"].is_unique
assert transactions["transaction_id"].notna().all()

assert not campaign_events.duplicated(
    subset=["campaign_id", "customer_id"]
).any()

assert set(campaign_events["customer_id"]).issubset(
    set(customers["customer_id"])
)

assert set(campaign_events["campaign_id"]).issubset(
    set(campaigns["campaign_id"])
)


connection = duckdb.connect(str(DATABASE_PATH))

connection.register("customers_df", customers)
connection.register("campaigns_df", campaigns)
connection.register("campaign_events_df", campaign_events)
connection.register("transactions_df", transactions)

connection.execute(
    """
    CREATE OR REPLACE TABLE customers AS
    SELECT *
    FROM customers_df
    """
)

connection.execute(
    """
    CREATE OR REPLACE TABLE campaigns AS
    SELECT *
    FROM campaigns_df
    """
)

connection.execute(
    """
    CREATE OR REPLACE TABLE campaign_events AS
    SELECT *
    FROM campaign_events_df
    """
)

connection.execute(
    """
    CREATE OR REPLACE TABLE transactions AS
    SELECT *
    FROM transactions_df
    """
)
sql_path = (
    PROJECT_DIR
    / "sql"
    / "02_campaign_performance.sql"
)

sql_query = sql_path.read_text(
    encoding="utf-8",
)

connection.execute(sql_query)

campaign_performance = connection.execute(
    """
    SELECT *
    FROM campaign_performance
    ORDER BY net_revenue DESC
    """
).df()

campaign_performance.to_parquet(
    PROJECT_DIR
    / "data"
    / "curated"
    / "campaign_performance.parquet",
    index=False,
)

campaign_performance.to_csv(
    PROJECT_DIR
    / "data"
    / "curated"
    / "campaign_performance.csv",
    index=False,
)

connection.close()

print("Data validation passed.")
print(f"Customers: {len(customers)}")
print(f"Campaigns: {len(campaigns)}")
print(f"Campaign events: {len(campaign_events)}")
print(f"Transactions: {len(transactions)}")
print(f"DuckDB database created: {DATABASE_PATH}")

print(f"SQL file: {sql_path}")
print(f"SQL length: {len(sql_query)} characters")