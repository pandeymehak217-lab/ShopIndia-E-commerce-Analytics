# ShopIndia E-commerce Sales Analytics

**Author:** Mehak Pandey
**Email:** pandeymehak.217@gmail.com
**Tools:** SQL, Python, Statistics, Excel
**Dataset:** 6 tables | 40,000 orders | 77,000 line items | 2020-2024

---

## Project Overview

ShopIndia is a simulated Indian e-commerce platform analytics project covering
end-to-end sales analysis from raw transaction data to executive dashboards.
The project demonstrates skills that are directly tested in data analyst interviews
at companies like Flipkart, Amazon India, Nykaa, Meesho, and Reliance Retail.

The analysis covers revenue performance, customer segmentation using RFM modelling,
statistical hypothesis testing, return analysis, campaign ROI measurement

---

## Dataset Schema

| Table | Rows | Description |
|-------|------|-------------|
| customers | 5,000 | Demographics, segment, acquisition source |
| products | 800 | Category, brand, cost, MRP, discount |
| orders | 40,000 | Order status, payment, shipping, date |
| order_items | 77,192 | Revenue, profit, margin per line item |
| returns | 7,600 | Return reason, refund status, value |
| campaigns | 20 | Budget, ROAS, channel, new customers |

Total Revenue: Rs 134.5 Crore | Avg Margin: 42.9% | Return Rate: 19%

---

## Project Structure

```
ecommerce-analytics/
|
|-- data/
|   |-- customers.csv
|   |-- products.csv
|   |-- orders.csv
|   |-- order_items.csv
|   |-- returns.csv
|   |-- campaigns.csv
|
|-- sql/
|   |-- ecommerce_analysis.sql    (25+ queries, 6 sections)
|
|-- python/
|   |-- analysis.py               (stats, charts, Excel report)
|
|-- outputs/
|   |-- ecommerce_dashboard.png   (8-panel matplotlib dashboard)
|   |-- ShopIndia_Analytics_Report.xlsx  (5-sheet Excel report)
|
|-- generate_data.py
|-- run_queries.py
|-- README.md
```

---

## SQL Analysis (25+ Queries across 6 Sections)

**Section 1 - Sales Performance**
- Year-wise revenue with YoY growth using LAG()
- Category performance with revenue share and RANK()
- Monthly seasonality with 5-month smoothed average
- Top 10 products by revenue and margin

**Section 2 - Customer Behaviour**
- Full RFM segmentation using NTILE(5) window functions
- Cohort retention analysis month by month
- Customer Lifetime Value prediction model using PERCENT_RANK()

**Section 3 - Statistical Analysis**
- Descriptive statistics per category: mean, median, std dev, IQR, CV
- Discount elasticity: revenue and margin by discount bracket
- Day-of-week and hour demand analysis
- Payment method A/B style comparison with z-score

**Section 4 - Return Analysis**
- Return rate by category and reason with PARTITION BY
- Return impact on net revenue and profitability

**Section 5 - Marketing Analytics**
- Campaign ROI: ROAS, CAC, revenue per order
- Channel effectiveness: avg ROAS and cost per acquisition

**Section 6 - Advanced Window Functions**
- 30-day moving average revenue using ROWS BETWEEN
- Brand market share within category using QUALIFY
- State percentile ranking using PERCENT_RANK() and DENSE_RANK()
- Executive KPI summary single query

---

## Statistical Analysis (Python + SciPy)

**Pearson Correlation**
Discount percentage vs profit margin: r = -0.159, p < 0.0001
Conclusion: Higher discounts significantly reduce profit margins.
Every 10% increase in discount reduces margin by approximately 1.6 percentage points.

**One-Way ANOVA**
Revenue variation across product categories: F = 426.25, p < 0.000001
Conclusion: Revenue differs significantly across categories.
Electronics and Fashion drive disproportionately higher order values.

**Descriptive Statistics Applied**
Mean, Median, Standard Deviation, Variance, IQR, Coefficient of Variation
computed per category to understand revenue consistency and spread.


---

## Excel Report (5 Sheets)

Sheet 1 - Executive Summary: KPI cards + yearly performance table + dashboard image
Sheet 2 - Category Analytics: Revenue, margin, return analysis
Sheet 3 - Customer Analytics: RFM segments, state performance, payment method
Sheet 4 - Marketing Analytics: Campaign ROI + channel effectiveness
Sheet 5 - Statistical Analysis: Descriptive stats + test results with color coding

---

## Key Business Findings

Electronics has the highest revenue at Rs 23.4 Crore but carries a 21.3% return rate,
which is the highest across all categories. This suggests quality or expectation issues
that need product team attention.

Champions and Loyal customer segments together represent 35% of customers
but contribute over 60% of revenue. Retaining these two segments should be
the primary focus of CRM campaigns.

Campaigns run on Social Media channels delivered the highest average ROAS at 5.8x,
outperforming Email (4.2x) and Google Ads (3.9x). However, Google Ads acquired
the most new customers per campaign.

Higher discounts above 30% show a sharp decline in profit margins without
a proportional increase in order volume. The optimal discount range for
balancing volume and profitability is 10-20%.

EMI payment users have the highest average order value at Rs 8,240,
making them the most valuable segment for electronics and high-ticket categories.

---

## How to Run

```bash
# Install dependencies
pip3 install duckdb pandas numpy matplotlib scipy xlsxwriter

# Generate dataset
python3 generate_data.py

# Run SQL queries
python3 run_queries.py

# Run Python analysis and generate outputs
python3 python/analysis.py
```

For Tableau: import CSVs from data/ folder and follow tableau/TABLEAU_GUIDE.md

---

## SQL Concepts Demonstrated

CTEs, LAG() and LEAD(), NTILE() for RFM scoring, PERCENT_RANK(),
DENSE_RANK() and RANK() with PARTITION BY, QUALIFY clause for top-N per group,
running totals with SUM() OVER, rolling averages with ROWS BETWEEN,
PERCENTILE_CONT for median and quartiles, multi-table joins across 6 tables,
CASE-based pivoting, conditional aggregation, statistical z-score in SQL

---

## About

Mehak Pandey - Fresher Data Analyst
Email: pandeymehak.217@gmail.com


