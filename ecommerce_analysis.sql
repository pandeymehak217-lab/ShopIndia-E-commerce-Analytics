-- ================================================================
-- ShopIndia E-commerce Analytics
-- Author      : Mehak Pandey
-- Email       : pandeymehak.217@gmail.com
-- Description : End-to-end e-commerce SQL analysis covering
--               sales performance, customer behaviour,
--               statistical analysis, and marketing ROI
-- Period      : 2020 - 2024
-- Tables      : customers, products, orders, order_items,
--               returns, campaigns
-- ================================================================

-- ----------------------------------------------------------------
-- SECTION 1: SALES PERFORMANCE ANALYSIS
-- ----------------------------------------------------------------

-- 1.1 Year-wise revenue, orders, and growth
WITH yearly AS (
    SELECT
        oi.order_year,
        COUNT(DISTINCT o.order_id)           AS total_orders,
        COUNT(DISTINCT o.customer_id)        AS unique_customers,
        ROUND(SUM(oi.revenue)/10000000, 2)   AS revenue_crore,
        ROUND(SUM(oi.profit)/10000000, 2)    AS profit_crore,
        ROUND(AVG(oi.profit_margin), 2)      AS avg_margin_pct,
        ROUND(SUM(oi.revenue)/COUNT(DISTINCT o.order_id), 0) AS aov
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY oi.order_year
)
SELECT
    order_year,
    total_orders,
    unique_customers,
    revenue_crore,
    profit_crore,
    avg_margin_pct,
    aov,
    LAG(revenue_crore) OVER (ORDER BY order_year)  AS prev_year_revenue,
    ROUND(
        (revenue_crore - LAG(revenue_crore) OVER (ORDER BY order_year))
        * 100.0 / NULLIF(LAG(revenue_crore) OVER (ORDER BY order_year), 0),
    2) AS yoy_growth_pct
FROM yearly
ORDER BY order_year;


-- 1.2 Category performance with contribution and rank
SELECT
    category,
    COUNT(DISTINCT order_id)                             AS orders,
    ROUND(SUM(revenue)/10000000, 2)                      AS revenue_crore,
    ROUND(SUM(profit)/10000000, 2)                       AS profit_crore,
    ROUND(AVG(profit_margin), 2)                         AS avg_margin,
    ROUND(SUM(revenue)*100.0/SUM(SUM(revenue)) OVER(),2) AS revenue_share_pct,
    RANK() OVER (ORDER BY SUM(revenue) DESC)             AS revenue_rank,
    ROUND(SUM(CASE WHEN return_flag=1 THEN revenue ELSE 0 END)
          *100.0/SUM(revenue), 2)                        AS return_rate_pct
FROM order_items
GROUP BY category
ORDER BY revenue_crore DESC;


-- 1.3 Monthly seasonality analysis
SELECT
    order_month,
    order_year,
    COUNT(DISTINCT order_id)                      AS orders,
    ROUND(SUM(revenue)/10000000, 2)               AS revenue_crore,
    ROUND(AVG(SUM(revenue)/10000000) OVER (
        ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ), 2)                                         AS smoothed_revenue,
    ROUND(SUM(revenue)/10000000
        - LAG(SUM(revenue)/10000000) OVER (
            PARTITION BY EXTRACT(MONTH FROM CAST(order_month||'-01' AS DATE))
            ORDER BY order_year
        ), 2)                                     AS yoy_monthly_change
FROM order_items
GROUP BY order_month, order_year
ORDER BY order_month;


-- 1.4 Top 10 products by revenue with margin analysis
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.rating,
    COUNT(DISTINCT oi.order_id)           AS times_ordered,
    SUM(oi.quantity)                      AS units_sold,
    ROUND(SUM(oi.revenue)/100000, 2)      AS revenue_lakh,
    ROUND(AVG(oi.profit_margin), 2)       AS avg_margin_pct,
    ROUND(AVG(oi.discount_pct), 1)        AS avg_discount,
    RANK() OVER (ORDER BY SUM(oi.revenue) DESC) AS revenue_rank
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.brand, p.rating
ORDER BY revenue_lakh DESC
LIMIT 10;


-- ----------------------------------------------------------------
-- SECTION 2: CUSTOMER BEHAVIOUR AND SEGMENTATION
-- ----------------------------------------------------------------

-- 2.1 RFM Segmentation with full scoring
WITH rfm_raw AS (
    SELECT
        o.customer_id,
        DATEDIFF('day', MAX(CAST(o.order_date AS DATE)),
                         CAST('2024-12-31' AS DATE))  AS recency_days,
        COUNT(DISTINCT o.order_id)                    AS frequency,
        ROUND(SUM(oi.revenue), 0)                     AS monetary
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id
),
rfm_scored AS (
    SELECT
        customer_id, recency_days, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency_days)   AS r_score,
        NTILE(5) OVER (ORDER BY frequency)      AS f_score,
        NTILE(5) OVER (ORDER BY monetary)       AS m_score
    FROM rfm_raw
)
SELECT
    r.customer_id,
    c.customer_name,
    c.state,
    c.customer_type,
    r.recency_days,
    r.frequency,
    r.monetary,
    r.r_score, r.f_score, r.m_score,
    r.r_score + r.f_score + r.m_score          AS rfm_score,
    CASE
        WHEN r.r_score >= 4 AND r.f_score >= 4
         AND r.m_score >= 4                    THEN 'Champions'
        WHEN r.r_score >= 3 AND r.f_score >= 3 THEN 'Loyal Customers'
        WHEN r.r_score >= 4 AND r.f_score <= 2 THEN 'Potential Loyalist'
        WHEN r.r_score >= 4 AND r.f_score  = 1 THEN 'New Customers'
        WHEN r.r_score <= 2 AND r.f_score >= 3
         AND r.m_score >= 3                    THEN 'At Risk'
        WHEN r.r_score <= 1 AND r.f_score <= 1 THEN 'Lost'
        ELSE                                       'Needs Attention'
    END AS rfm_segment
FROM rfm_scored r
JOIN customers c ON r.customer_id = c.customer_id
ORDER BY rfm_score DESC;


-- 2.2 Customer cohort retention analysis
-- Which acquisition month retains customers best?
WITH first_order AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(CAST(order_date AS DATE))) AS cohort_month
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('month', CAST(o.order_date AS DATE)) AS activity_month
    FROM orders o
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id, DATE_TRUNC('month', CAST(o.order_date AS DATE))
)
SELECT
    fo.cohort_month,
    DATEDIFF('month', fo.cohort_month, ma.activity_month) AS months_since_join,
    COUNT(DISTINCT ma.customer_id)                         AS active_customers,
    ROUND(COUNT(DISTINCT ma.customer_id) * 100.0
        / COUNT(DISTINCT fo.customer_id), 2)               AS retention_rate
FROM first_order fo
JOIN monthly_activity ma ON fo.customer_id = ma.customer_id
GROUP BY fo.cohort_month, DATEDIFF('month', fo.cohort_month, ma.activity_month)
ORDER BY fo.cohort_month, months_since_join
LIMIT 60;


-- 2.3 Customer Lifetime Value (CLV) model
WITH customer_orders AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id)          AS total_orders,
        ROUND(SUM(oi.revenue), 0)           AS total_revenue,
        ROUND(AVG(oi.revenue), 0)           AS avg_order_value,
        ROUND(SUM(oi.profit), 0)            AS total_profit,
        MIN(CAST(o.order_date AS DATE))     AS first_order,
        MAX(CAST(o.order_date AS DATE))     AS last_order,
        DATEDIFF('day',
            MIN(CAST(o.order_date AS DATE)),
            MAX(CAST(o.order_date AS DATE))) AS customer_lifespan_days
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id
)
SELECT
    co.customer_id,
    c.customer_name,
    c.customer_type,
    c.state,
    c.is_prime_member,
    co.total_orders,
    co.total_revenue,
    co.avg_order_value,
    co.total_profit,
    co.customer_lifespan_days,
    -- Predicted CLV = AOV x purchase frequency x expected lifespan
    ROUND(co.avg_order_value
        * (co.total_orders / NULLIF(co.customer_lifespan_days/30.0, 0))
        * 24, 0)                            AS predicted_clv_2yr,
    PERCENT_RANK() OVER (ORDER BY co.total_revenue) * 100 AS revenue_percentile,
    CASE
        WHEN PERCENT_RANK() OVER (ORDER BY co.total_revenue) >= 0.90 THEN 'Top 10%'
        WHEN PERCENT_RANK() OVER (ORDER BY co.total_revenue) >= 0.75 THEN 'Top 25%'
        WHEN PERCENT_RANK() OVER (ORDER BY co.total_revenue) >= 0.50 THEN 'Top 50%'
        ELSE 'Bottom 50%'
    END AS clv_tier
FROM customer_orders co
JOIN customers c ON co.customer_id = c.customer_id
ORDER BY predicted_clv_2yr DESC
LIMIT 20;


-- ----------------------------------------------------------------
-- SECTION 3: STATISTICAL ANALYSIS
-- ----------------------------------------------------------------

-- 3.1 Descriptive statistics by category
-- Mean, Median, Std Dev, Variance, Skewness
SELECT
    category,
    COUNT(*)                          AS n,
    ROUND(AVG(revenue), 2)            AS mean_revenue,
    ROUND(MEDIAN(revenue), 2)         AS median_revenue,
    ROUND(STDDEV(revenue), 2)         AS std_dev,
    ROUND(VARIANCE(revenue), 2)       AS variance,
    ROUND(MIN(revenue), 2)            AS min_revenue,
    ROUND(MAX(revenue), 2)            AS max_revenue,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue), 2) AS q1,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue), 2) AS q3,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY revenue)
        - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY revenue), 2) AS iqr,
    -- Coefficient of variation (lower = more consistent)
    ROUND(STDDEV(revenue)/NULLIF(AVG(revenue),0)*100, 2)            AS cv_pct
FROM order_items
WHERE return_flag = 0
GROUP BY category
ORDER BY mean_revenue DESC;


-- 3.2 Discount elasticity analysis
-- Does more discount lead to more revenue? Statistical relationship
SELECT
    CASE
        WHEN discount_pct = 0         THEN '0% - No Discount'
        WHEN discount_pct <= 10       THEN '1-10%'
        WHEN discount_pct <= 20       THEN '11-20%'
        WHEN discount_pct <= 30       THEN '21-30%'
        WHEN discount_pct <= 40       THEN '31-40%'
        ELSE                               '40%+'
    END AS discount_bracket,
    COUNT(*)                          AS items_sold,
    ROUND(AVG(quantity), 2)           AS avg_quantity,
    ROUND(AVG(revenue), 0)            AS avg_revenue,
    ROUND(AVG(profit_margin), 2)      AS avg_margin_pct,
    ROUND(SUM(revenue)/10000000, 2)   AS total_revenue_crore,
    -- Conversion proxy: units per order
    ROUND(SUM(quantity)/COUNT(DISTINCT order_id), 2) AS units_per_order
FROM order_items
GROUP BY 1
ORDER BY discount_bracket;


-- 3.3 Day-of-week and hour analysis (peak demand)
SELECT
    order_day_of_week,
    order_hour,
    COUNT(*)                             AS orders,
    ROUND(SUM(oi.revenue)/10000000, 3)  AS revenue_crore,
    ROUND(AVG(oi.revenue), 0)           AS avg_order_value,
    RANK() OVER (ORDER BY COUNT(*) DESC) AS demand_rank
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
GROUP BY order_day_of_week, order_hour
ORDER BY orders DESC
LIMIT 20;


-- 3.4 A/B style payment method analysis
-- Does payment method affect average order value?
SELECT
    payment_method,
    COUNT(DISTINCT o.order_id)           AS orders,
    ROUND(AVG(oi.revenue), 0)            AS avg_order_value,
    ROUND(STDDEV(oi.revenue), 0)         AS std_dev_aov,
    ROUND(SUM(oi.revenue)/10000000, 2)   AS total_revenue_crore,
    ROUND(AVG(oi.profit_margin), 2)      AS avg_margin,
    -- Z-score vs overall mean
    ROUND((AVG(oi.revenue) - AVG(AVG(oi.revenue)) OVER())
        / NULLIF(STDDEV(AVG(oi.revenue)) OVER(), 0), 2) AS z_score_vs_avg,
    ROUND(COUNT(DISTINCT o.order_id)*100.0
        / SUM(COUNT(DISTINCT o.order_id)) OVER(), 2)    AS order_share_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
GROUP BY payment_method
ORDER BY avg_order_value DESC;


-- ----------------------------------------------------------------
-- SECTION 4: RETURN ANALYSIS
-- ----------------------------------------------------------------

-- 4.1 Return rate by category and reason
SELECT
    r.category,
    r.return_reason,
    COUNT(*)                                           AS returns,
    ROUND(SUM(r.return_amount)/100000, 2)             AS return_value_lakh,
    ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER
        (PARTITION BY r.category), 2)                 AS pct_within_category,
    ROUND(AVG(r.refund_days), 1)                      AS avg_refund_days
FROM returns r
GROUP BY r.category, r.return_reason
ORDER BY r.category, returns DESC;


-- 4.2 Return impact on profitability
WITH category_sales AS (
    SELECT category,
           SUM(revenue)       AS gross_revenue,
           SUM(profit)        AS gross_profit
    FROM order_items
    GROUP BY category
),
category_returns AS (
    SELECT category,
           SUM(return_amount) AS return_value,
           COUNT(*)           AS return_count
    FROM returns
    GROUP BY category
)
SELECT
    cs.category,
    ROUND(cs.gross_revenue/10000000, 2)  AS gross_revenue_crore,
    ROUND(cr.return_value/10000000, 2)   AS return_value_crore,
    ROUND((cs.gross_revenue - cr.return_value)/10000000, 2) AS net_revenue_crore,
    ROUND(cr.return_value*100.0/cs.gross_revenue, 2)        AS return_rate_pct,
    ROUND(cs.gross_profit/10000000, 2)   AS gross_profit_crore,
    cr.return_count
FROM category_sales cs
LEFT JOIN category_returns cr ON cs.category = cr.category
ORDER BY return_rate_pct DESC;


-- ----------------------------------------------------------------
-- SECTION 5: MARKETING AND CAMPAIGN ANALYTICS
-- ----------------------------------------------------------------

-- 5.1 Campaign ROI analysis
SELECT
    campaign_name,
    channel,
    target_segment,
    duration_days,
    discount_offered,
    ROUND(budget/100000, 1)                     AS budget_lakh,
    ROUND(revenue_generated/100000, 1)          AS revenue_lakh,
    orders_generated,
    new_customers,
    roas,
    ROUND(revenue_generated/NULLIF(budget,0), 2) AS roi_multiplier,
    ROUND(revenue_generated/NULLIF(orders_generated,0), 0) AS revenue_per_order,
    ROUND(budget/NULLIF(new_customers,0), 0)     AS cac,
    RANK() OVER (ORDER BY roas DESC)             AS roas_rank
FROM campaigns
ORDER BY roas DESC;


-- 5.2 Channel effectiveness comparison
SELECT
    channel,
    COUNT(*)                                    AS campaigns_run,
    ROUND(AVG(roas), 2)                         AS avg_roas,
    ROUND(SUM(revenue_generated)/SUM(budget),2) AS overall_roi,
    SUM(new_customers)                          AS total_new_customers,
    ROUND(SUM(budget)/SUM(new_customers), 0)    AS avg_cac,
    ROUND(AVG(duration_days), 1)                AS avg_duration
FROM campaigns
GROUP BY channel
ORDER BY avg_roas DESC;


-- ----------------------------------------------------------------
-- SECTION 6: ADVANCED WINDOW FUNCTION ANALYTICS
-- ----------------------------------------------------------------

-- 6.1 Running total revenue and 30-day moving average
WITH daily AS (
    SELECT
        CAST(order_date AS DATE)    AS dt,
        SUM(revenue)                AS daily_revenue,
        COUNT(DISTINCT order_id)    AS daily_orders
    FROM order_items
    GROUP BY CAST(order_date AS DATE)
)
SELECT
    dt,
    daily_revenue,
    daily_orders,
    ROUND(SUM(daily_revenue) OVER (ORDER BY dt), 0)          AS running_total,
    ROUND(AVG(daily_revenue) OVER (
        ORDER BY dt ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 0)                                                     AS moving_avg_30d,
    ROUND(daily_revenue - LAG(daily_revenue) OVER
        (ORDER BY dt), 0)                                     AS day_over_day_change
FROM daily
ORDER BY dt
LIMIT 60;


-- 6.2 Brand market share within category using PARTITION
SELECT
    category,
    brand,
    COUNT(DISTINCT order_id)                         AS orders,
    ROUND(SUM(revenue)/10000000, 3)                  AS revenue_crore,
    ROUND(SUM(revenue)*100.0
        / SUM(SUM(revenue)) OVER (PARTITION BY category), 2) AS category_share_pct,
    RANK() OVER (PARTITION BY category ORDER BY SUM(revenue) DESC) AS brand_rank
FROM order_items
GROUP BY category, brand
QUALIFY RANK() OVER (PARTITION BY category ORDER BY SUM(revenue) DESC) <= 3
ORDER BY category, brand_rank;


-- 6.3 State-wise performance with percentile ranking
SELECT
    state,
    COUNT(DISTINCT customer_id)                    AS customers,
    COUNT(DISTINCT order_id)                       AS orders,
    ROUND(SUM(revenue)/10000000, 2)                AS revenue_crore,
    ROUND(AVG(revenue), 0)                         AS avg_order_value,
    ROUND(SUM(revenue)/COUNT(DISTINCT customer_id),0) AS revenue_per_customer,
    PERCENT_RANK() OVER (ORDER BY SUM(revenue))*100   AS revenue_percentile,
    DENSE_RANK() OVER (ORDER BY SUM(revenue) DESC)    AS state_rank
FROM order_items
GROUP BY state
ORDER BY revenue_crore DESC;


-- 6.4 Executive KPI summary
SELECT
    COUNT(DISTINCT o.customer_id)              AS total_customers,
    COUNT(DISTINCT o.order_id)                 AS total_orders,
    ROUND(SUM(oi.revenue)/10000000, 2)         AS total_revenue_crore,
    ROUND(SUM(oi.profit)/10000000, 2)          AS total_profit_crore,
    ROUND(AVG(oi.profit_margin), 2)            AS avg_margin_pct,
    ROUND(AVG(oi.revenue), 0)                  AS avg_order_value,
    (SELECT COUNT(*) FROM returns)             AS total_returns,
    ROUND((SELECT COUNT(*) FROM returns)*100.0
        / COUNT(DISTINCT o.order_id), 2)       AS return_rate_pct,
    (SELECT ROUND(AVG(roas),2) FROM campaigns) AS avg_campaign_roas
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered';
