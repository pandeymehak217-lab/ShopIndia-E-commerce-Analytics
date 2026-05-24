"""
ShopIndia E-commerce Analytics
Author : Mehak Pandey
Email  : pandeymehak.217@gmail.com
Tools  : Python, Pandas, Matplotlib, SciPy, xlsxwriter
"""
import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = '/home/claude/ecommerce_project/data'
OUT  = '/home/claude/ecommerce_project/outputs'

con = duckdb.connect()
for t in ['customers','products','orders','order_items','returns','campaigns']:
    con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv_auto('{BASE}/{t}.csv')")
print("Data loaded.")

def q(sql): return con.execute(sql).df()

# ── Queries ────────────────────────────────────────────────
yearly = q("""
    SELECT oi.order_year,
           COUNT(DISTINCT o.order_id) AS orders,
           ROUND(SUM(oi.revenue)/10000000,2) AS revenue_crore,
           ROUND(SUM(oi.profit)/10000000,2) AS profit_crore,
           ROUND(AVG(oi.profit_margin),2) AS avg_margin,
           ROUND(AVG(oi.revenue),0) AS aov
    FROM order_items oi JOIN orders o ON oi.order_id=o.order_id
    WHERE o.order_status='Delivered' GROUP BY oi.order_year ORDER BY 1
""")

category_perf = q("""
    SELECT category,
           ROUND(SUM(revenue)/10000000,2) AS revenue_crore,
           ROUND(SUM(profit)/10000000,2) AS profit_crore,
           ROUND(AVG(profit_margin),2) AS avg_margin,
           ROUND(SUM(CASE WHEN return_flag=1 THEN revenue ELSE 0 END)*100.0/SUM(revenue),2) AS return_rate
    FROM order_items GROUP BY category ORDER BY revenue_crore DESC
""")

payment_analysis = q("""
    SELECT payment_method,
           COUNT(DISTINCT o.order_id) AS orders,
           ROUND(AVG(oi.revenue),0) AS avg_order_value,
           ROUND(SUM(oi.revenue)/10000000,2) AS revenue_crore
    FROM orders o JOIN order_items oi ON o.order_id=oi.order_id
    WHERE o.order_status='Delivered' GROUP BY payment_method ORDER BY orders DESC
""")

state_perf = q("""
    SELECT state,
           COUNT(DISTINCT order_id) AS orders,
           ROUND(SUM(revenue)/10000000,2) AS revenue_crore,
           ROUND(AVG(revenue),0) AS aov
    FROM order_items GROUP BY state ORDER BY revenue_crore DESC LIMIT 10
""")

discount_analysis = q("""
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
""")

campaign_roi = q("""
    SELECT campaign_name, channel, roas,
           ROUND(budget/100000,1) AS budget_lakh,
           ROUND(revenue_generated/100000,1) AS revenue_lakh
    FROM campaigns ORDER BY roas DESC LIMIT 10
""")

rfm = q("""
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
""")

return_analysis = q("""
    SELECT category, return_reason, COUNT(*) AS returns,
           ROUND(SUM(return_amount)/100000,2) AS value_lakh
    FROM returns GROUP BY category, return_reason ORDER BY returns DESC LIMIT 15
""")

kpi = q("""
    SELECT COUNT(DISTINCT o.customer_id) AS customers,
           COUNT(DISTINCT o.order_id) AS orders,
           ROUND(SUM(oi.revenue)/10000000,2) AS revenue_crore,
           ROUND(SUM(oi.profit)/10000000,2) AS profit_crore,
           ROUND(AVG(oi.profit_margin),2) AS avg_margin,
           ROUND(AVG(oi.revenue),0) AS aov
    FROM orders o JOIN order_items oi ON o.order_id=oi.order_id
    WHERE o.order_status='Delivered'
""")

print("Queries done.")

# ── STATISTICAL TESTS ──────────────────────────────────────
raw = q("SELECT revenue, discount_pct, profit_margin, category FROM order_items WHERE return_flag=0 LIMIT 5000")

# Pearson correlation: discount vs margin
corr_r, corr_p = stats.pearsonr(raw['discount_pct'], raw['profit_margin'])
print(f"Discount vs Margin correlation: r={corr_r:.3f}, p={corr_p:.4f}")

# One-way ANOVA: revenue differs by category?
groups = [raw[raw['category']==c]['revenue'].dropna().values for c in raw['category'].unique()]
f_stat, anova_p = stats.f_oneway(*groups)
print(f"ANOVA (revenue by category): F={f_stat:.2f}, p={anova_p:.6f}")

# ── MATPLOTLIB DASHBOARD ──────────────────────────────────
fig = plt.figure(figsize=(22, 26), facecolor='#FFFFFF')
gs  = gridspec.GridSpec(4, 3, figure=fig, hspace=0.48, wspace=0.38)

RED    = '#C0392B'
YELLOW = '#F39C12'
GREEN  = '#27AE60'
DARK   = '#2C3E50'
LIGHT  = '#F5F6FA'

PALETTE = [RED, YELLOW, GREEN, '#2980B9','#8E44AD','#1ABC9C','#E74C3C','#F1C40F','#16A085','#D35400']

# Row 0 — KPI banner
ax0 = fig.add_subplot(gs[0,:])
ax0.set_facecolor(DARK)
ax0.set_xlim(0,10); ax0.set_ylim(0,1); ax0.axis('off')
ax0.text(5, 0.85, 'ShopIndia E-commerce — Analytics Dashboard 2020-2024',
         ha='center', fontsize=15, fontweight='bold', color='white',
         fontfamily='DejaVu Sans')
kpi_items = [
    (f"Rs {kpi['revenue_crore'].iloc[0]}Cr", 'Total Revenue'),
    (f"Rs {kpi['profit_crore'].iloc[0]}Cr",  'Total Profit'),
    (f"{kpi['avg_margin'].iloc[0]}%",         'Avg Margin'),
    (f"{kpi['customers'].iloc[0]:,}",          'Customers'),
    (f"{kpi['orders'].iloc[0]:,}",             'Orders'),
    (f"Rs {kpi['aov'].iloc[0]:,}",             'Avg Order Value'),
]
for i,(val,lbl) in enumerate(kpi_items):
    x = 0.85 + i*1.38
    ax0.text(x, 0.50, val, ha='center', fontsize=12, fontweight='bold',
             color=YELLOW, fontfamily='DejaVu Sans')
    ax0.text(x, 0.22, lbl, ha='center', fontsize=8, color='#BDC3C7',
             fontfamily='DejaVu Sans')

# Row 1 — Yearly trend, Category revenue, RFM
ax1 = fig.add_subplot(gs[1,0])
ax1.set_facecolor(LIGHT)
bars = ax1.bar(yearly['order_year'].astype(str), yearly['revenue_crore'],
               color=[RED,YELLOW,GREEN,RED,YELLOW], edgecolor='white', linewidth=0.5)
ax1_t = ax1.twinx()
ax1_t.plot(yearly['order_year'].astype(str), yearly['avg_margin'],
           color=DARK, marker='o', linewidth=2, markersize=5, label='Margin %')
ax1.set_title('Yearly Revenue & Margin', fontweight='bold', fontsize=10, color=DARK)
ax1.set_ylabel('Revenue (Rs Crore)', color=DARK, fontsize=8)
ax1_t.set_ylabel('Avg Margin %', color=DARK, fontsize=8)
for bar in bars:
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
             f'{bar.get_height():.1f}', ha='center', fontsize=7, color=DARK)

ax2 = fig.add_subplot(gs[1,1])
ax2.set_facecolor(LIGHT)
colors2 = [RED if m < 40 else YELLOW if m < 50 else GREEN for m in category_perf['avg_margin']]
ax2.barh(category_perf['category'], category_perf['revenue_crore'],
         color=colors2, edgecolor='white')
ax2.set_title('Revenue by Category (Rs Crore)', fontweight='bold', fontsize=10, color=DARK)
ax2.set_xlabel('Rs Crore', fontsize=8)
for i,(v,r) in enumerate(zip(category_perf['revenue_crore'], category_perf['return_rate'])):
    ax2.text(v+0.1, i, f'Ret:{r}%', va='center', fontsize=6.5, color=RED)

ax3 = fig.add_subplot(gs[1,2])
ax3.set_facecolor(LIGHT)
rfm_colors = [RED,GREEN,YELLOW,'#2980B9','#8E44AD','#1ABC9C']
wedges, texts, pcts = ax3.pie(rfm['customers'], labels=rfm['segment'],
                               autopct='%1.1f%%', colors=rfm_colors[:len(rfm)],
                               pctdistance=0.78, textprops={'fontsize':7})
ax3.set_title('RFM Customer Segments', fontweight='bold', fontsize=10, color=DARK)

# Row 2 — Discount analysis, Payment method, State performance
ax4 = fig.add_subplot(gs[2,0])
ax4.set_facecolor(LIGHT)
d_colors = [GREEN if m >= 45 else YELLOW if m >= 35 else RED
            for m in discount_analysis['avg_margin']]
ax4.bar(discount_analysis['bracket'], discount_analysis['avg_margin'],
        color=d_colors, edgecolor='white')
ax4.axhline(y=discount_analysis['avg_margin'].mean(), color=DARK,
            linestyle='--', linewidth=1.2, label='Average')
ax4.set_title('Discount Bracket vs Profit Margin', fontweight='bold', fontsize=10, color=DARK)
ax4.set_ylabel('Avg Margin %', fontsize=8)
ax4.set_xlabel('Discount Bracket', fontsize=8)
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=25, ha='right', fontsize=7)
ax4.legend(fontsize=7)

ax5 = fig.add_subplot(gs[2,1])
ax5.set_facecolor(LIGHT)
p_colors = [GREEN,RED,YELLOW,'#2980B9','#8E44AD','#1ABC9C','#D35400']
bars5 = ax5.bar(payment_analysis['payment_method'], payment_analysis['avg_order_value'],
                color=p_colors[:len(payment_analysis)], edgecolor='white')
ax5.set_title('Payment Method vs Avg Order Value', fontweight='bold', fontsize=10, color=DARK)
ax5.set_ylabel('Avg Order Value (Rs)', fontsize=8)
plt.setp(ax5.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=7)
for bar in bars5:
    ax5.text(bar.get_x()+bar.get_width()/2, bar.get_height()+10,
             f'Rs{int(bar.get_height()):,}', ha='center', fontsize=6.5, color=DARK)

ax6 = fig.add_subplot(gs[2,2])
ax6.set_facecolor(LIGHT)
state_colors = [GREEN if r >= state_perf['revenue_crore'].median() else RED
                for r in state_perf['revenue_crore']]
ax6.barh(state_perf['state'], state_perf['revenue_crore'],
         color=state_colors, edgecolor='white')
ax6.set_title('Top 10 States by Revenue', fontweight='bold', fontsize=10, color=DARK)
ax6.set_xlabel('Rs Crore', fontsize=8)

# Row 3 — Campaign ROI, Statistical notes, Return analysis
ax7 = fig.add_subplot(gs[3,0])
ax7.set_facecolor(LIGHT)
bar_colors7 = [GREEN if r >= 5 else YELLOW if r >= 3 else RED
               for r in campaign_roi['roas']]
bars7 = ax7.bar(range(len(campaign_roi)), campaign_roi['roas'],
                color=bar_colors7, edgecolor='white')
ax7.set_xticks(range(len(campaign_roi)))
ax7.set_xticklabels([n[:12] for n in campaign_roi['campaign_name']],
                    rotation=40, ha='right', fontsize=6.5)
ax7.axhline(y=campaign_roi['roas'].mean(), color=DARK,
            linestyle='--', linewidth=1.2, label=f'Avg ROAS: {campaign_roi["roas"].mean():.2f}x')
ax7.set_title('Campaign ROAS (Top 10)', fontweight='bold', fontsize=10, color=DARK)
ax7.set_ylabel('ROAS (x)', fontsize=8)
ax7.legend(fontsize=7)

ax8 = fig.add_subplot(gs[3,1])
ax8.set_facecolor(LIGHT)
ax8.axis('off')
stats_text = (
    f"Statistical Analysis Summary\n"
    f"{'─'*36}\n\n"
    f"Pearson Correlation\n"
    f"Discount vs Profit Margin\n"
    f"r = {corr_r:.3f}   p = {corr_p:.4f}\n"
    f"{'Significant' if corr_p < 0.05 else 'Not Significant'} at 95% CI\n\n"
    f"One-Way ANOVA\n"
    f"Revenue across categories\n"
    f"F = {f_stat:.2f}   p = {anova_p:.6f}\n"
    f"{'Significant' if anova_p < 0.05 else 'Not Significant'} at 95% CI\n\n"
    f"Revenue Distribution\n"
    f"Mean  : Rs {raw['revenue'].mean():,.0f}\n"
    f"Median: Rs {raw['revenue'].median():,.0f}\n"
    f"StdDev: Rs {raw['revenue'].std():,.0f}\n"
    f"Skew  : {stats.skew(raw['revenue']):.2f}"
)
ax8.text(0.05, 0.95, stats_text, transform=ax8.transAxes,
         va='top', ha='left', fontsize=8.5, fontfamily='DejaVu Sans',
         color=DARK, linespacing=1.6,
         bbox=dict(boxstyle='round,pad=0.6', facecolor='#EBF5FB', edgecolor=GREEN, linewidth=1.5))
ax8.set_title('Statistical Tests', fontweight='bold', fontsize=10, color=DARK)

ax9 = fig.add_subplot(gs[3,2])
ax9.set_facecolor(LIGHT)
ret_by_cat = return_analysis.groupby('category')['returns'].sum().sort_values(ascending=True)
r_colors = [RED if v == ret_by_cat.max() else YELLOW if v >= ret_by_cat.median() else GREEN
            for v in ret_by_cat.values]
ax9.barh(ret_by_cat.index, ret_by_cat.values, color=r_colors, edgecolor='white')
ax9.set_title('Returns by Category', fontweight='bold', fontsize=10, color=DARK)
ax9.set_xlabel('Number of Returns', fontsize=8)

plt.suptitle('ShopIndia E-commerce Platform — Complete Analytics Report',
             fontsize=16, fontweight='bold', y=0.995, color=DARK,
             fontfamily='DejaVu Sans')

chart_path = f'{OUT}/ecommerce_dashboard.png'
plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='#FFFFFF')
plt.close()
print("Dashboard saved.")

# ── EXCEL REPORT ──────────────────────────────────────────
excel_path = f'{OUT}/ShopIndia_Analytics_Report.xlsx'
writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
wb     = writer.book

hdr = wb.add_format({'bold':True,'font_color':'#FFFFFF','bg_color':'#2C3E50',
                     'border':1,'align':'center','font_name':'Arial','font_size':9})
alt1= wb.add_format({'bg_color':'#EBF5FB','border':1,'font_name':'Arial','font_size':9})
alt2= wb.add_format({'bg_color':'#FFFFFF','border':1,'font_name':'Arial','font_size':9})
red = wb.add_format({'font_color':'#C0392B','bold':True,'bg_color':'#FADBD8',
                     'border':1,'font_name':'Arial','font_size':9})
grn = wb.add_format({'font_color':'#27AE60','bold':True,'bg_color':'#D5F5E3',
                     'border':1,'font_name':'Arial','font_size':9})
ttl = wb.add_format({'bold':True,'font_size':13,'font_color':'#FFFFFF',
                     'bg_color':'#2C3E50','align':'center','valign':'vcenter',
                     'font_name':'Arial'})
kpi_fmt = wb.add_format({'bold':True,'font_size':14,'font_color':'#C0392B',
                          'align':'center','valign':'vcenter','border':2,
                          'bg_color':'#FDEDEC','font_name':'Arial'})
kpi_lbl = wb.add_format({'font_size':8,'font_color':'#7F8C8D','align':'center',
                          'bg_color':'#F5F6FA','font_name':'Arial'})

def write_sheet(ws, df, row_start=1):
    for c, col in enumerate(df.columns):
        ws.write(row_start, c, col, hdr)
    for r, row in enumerate(df.itertuples(index=False), row_start+1):
        fmt = alt1 if r%2==0 else alt2
        for c, val in enumerate(row):
            ws.write(r, c, val, fmt)
    for c in range(len(df.columns)):
        ws.set_column(c, c, 18)

# Sheet 1: Executive Summary
ws1 = wb.add_worksheet('Executive Summary')
ws1.set_tab_color('#C0392B')
ws1.merge_range('A1:H2','ShopIndia E-commerce — Executive Summary 2020-2024', ttl)
ws1.set_row(0,22); ws1.set_row(1,22)
kpi_vals = [
    (f"Rs {kpi['revenue_crore'].iloc[0]}Cr", 'Total Revenue'),
    (f"Rs {kpi['profit_crore'].iloc[0]}Cr",  'Total Profit'),
    (f"{kpi['avg_margin'].iloc[0]}%",         'Avg Margin'),
    (f"{kpi['customers'].iloc[0]:,}",          'Customers'),
    (f"{kpi['orders'].iloc[0]:,}",             'Orders'),
    (f"Rs {kpi['aov'].iloc[0]:,}",             'Avg Order Value'),
]
for i,(v,l) in enumerate(kpi_vals):
    ws1.merge_range(3,i,3,i,v,kpi_fmt)
    ws1.merge_range(4,i,4,i,l,kpi_lbl)
    ws1.set_row(3,32); ws1.set_row(4,18)
ws1.merge_range('A7:H7','Year-wise Performance', ttl)
write_sheet(ws1, yearly, 7)
ws1.insert_image('A20', chart_path, {'x_scale':0.6,'y_scale':0.6})

# Sheet 2: Category Analytics
ws2 = wb.add_worksheet('Category Analytics')
ws2.set_tab_color('#F39C12')
ws2.merge_range('A1:H1','Category Performance Analysis', ttl)
write_sheet(ws2, category_perf, 1)
ws2.merge_range('A14:H14','Return Analysis by Category and Reason', ttl)
write_sheet(ws2, return_analysis, 14)

# Sheet 3: Customer Analytics
ws3 = wb.add_worksheet('Customer Analytics')
ws3.set_tab_color('#27AE60')
ws3.merge_range('A1:H1','RFM Customer Segmentation', ttl)
write_sheet(ws3, rfm, 1)
ws3.merge_range('A10:H10','State Performance', ttl)
write_sheet(ws3, state_perf, 10)
ws3.merge_range('A23:H23','Payment Method Analysis', ttl)
write_sheet(ws3, payment_analysis, 23)

# Sheet 4: Marketing Analytics
ws4 = wb.add_worksheet('Marketing Analytics')
ws4.set_tab_color('#2980B9')
ws4.merge_range('A1:H1','Campaign ROI Analysis', ttl)
write_sheet(ws4, campaign_roi, 1)
channel_perf = q("""
    SELECT channel, COUNT(*) AS campaigns,
           ROUND(AVG(roas),2) AS avg_roas,
           SUM(new_customers) AS new_customers,
           ROUND(SUM(budget)/SUM(new_customers),0) AS avg_cac
    FROM campaigns GROUP BY channel ORDER BY avg_roas DESC
""")
ws4.merge_range('A14:H14','Channel Effectiveness', ttl)
write_sheet(ws4, channel_perf, 14)

# Sheet 5: Statistical Analysis
ws5 = wb.add_worksheet('Statistical Analysis')
ws5.set_tab_color('#8E44AD')
ws5.merge_range('A1:H1','Statistical Analysis Summary', ttl)
stat_df = q("""
    SELECT category,
           COUNT(*) AS n,
           ROUND(AVG(revenue),0) AS mean_revenue,
           ROUND(MEDIAN(revenue),0) AS median_revenue,
           ROUND(STDDEV(revenue),0) AS std_dev,
           ROUND(MIN(revenue),0) AS min_val,
           ROUND(MAX(revenue),0) AS max_val,
           ROUND(AVG(profit_margin),2) AS avg_margin
    FROM order_items WHERE return_flag=0 GROUP BY category
""")
write_sheet(ws5, stat_df, 1)
ws5.merge_range('A14:H14','Discount Elasticity Analysis', ttl)
write_sheet(ws5, discount_analysis, 14)
# Write stat test results
ws5.write(22, 0, 'Statistical Test', hdr)
ws5.write(22, 1, 'Result', hdr)
ws5.write(22, 2, 'p-value', hdr)
ws5.write(22, 3, 'Conclusion', hdr)
ws5.write(23, 0, 'Pearson: Discount vs Margin', alt1)
ws5.write(23, 1, f'r = {corr_r:.3f}', alt1)
ws5.write(23, 2, round(corr_p,4), alt1)
ws5.write(23, 3, 'Significant - discount hurts margin', red if corr_p<0.05 else alt1)
ws5.write(24, 0, 'ANOVA: Revenue by Category', alt2)
ws5.write(24, 1, f'F = {f_stat:.2f}', alt2)
ws5.write(24, 2, round(anova_p,6), alt2)
ws5.write(24, 3, 'Revenue differs significantly across categories', grn if anova_p<0.05 else alt2)

writer.close()
print(f"Excel saved: {excel_path}")
con.close()
print("\nAll outputs complete.")
print(f"  Dashboard : {OUT}/ecommerce_dashboard.png")
print(f"  Excel     : {OUT}/ShopIndia_Analytics_Report.xlsx")
