CREATE OR REPLACE VIEW campaign_performance AS

WITH funnel AS (
    SELECT
        campaign_id,
        COUNT(*) AS customers_sent,
        COUNT(*) FILTER (WHERE opened) AS customers_opened,
        COUNT(*) FILTER (WHERE clicked) AS customers_clicked,
        COUNT(*) FILTER (WHERE converted) AS customers_converted
    FROM campaign_events
    GROUP BY campaign_id
),

revenue AS (
    SELECT
        campaign_id,
        COUNT(DISTINCT transaction_id) AS transactions,
        COUNT(DISTINCT customer_id) AS purchasing_customers,
        SUM(net_amount) AS net_revenue,
        AVG(net_amount) AS average_order_value
    FROM transactions
    GROUP BY campaign_id
)

SELECT
    campaigns.campaign_id,
    campaigns.campaign_name,
    campaigns.channel,
    campaigns.target_segment,
    campaigns.start_date,
    campaigns.end_date,
    campaigns.budget,
    campaigns.conversion_target,
    campaigns.roas_target,

    COALESCE(funnel.customers_sent, 0) AS customers_sent,
    COALESCE(funnel.customers_opened, 0) AS customers_opened,
    COALESCE(funnel.customers_clicked, 0) AS customers_clicked,
    COALESCE(funnel.customers_converted, 0) AS customers_converted,

    COALESCE(revenue.transactions, 0) AS transactions,
    COALESCE(revenue.purchasing_customers, 0) AS purchasing_customers,
    COALESCE(revenue.net_revenue, 0) AS net_revenue,
    COALESCE(revenue.average_order_value, 0) AS average_order_value,

    funnel.customers_opened * 1.0
        / NULLIF(funnel.customers_sent, 0) AS open_rate,

    funnel.customers_clicked * 1.0
        / NULLIF(funnel.customers_opened, 0) AS click_rate,

    funnel.customers_converted * 1.0
    / NULLIF(funnel.customers_sent, 0) AS conversion_rate,

funnel.customers_converted * 1.0
    / NULLIF(funnel.customers_clicked, 0)
    AS click_to_conversion_rate,

    COALESCE(revenue.net_revenue, 0)
        / NULLIF(campaigns.budget, 0) AS roas,

    campaigns.budget
        / NULLIF(funnel.customers_converted, 0)
        AS cost_per_conversion

FROM campaigns

LEFT JOIN funnel
    ON campaigns.campaign_id = funnel.campaign_id

LEFT JOIN revenue
    ON campaigns.campaign_id = revenue.campaign_id;