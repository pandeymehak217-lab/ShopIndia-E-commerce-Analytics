# ShopIndia E-commerce Sales Analytics

I wanted to build something that combined SQL with actual statistics.
Not just GROUP BY and window functions but real hypothesis testing —
the kind of thing that comes up when you work with a product or marketing
team and they ask you to prove whether something is actually working or
just looks like it is working.

E-commerce felt like the right domain because the data is rich and the
business questions are straightforward. Everyone understands what revenue,
margin, and return rate mean so it is easy to explain what you found.

---

## What I Built

End-to-end sales analysis on 40,000 orders and 77,000 line items across
6 tables. SQL analysis with 25+ queries, Python for statistical testing
and charts, and a 5-sheet Excel report.

The statistical testing part is what I am most proud of in this project.
I ran Pearson correlation, one-way ANOVA, and descriptive statistics
using SciPy in Python and put the results in both the dashboard and
the Excel report with proper interpretation.

---

## Dataset

| Table | Rows | What it contains |
|-------|------|-----------------|
| customers | 5,000 | Demographics, acquisition source, segment |
| products | 800 | Category, brand, MRP, cost, discount |
| orders | 40,000 | Status, payment method, shipping, date |
| order_items | 77,192 | Revenue, profit, margin per line item |
| returns | 7,600 | Return reason, refund status, value |
| campaigns | 20 | Budget, ROAS, channel, new customers |

Total Revenue: Rs 134.5 Crore
Avg Margin: 42.9%
Return Rate: 19%

---

## Folder Structure

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
|   |-- ecommerce_analysis.sql
|
|-- python/
|   |-- analysis.py
|
|-- tableau/
|   |-- TABLEAU_GUIDE.md
|
|-- outputs/
|   |-- ecommerce_dashboard.png
|   |-- ShopIndia_Analytics_Report.xlsx
|
|-- generate_data.py
|-- run_queries.py
|-- README.md
```

---

## SQL Work

Six sections covering different parts of the analysis.

Sales performance covers year-over-year growth using LAG, category
revenue with share percentage using window functions, monthly
seasonality with a 5-month smoothed average, and top 10 products
by revenue and margin.

Customer behaviour has the full RFM model using NTILE(5), cohort
retention analysis tracking users month by month from their first
order, and a CLV prediction model using PERCENT_RANK to tier customers.

Statistical analysis in SQL includes descriptive stats per category
using PERCENTILE_CONT for median and quartile calculations, discount
elasticity analysis, day-of-week demand patterns, and a z-score
comparison across payment methods.

Return analysis uses PARTITION BY to calculate return rates within
categories and measures the impact on net revenue after accounting
for refunds.

Marketing analytics covers campaign ROAS, CAC per channel, and
revenue per order by campaign. The QUALIFY clause for top-N brand
per category was a new pattern I learned while writing this.

---

## Statistical Tests

This is the part that goes beyond standard SQL portfolio projects.

Pearson correlation between discount percentage and profit margin
came out at r = -0.159 with p less than 0.0001. The relationship
is statistically significant. Higher discounts hurt margins and
the data confirms it clearly.

One-way ANOVA testing whether revenue differs across product
categories gave F = 426.25 with p essentially zero. Revenue
is not the same across categories. Electronics and Fashion drive
significantly higher order values than Grocery and Books.

I also calculated mean, median, standard deviation, IQR, and
coefficient of variation per category to understand which
categories are consistent versus which ones have high variance.

---

## What I Found

Electronics has the highest revenue at Rs 23.4 Crore but also
the highest return rate at 21.3 percent. Something is going wrong
with product quality or customer expectations in that category.

Social Media campaigns had the best ROAS at 5.8x. Google Ads
had lower ROAS but acquired the most new customers per campaign.
The right channel depends on whether the goal is efficiency
or growth.

Discounts above 30 percent hurt margins significantly without
a proportional increase in order volume. The 10 to 20 percent
bracket is where volume and margin balance best in this dataset.

EMI payment users have the highest average order value at Rs 8,240.
This makes sense — people use EMI specifically for high-ticket items.

---

## How To Run

```bash
pip3 install duckdb pandas numpy matplotlib scipy xlsxwriter
python3 generate_data.py
python3 run_queries.py
python3 python/analysis.py
```

For Tableau setup follow tableau/TABLEAU_GUIDE.md. It has the
calculated fields and join logic written out.

---

## What I Would Do Differently

The cohort retention analysis is the weakest query in the project.
I grouped by month of first order but the retention calculation
is simplified. A proper cohort analysis should track whether each
user made a purchase in month N after joining, not just whether
they were active at some point.

The campaign data only has 20 rows which is not enough to draw
strong conclusions. I want to expand this to 200+ campaigns
across different time periods so the channel comparison is
more meaningful.

---

## What I Learned

Running actual statistical tests on data I generated and interpreted
myself made the numbers feel real. Knowing that the discount-margin
correlation is statistically significant at p less than 0.0001 is
more satisfying than just eyeballing a bar chart.

ANOVA was something I had learned in college statistics but never
applied to real data. Using it to confirm that category differences
in revenue are not random felt like connecting two things I had
learned separately.

The QUALIFY clause is something most SQL tutorials do not cover.
It filters after window functions run which means you can do
top-N per group in a single query without a subquery.
I use it regularly now.

---

Mehak Pandey
pandeymehak.217@gmail.com
