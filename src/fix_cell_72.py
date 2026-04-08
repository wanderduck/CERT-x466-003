import json

new_code_part1 = """### ML 5: Job Market Growth Analysis — Trend and Year-over-Year Growth
# 2026 only contains 1 quarter of data (Jan-Mar). 
# To compute meaningful year-over-year growth and linear trends,
# we annualize the 2026 data by multiplying it by 4 (12 months / 3 months).

# --- 1. Annual posting counts and YoY growth ---
annual_counts = ai_df.groupby('job_posting_year').size().reset_index(name='postings')

# Annualize 2026
months_in_2026 = ai_df[ai_df['job_posting_year'] == 2026]['job_posting_month'].nunique()
annualize_factor = 12 / months_in_2026 if months_in_2026 > 0 else 1

annual_counts['annualized_postings'] = annual_counts['postings'].copy()
annual_counts.loc[annual_counts['job_posting_year'] == 2026, 'annualized_postings'] *= annualize_factor
annual_counts['yoy_growth'] = annual_counts['annualized_postings'].pct_change() * 100

# --- 2. Entry-level annual counts and YoY growth ---
entry_annual = ai_df[ai_df['experience_level'] == 'Entry'].groupby('job_posting_year').size().reset_index(name='entry_postings')
annual_counts = annual_counts.merge(entry_annual, on='job_posting_year')

annual_counts['annualized_entry_postings'] = annual_counts['entry_postings'].copy()
annual_counts.loc[annual_counts['job_posting_year'] == 2026, 'annualized_entry_postings'] *= annualize_factor
annual_counts['entry_yoy_growth'] = annual_counts['annualized_entry_postings'].pct_change() * 100

# --- 3. Linear trend fit (using annualized data) ---
years = annual_counts['job_posting_year'].values.astype(float)
counts_annualized = annual_counts['annualized_postings'].values.astype(float)
slope, intercept = np.polyfit(years, counts_annualized, 1)
trend_line = slope * years + intercept

print('=== Job Market Growth Analysis ===')
print(f'Linear trend: ~{slope:.0f} additional postings per year (based on annualized data)')
print(f'\\nYear-over-Year Growth Rates:')
for _, row in annual_counts.iterrows():
    year = int(row['job_posting_year'])
    yoy = f"{row['yoy_growth']:+.1f}%" if not np.isnan(row['yoy_growth']) else 'N/A'
    entry_yoy = f"{row['entry_yoy_growth']:+.1f}%" if not np.isnan(row['entry_yoy_growth']) else 'N/A'
    
    if year == 2026:
        print(f"  {year}: {int(row['postings']):,} actual -> {int(row['annualized_postings']):,} annualized ({yoy})  |  {int(row['entry_postings']):,} actual -> {int(row['annualized_entry_postings']):,} entry annualized ({entry_yoy})")
    else:
        print(f"  {year}: {int(row['postings']):,} total ({yoy})  |  {int(row['entry_postings']):,} entry-level ({entry_yoy})")

# --- 4. Visualization: Total vs Entry postings with trend ---
"""

new_code_part2 = """fig = make_subplots(rows=1, cols=2, subplot_titles=('Total Job Postings with Linear Trend',
                                                      'Year-over-Year Growth: Total vs. Entry-Level'))

# Subplot 1: Total Postings (use annualized for all so it's a single bar series, but color 2026 differently)
colors = ['#636EFA'] * len(annual_counts)
colors[-1] = 'rgba(99, 110, 250, 0.5)' # Lighter color for projected 2026

fig.add_trace(go.Bar(x=annual_counts['job_posting_year'], 
                     y=annual_counts['annualized_postings'],
                     name='Annualized Postings', marker_color=colors,
                     text=annual_counts['annualized_postings'].apply(lambda x: f"{x:,.0f}{'*' if x == annual_counts['annualized_postings'].iloc[-1] else ''}"),
                     textposition='auto'), row=1, col=1)

fig.add_trace(go.Scatter(x=annual_counts['job_posting_year'], y=trend_line,
                         mode='lines', name=f'Trend (+{slope:.0f}/yr)',
                         line=dict(dash='dash', color='red', width=2)), row=1, col=1)

# Subplot 2: YoY Growth
fig.add_trace(go.Bar(x=annual_counts['job_posting_year'], y=annual_counts['yoy_growth'],
                     name='Total YoY %', marker_color='#636EFA'), row=1, col=2)
fig.add_trace(go.Bar(x=annual_counts['job_posting_year'], y=annual_counts['entry_yoy_growth'],
                     name='Entry-Level YoY %', marker_color='#EF553B'), row=1, col=2)

fig.update_layout(title='Job Market Growth Analysis: Overall Trend and Entry-Level Comparison<br><sup>*2026 figures are annualized based on Q1 data</sup>',
                  height=450, barmode='group')
fig.update_xaxes(title_text='Year', row=1, col=1)
fig.update_xaxes(title_text='Year', row=1, col=2)
fig.update_yaxes(title_text='Number of Postings', row=1, col=1)
fig.update_yaxes(title_text='Growth Rate (%)', row=1, col=2)

fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.69)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.69)')
)

fig.write_image('notebook_images/plot_images/new/ml05_01.png', scale=2)
fig.show()
"""

with open("CERT-x466-003_MAIN.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        src = "".join(cell.get("source", []))
        if "### ML 5: Job Market Growth Analysis" in src:
            final_code = new_code_part1 + new_code_part2
            
            # Use original save location if needed, but let's extract the actual write_image call from the original source
            # Find the write_image line in original source
            write_image_line = next((line for line in src.split("\n") if "fig.write_image" in line), "fig.write_image('notebook_images/plot_images/jobmarket_growthanalysis.png', scale=2)")
            
            final_code = final_code.replace("fig.write_image('notebook_images/plot_images/new/ml05_01.png', scale=2)", write_image_line.strip())
            
            cell["source"] = [line + "\n" for line in final_code.split("\n")]
            break

with open("CERT-x466-003_MAIN.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
    f.write('\n')
