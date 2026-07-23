from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
NUMBER_OF_CUSTOMERS = 1_000
rng = np.random.default_rng(SEED)

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def generate_campaigns() -> pd.DataFrame:
    rows = [
        ["CMP-001", "Spring Loyalty Bonus", "Email", "2026-03-01", "2026-03-21", 400, "High Value", 0.08, 4.0],
        ["CMP-002", "Summer Social Reach", "Paid Social", "2026-04-01", "2026-04-30", 1200, "New", 0.04, 2.5],
        ["CMP-003", "Win-back SMS", "SMS", "2026-05-01", "2026-05-14", 500, "At Risk", 0.07, 2.0],
        ["CMP-004", "App Exclusive Offer", "Push", "2026-05-15", "2026-06-05", 300, "Active", 0.09, 4.5],
        ["CMP-005", "Premium Customer Week", "Email", "2026-06-01", "2026-06-14", 350, "High Value", 0.10, 5.0],
        ["CMP-006", "Mid-year Acquisition", "Paid Search", "2026-06-15", "2026-07-15", 900, "New", 0.05, 3.0],
    ]
    columns = [
        "campaign_id", "campaign_name", "channel", "start_date",
        "end_date", "budget", "target_segment",
        "conversion_target", "roas_target",
    ]
    campaigns = pd.DataFrame(rows, columns=columns)
    campaigns["start_date"] = pd.to_datetime(campaigns["start_date"])
    campaigns["end_date"] = pd.to_datetime(campaigns["end_date"])
    return campaigns


def generate_customers(number_of_customers: int) -> pd.DataFrame:
    segments = ["New", "Active", "High Value", "At Risk"]
    segment_probabilities = [0.25, 0.40, 0.15, 0.20]
    loyalty_probabilities = {
        "New": 0.10,
        "Active": 0.40,
        "High Value": 0.75,
        "At Risk": 0.30,
    }
    rows = []

    for number in range(1, number_of_customers + 1):
        segment = rng.choice(segments, p=segment_probabilities)
        rows.append(
            {
                "customer_id": f"CUS-{number:05d}",
                "customer_segment": segment,
                "loyalty_member": (
                    rng.random() < loyalty_probabilities[segment]
                ),
            }
        )

    return pd.DataFrame(rows)


def generate_campaign_events(
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    rates = {
        "Email": (0.60, 0.35, 0.45),
        "Paid Social": (0.75, 0.18, 0.18),
        "SMS": (0.80, 0.30, 0.35),
        "Push": (0.70, 0.28, 0.38),
        "Paid Search": (0.70, 0.25, 0.24),
    }
    results = []

    for index, campaign in campaigns.iterrows():
        eligible = customers[
            customers["customer_segment"] == campaign["target_segment"]
        ]
        audience_size = min(120, len(eligible))
        audience = eligible.sample(
            audience_size,
            random_state=SEED + index,
        )[["customer_id"]].copy()

        open_rate, click_rate, conversion_rate = rates[campaign["channel"]]
        audience["campaign_id"] = campaign["campaign_id"]
        audience["sent"] = True
        audience["opened"] = rng.random(audience_size) < open_rate
        audience["clicked"] = (
            audience["opened"]
            & (rng.random(audience_size) < click_rate)
        )
        audience["converted"] = (
            audience["clicked"]
            & (rng.random(audience_size) < conversion_rate)
        )
        results.append(audience)

    return pd.concat(results, ignore_index=True)


def generate_transactions(
    events: pd.DataFrame,
    campaigns: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    converted = events[events["converted"]].copy()
    converted = converted.merge(
        campaigns[["campaign_id", "end_date"]],
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )
    converted = converted.merge(
        customers[["customer_id", "loyalty_member"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    count = len(converted)
    transactions = pd.DataFrame(
        {
            "transaction_id": [
                f"TRX-{number:06d}" for number in range(1, count + 1)
            ],
            "customer_id": converted["customer_id"],
            "campaign_id": converted["campaign_id"],
            "transaction_date": (
                converted["end_date"]
                + pd.to_timedelta(rng.integers(0, 8, count), unit="D")
            ),
            "gross_amount": rng.uniform(40, 250, count).round(2),
            "loyalty_member": converted["loyalty_member"],
        }
    )
    transactions["discount_amount"] = np.where(
        transactions["loyalty_member"],
        transactions["gross_amount"] * 0.10,
        0,
    ).round(2)
    transactions["status"] = rng.choice(
        ["Completed", "Refunded"],
        size=count,
        p=[0.92, 0.08],
    )
    transactions["net_amount"] = (
        transactions["gross_amount"]
        - transactions["discount_amount"]
    ).round(2)
    transactions.loc[
        transactions["status"] == "Refunded",
        "net_amount",
    ] *= -1
    return transactions.drop(columns="loyalty_member")


campaigns = generate_campaigns()
customers = generate_customers(NUMBER_OF_CUSTOMERS)
events = generate_campaign_events(customers, campaigns)
transactions = generate_transactions(events, campaigns, customers)

campaigns.to_excel(
    RAW_DIR / "campaigns.xlsx",
    index=False,
    sheet_name="Campaigns",
)
customers.to_csv(RAW_DIR / "customers.csv", index=False)
events.to_json(
    RAW_DIR / "campaign_events.json",
    orient="records",
    lines=True,
)
transactions.to_csv(RAW_DIR / "transactions.csv", index=False)

print(f"Created {len(campaigns)} campaigns.")
print(f"Created {len(customers)} customers.")
print(f"Created {len(events)} campaign events.")
print(f"Created {len(transactions)} transactions.")
