# Marketing Analytics Dashboard

A compact end-to-end analytics project that evaluates marketing campaign performance by connecting funnel engagement with commercial outcomes such as revenue, conversion rate, ROAS and target achievement.

All data used in this project is fully synthetic. No company, customer or confidential information is included.

## Business questions

The project addresses three questions:

1. Which campaigns generate the strongest commercial results?
2. Where do customers drop out of the campaign funnel?
3. Which campaigns achieve their conversion and ROAS targets?

## Analytical workflow

```text
Synthetic source data
        ↓
Python generation and validation
        ↓
DuckDB analytical database
        ↓
SQL transformations and campaign-level metrics
        ↓
Power BI semantic and presentation layer
```

## Technology

- Python
- pandas and NumPy
- Faker
- DuckDB
- SQL
- Power BI and DAX
- Git and GitHub

## Source datasets and grain

| Dataset | Grain | Purpose |
|---|---|---|
| `customers.csv` | One row per customer | Synthetic CRM customer master |
| `campaigns.xlsx` | One row per campaign | Campaign plan, budget and targets |
| `campaign_events.json` | One row per customer and campaign | Funnel activity: sent, opened, clicked and converted |
| `transactions.csv` | One row per transaction | Revenue associated with customers and campaigns |
| `campaign_performance.csv` | One row per campaign | Curated campaign-level reporting output |

Defining the grain before joining the datasets was important because campaign events and transactions are separate fact-level datasets. They are aggregated independently to campaign grain before their metrics are combined, preventing row multiplication and overstated revenue.

## Metrics

- Customers sent, opened, clicked and converted
- Open rate
- Click-through rate
- Conversion rate
- Net revenue
- Average order value
- Cost per conversion
- Return on advertising spend (ROAS)
- ROAS and conversion variance against campaign targets

## Project structure

```text
marketing-analytics-dashboard/
- data/
    raw/
     curated/
- powerbi/
     Marketing Analytics Dashboard.pbix
        marketing_theme.json
- python/
      generate_data.py
        prepare_data.py
- sql/
      02_campaign_performance.sql
- README.md
- requirements.txt
```

## Running the project locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Generate the synthetic source data:

```powershell
python .\python\generate_data.py
```

Create the DuckDB tables and curated analytical output:

```powershell
python .\python\prepare_data.py
```

The curated campaign performance data is written to:

```text
data/curated/campaign_performance.csv
data/curated/campaign_performance.parquet
```

The Power BI report is available in:

```text
powerbi/Marketing Analytics Dashboard.pbix
```

## Dashboard

The Campaign Performance Overview includes:

- executive KPI cards;
- campaign revenue ranking;
- ROAS comparison against campaign targets;
- funnel progression from sent to converted;
- detailed target-performance table;
- channel and customer-segment filters.

## Example findings

- Win-back SMS generated the highest total campaign revenue.
- App Exclusive Offer achieved the highest ROAS because of its comparatively low budget.
- Campaigns with substantial reach did not necessarily deliver the strongest commercial efficiency.
- The funnel shows that engagement performance and final conversion should be evaluated as separate stages.

## Limitations and possible extensions

- Campaign attribution is simplified to a single campaign identifier.
- The project does not attempt to establish causal campaign impact.
- Synthetic patterns were deliberately introduced to create realistic analytical scenarios.
- Potential extensions include customer-level loyalty analysis, cohort retention, multi-touch attribution and a transaction-level drill-through page.
