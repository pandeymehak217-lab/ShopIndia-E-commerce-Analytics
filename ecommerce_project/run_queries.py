"""
ShopIndia E-commerce — Run SQL Queries
Author: Mehak Pandey | pandeymehak.217@gmail.com
"""
import duckdb, pandas as pd

BASE = '/home/claude/ecommerce_project/data'
con  = duckdb.connect()
for t in ['customers','products','orders','order_items','returns','campaigns']:
    con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{BASE}/{t}.csv')")

queries = {
"1. Yearly Revenue with YoY Growth": """
    WITH y AS (
        SELECT oi.order_year,
               COUNT(DISTINCT o.order_id) AS orders,
               ROUND(SUM(oi.revenue)/10000000,2) AS revenue_crore,
               ROUND(AVG(oi.profit_margin),2) AS avg_margin
        FROM order_items oi JOIN orders o ON oi.order_id=o.order_id
        WHERE o.order_status='Delivered' GROUP BY oi.order_year
    )
    SELECT *, ROUND((revenue_crore-LAG(revenue_crore) OVER (ORDER BY order_year))
              *100.0/NULLIF(LAG(revenue_crore) OVER (ORDER BY order_year),0),2) AS yoy_growth
    FROM y ORDER BY order_year
""",
"2. Category Performance with Rank": """
    SELECT category,
           ROUND(SUM(revenue)/10000000,2) AS revenue_crore,
           ROUND(AVG(profit_margin),2) AS avg_margin,
           ROUND(SUM(revenue)*100.0/SUM(SUM(revenue)) OVER(),2) AS share_pct,
           RANK() OVER (ORDER BY SUM(revenue) DESC) AS rank
    FROM order_items GROUP BY category ORDER BY revenue_crore DESC
""",
"3. RFM Segments": """
    WITH r AS (
        SELECT o.customer_id,
               COUNT(DISTINCT o.order_id) AS freq,
               SUM(oi.revenue) AS monetary,
               NTILE(5) OVER (ORDER BY COUNT(DISTINCT o.order_id)) AS f,
               NTILE(5) OVER (ORDER BY SUM(oi.revenue)) AS m
        FROM orders o JOIN order_items oi ON o.order_id=oi.order_id
        WHERE o.order_status='Delivered' GROUP BY o.customer_id
    )
    SELECT CASE WHEN f>=4 AND m>=4 THEN 'Champions'
                WHEN f>=3 AND m>=3 THEN 'Loyal'
                WHEN f>=4 AND m<=2 THEN 'Potential'
                WHEN f<=2 AND m>=3 THEN 'At Risk'
                WHEN f<=1 AND m<=1 THEN 'Lost'
                ELSE 'Needs Attention' END AS segment,
           COUNT(*) AS customers,
           ROUND(AVG(monetary),0) AS avg_spend
    FROM r GROUP BY 1 ORDER BY customers DESC
""",
"4. Discount Elasticity": """
    SELECT CASE WHEN discount_pct=0 THEN 'No Discount'
                WHEN discount_pct<=10 THEN '1-10%'
                WHEN discount_pct<=20 THEN '11-20%'
                WHEN discount_pct<=30 THEN '21-30%'
                WHEN discount_pct<=40 THEN '31-40%'
                ELSE '40%+' END AS bracket,
           ROUND(AVG(profit_margin),2) AS avg_margin,
           ROUND(SUM(revenue)/10000000,2) AS revenue_crore,
           COUNT(*) AS items
    FROM order_items GROUP BY 1 ORDER BY revenue_crore DESC
""",
"5. Campaign ROAS Ranking": """
    SELECT campaign_name, channel,
           ROUND(budget/100000,1) AS budget_lakh,
           ROUND(revenue_generated/100000,1) AS revenue_lakh,
           roas, new_customers,
           ROUND(budget/NULLIF(new_customers,0),0) AS cac,
           RANK() OVER (ORDER BY roas DESC) AS roas_rank
    FROM campaigns ORDER BY roas DESC
""",
"6. Executive KPI": """
    SELECT COUNT(DISTINCT o.customer_id) AS customers,
           COUNT(DISTINCT o.order_id) AS orders,
           ROUND(SUM(oi.revenue)/10000000,2) AS revenue_crore,
           ROUND(SUM(oi.profit)/10000000,2) AS profit_crore,
           ROUND(AVG(oi.profit_margin),2) AS avg_margin,
           ROUND(AVG(oi.revenue),0) AS aov,
           (SELECT COUNT(*) FROM returns) AS total_returns
    FROM orders o JOIN order_items oi ON o.order_id=oi.order_id
    WHERE o.order_status='Delivered'
""",
}

print("="*60)
print("  ShopIndia E-commerce — SQL Results")
print("  Author: Mehak Pandey | pandeymehak.217@gmail.com")
print("="*60)

for name, sql in queries.items():
    print(f"\n{'─'*60}\n  {name}\n{'─'*60}")
    print(con.execute(sql).df().to_string(index=False))

print("\n" + "="*60)
print("  All queries passed.")
print("="*60)
con.close()
