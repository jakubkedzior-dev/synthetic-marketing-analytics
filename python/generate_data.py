from pathlib import Path
import random

import numpy as np
import pandas as pd
from faker import Faker


SEED = 42
NUMBER_OF_CUSTOMERS = 1_000

random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)

fake = Faker("en_GB")
rng = np.random.default_rng(SEED)

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_campaigns() -> pd.DataFrame:
    campaigns = pd.DataFrame(
        [
            {
                "campaign_id": "CMP-001",
                "campaign_name": "Spring Loyalty Bonus",
                "channel": "Email",
                "start_date": "2026-03-01",
                "end_date": "2026-03-21",
                "budget": 400,
                "target_segment": "High Value",
                "conversion_target": 0.08,
                "roas_target": 4.0,
            },
            {
                "campaign_id": "CMP-002",
                "campaign_name": "Summer Social Reach",
                "channel": "Paid Social",
                "start_date": "2026-04-01",
                "end_date": "2026-04-30",
                "budget": 1200,
                "target_segment": "New",
                "conversion_target": 0.04,
                "roas_target": 2.5,
            },
            {
                "campaign_id": "CMP-003",
                "campaign_name": "Win-back SMS",
                "channel": "SMS",
                "start_date": "2026-05-01",
                "end_date": "2026-05-14",
                "budget": 500,
                "target_segment": "At Risk",
                "conversion_target": 0.07,
                "roas_target": 3.0,
            },
            {
                "campaign_id": "CMP-004",
                "campaign_name": "App Exclusive Offer",
                "channel": "Push",
                "start_date": "2026-05-15",
                "end_date": "2026-06-05",
                "budget": 300,
                "target_segment": "Active",
                "conversion_target": 0.09,
                "roas_target": 4.5,
            },
            {
                "campaign_id": "CMP-005",
                "campaign_name": "Premium Customer Week",
                "channel": "Email",
                "start_date": "2026-06-01",
                "end_date": "2026-06-14",
                "budget": 350,
                "target_segment": "High Value",
                "conversion_target": 0.10,
                "roas_target": 5.0,
            },
            {
                "campaign_id": "CMP-006",
                "campaign_name": "Mid-year Acquisition",
                "channel": "Paid Search",
                "start_date": "2026-06-15",
                "end_date": "2026-07-15",
                "budget": 900,
                "target_segment": "New",
                "conversion_target": 0.05,
                "roas_target": 3.0,
            },
        ]
    )

    campaigns["start_date"] = pd.to_datetime(campaigns["start_date"])
    campaigns["end_date"] = pd.to_datetime(campaigns["end_date"])

    return campaigns

def generate_customers(number_of_customers: int) -> pd.DataFrame:
    countries = ["Poland", "Germany", "United Kingdom", "Spain"]
    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
    acquisition_channels = [
        "Organic",
        "Paid Search",
        "Paid Social",
        "Referral",
        "Email",
    ]
    customer_segments = ["New", "Active", "High Value", "At Risk"]

    customers = []

    for customer_number in range(1, number_of_customers + 1):
        customer_id = f"CUS-{customer_number:05d}"

        registration_date = fake.date_between(
            start_date="-3y",
            end_date="-30d",
        )

        customer_segment = rng.choice(
            customer_segments,
            p=[0.25, 0.40, 0.15, 0.20],
        )

        loyalty_probability = {
            "New": 0.10,
            "Active": 0.40,
            "High Value": 0.75,
            "At Risk": 0.30,
        }[customer_segment]

        loyalty_member = rng.random() < loyalty_probability

        if loyalty_member:
            loyalty_join_date = fake.date_between(
                start_date=registration_date,
                end_date="today",
            )
        else:
            loyalty_join_date = None

        customers.append(
            {
                "customer_id": customer_id,
                "registration_date": registration_date,
                "country": rng.choice(
                    countries,
                    p=[0.45, 0.20, 0.20, 0.15],
                ),
                "age_group": rng.choice(
                    age_groups,
                    p=[0.15, 0.30, 0.25, 0.18, 0.12],
                ),
                "customer_segment": customer_segment,
                "acquisition_channel": rng.choice(
                    acquisition_channels,
                    p=[0.30, 0.20, 0.20, 0.15, 0.15],
                ),
                "loyalty_member": loyalty_member,
                "loyalty_join_date": loyalty_join_date,
            }
        )

    return pd.DataFrame(customers)

def generate_campaign_events(
    customers: pd.DataFrame,
    campaigns: pd.DataFrame,
) -> pd.DataFrame:
    channel_rates = {
        "Email": {
            "open_rate": 0.60,
            "click_rate": 0.35,
            "conversion_rate": 0.45,
        },
        "Paid Social": {
            "open_rate": 0.75,
            "click_rate": 0.18,
            "conversion_rate": 0.18,
        },
        "SMS": {
            "open_rate": 0.80,
            "click_rate": 0.30,
            "conversion_rate": 0.35,
        },
        "Push": {
            "open_rate": 0.70,
            "click_rate": 0.28,
            "conversion_rate": 0.38,
        },
        "Paid Search": {
            "open_rate": 0.70,
            "click_rate": 0.25,
            "conversion_rate": 0.24,
        },
    }

    campaign_results = []

    for campaign_index, campaign in campaigns.iterrows():
        target_customers = customers[
            customers["customer_segment"]
            == campaign["target_segment"]
        ]

        audience_size = min(120, len(target_customers))

        audience = target_customers.sample(
            n=audience_size,
            random_state=SEED + campaign_index,
        ).copy()

        rates = channel_rates[campaign["channel"]]

        audience["campaign_id"] = campaign["campaign_id"]
        audience["sent"] = True

        audience["opened"] = (
            rng.random(audience_size) < rates["open_rate"]
        )

        audience["clicked"] = (
            audience["opened"]
            & (rng.random(audience_size) < rates["click_rate"])
        )

        audience["converted"] = (
            audience["clicked"]
            & (rng.random(audience_size) < rates["conversion_rate"])
        )

        campaign_results.append(
            audience[
                [
                    "campaign_id",
                    "customer_id",
                    "sent",
                    "opened",
                    "clicked",
                    "converted",
                ]
            ]
        )

    return pd.concat(
        campaign_results,
        ignore_index=True,
    )
def generate_transactions(
    campaign_events: pd.DataFrame,
    campaigns: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    converted_customers = campaign_events[
        campaign_events["converted"]
    ].copy()

    converted_customers = converted_customers.merge(
        campaigns[
            [
                "campaign_id",
                "end_date",
            ]
        ],
        on="campaign_id",
        how="left",
    )

    converted_customers = converted_customers.merge(
        customers[
            [
                "customer_id",
                "loyalty_member",
            ]
        ],
        on="customer_id",
        how="left",
    )

    number_of_transactions = len(converted_customers)

    transactions = pd.DataFrame(
        {
            "transaction_id": [
                f"TRX-{number:06d}"
                for number in range(1, number_of_transactions + 1)
            ],
            "customer_id": converted_customers["customer_id"],
            "campaign_id": converted_customers["campaign_id"],
            "transaction_date": (
                converted_customers["end_date"]
                + pd.to_timedelta(
                    rng.integers(0, 8, number_of_transactions),
                    unit="D",
                )
            ),
            "gross_amount": rng.uniform(
                40,
                250,
                number_of_transactions,
            ).round(2),
            "loyalty_member": converted_customers[
                "loyalty_member"
            ],
        }
    )

    transactions["discount_amount"] = np.where(
        transactions["loyalty_member"],
        transactions["gross_amount"] * 0.10,
        0,
    ).round(2)

    transactions["status"] = rng.choice(
        ["Completed", "Refunded"],
        size=number_of_transactions,
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

    return transactions.drop(columns=["loyalty_member"])

campaigns = generate_campaigns()
customers = generate_customers(NUMBER_OF_CUSTOMERS)

campaign_events = generate_campaign_events(
    customers,
    campaigns,
)
transactions = generate_transactions(
    campaign_events,
    campaigns,
    customers,
)

campaigns_path = RAW_DATA_DIR / "campaigns.xlsx"
customers_path = RAW_DATA_DIR / "customers.csv"
events_path = RAW_DATA_DIR / "campaign_events.json"
transactions_path = RAW_DATA_DIR / "transactions.csv"

campaigns.to_excel(
    campaigns_path,
    index=False,
    sheet_name="Campaigns",
)

customers.to_csv(
    customers_path,
    index=False,
)

campaign_events.to_json(
    events_path,
    orient="records",
    lines=True,
)
transactions.to_csv(
    transactions_path,
    index=False,
)

print(f"Created {len(campaigns)} campaigns.")
print(f"Created {len(customers)} customers.")
print(f"Created {len(campaign_events)} campaign events.")

print(f"Saved campaigns to: {campaigns_path}")
print(f"Saved customers to: {customers_path}")
print(f"Saved events to: {events_path}")

print(f"Created {len(transactions)} transactions.")
print(f"Saved transactions to: {transactions_path}")