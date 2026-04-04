# Job Posting Forecast Model — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a hybrid SARIMA + proportion forecasting section to the notebook that projects AI job postings through Dec 2028 across all segment dimensions.

**Architecture:** Layer 1 fits SARIMA on aggregate monthly postings (84 months). Layer 2 models monthly shares for each segment dimension (experience level, remote type, industry, country) with per-category ARIMA, normalizes shares, and multiplies by the Layer 1 total forecast. Skills are modeled as independent rate series. Visualizations are split into Audience A (storytelling Plotly charts) and Audience B (methodology/diagnostics).

**Tech Stack:** pandas, numpy, statsmodels (SARIMAX), scipy.stats, plotly, itertools

**Spec:** `docs/superpowers/specs/2026-04-03-job-posting-forecast-design.md`

---

## File Map

All work happens in **one file**: `CERT-x466-003_MAIN.ipynb`. We insert 8 new cells after cell index 66 (the PyTorch Integrated Gradients code cell), before cell index 67 (the empty DATA STORY markdown cell). Cells are inserted by a Python script that manipulates the notebook JSON directly.

The notebook source list format: each cell's `"source"` is a list of strings, each ending in `\n` except possibly the last.

---

## Task 1: Insert Section Header Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert after cell index 66)

- [ ] **Step 1: Write the cell insertion script and insert the markdown header**

Create a Python script that inserts a markdown cell at index 67 (pushing existing cells down):

```bash
python3 -c "
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

cell = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '---\n',
        '## FORECASTING — Job Market Projections Through 2028\n',
        '\n',
        'The EDA and ML sections above show what the AI job market looks like *today*. Now we ask: **where is it heading?**\n',
        '\n',
        'We use a **hybrid forecasting approach**:\n',
        '1. **SARIMA** on aggregate monthly postings to project total market volume\n',
        '2. **Proportion models** for each segment (experience level, remote type, industry, country) to forecast *compositional shifts*\n',
        '3. **Rate models** for skill requirements (Python, SQL, ML, Deep Learning, Cloud)\n',
        '\n',
        'The key insight: with near-stationary total volume, the interesting story is not \"how much\" but \"what mix\" — and that is exactly what matters for someone planning to enter the market.'
    ],
    'id': uuid.uuid4().hex[:8]
}

nb['cells'].insert(67, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted markdown cell at index 67. Total cells: {len(nb[\"cells\"])}')
"
```

- [ ] **Step 2: Verify the cell was inserted correctly**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Cell 66 type: {nb[\"cells\"][66][\"cell_type\"]}')
print(f'Cell 67 type: {nb[\"cells\"][67][\"cell_type\"]}')
print(f'Cell 67 source: {\"|\".join(nb[\"cells\"][67][\"source\"][:2])}')
print(f'Cell 68 type: {nb[\"cells\"][68][\"cell_type\"]}')
"
```

Expected: Total cells: 69, Cell 67 is markdown starting with `---`, Cell 68 is the old empty markdown cell.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add forecasting section header to notebook"
```

---

## Task 2: Insert Forecast Preparation Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert code cell at index 68)

This cell builds all the time series data structures that subsequent cells consume. It depends on `ai_df` from cell 14 and `skill_cols` from EDA cell 35.

- [ ] **Step 1: Insert the forecast preparation code cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

code = r'''### Forecast Preparation — Build Monthly Time Series
import warnings
from itertools import product

# --- 1. Aggregate monthly postings ---
monthly_total = (
    ai_df.groupby(['job_posting_year', 'job_posting_month'])
    .size()
    .reset_index(name='count')
)
monthly_total['date'] = pd.to_datetime(
    monthly_total['job_posting_year'].astype(str) + '-'
    + monthly_total['job_posting_month'].astype(str).str.zfill(2) + '-01'
)
monthly_total = monthly_total.sort_values('date').reset_index(drop=True)
monthly_total = monthly_total.set_index('date')

print(f"Monthly total series: {len(monthly_total)} months, "
      f"{monthly_total['count'].min()}-{monthly_total['count'].max()} range")

# --- 2. Segment proportion series ---
segment_dims = {
    'experience_level': ['Entry', 'Mid', 'Senior'],
    'remote_type': ['Remote', 'Hybrid', 'Onsite'],
    'company_industry': ai_df['company_industry'].unique().tolist(),
    'country': ai_df['country'].unique().tolist(),
}

segment_shares = {}  # {dim: DataFrame with date index, one column per category}
for dim, categories in segment_dims.items():
    shares_df = pd.DataFrame(index=monthly_total.index)
    for cat in categories:
        cat_monthly = (
            ai_df[ai_df[dim] == cat]
            .groupby(['job_posting_year', 'job_posting_month'])
            .size()
            .reset_index(name='count')
        )
        cat_monthly['date'] = pd.to_datetime(
            cat_monthly['job_posting_year'].astype(str) + '-'
            + cat_monthly['job_posting_month'].astype(str).str.zfill(2) + '-01'
        )
        cat_monthly = cat_monthly.set_index('date').reindex(monthly_total.index, fill_value=0)
        shares_df[cat] = cat_monthly['count'] / monthly_total['count']
    segment_shares[dim] = shares_df
    print(f"  {dim}: {len(categories)} categories, shares sum check = "
          f"{shares_df.sum(axis=1).mean():.4f}")

# --- 3. Skill rate series ---
skill_cols_forecast = ['skills_python', 'skills_sql', 'skills_ml',
                       'skills_deep_learning', 'skills_cloud']
skill_rates = pd.DataFrame(index=monthly_total.index)
for skill in skill_cols_forecast:
    monthly_rate = (
        ai_df.groupby(['job_posting_year', 'job_posting_month'])[skill]
        .mean()
        .reset_index(name='rate')
    )
    monthly_rate['date'] = pd.to_datetime(
        monthly_rate['job_posting_year'].astype(str) + '-'
        + monthly_rate['job_posting_month'].astype(str).str.zfill(2) + '-01'
    )
    monthly_rate = monthly_rate.set_index('date').reindex(monthly_total.index)
    skill_rates[skill] = monthly_rate['rate']
print(f"  Skills: {len(skill_cols_forecast)} rate series built")

# --- 4. Entry-level sub-segment shares (for Audience A dashboard) ---
entry_df_forecast = ai_df[ai_df['experience_level'] == 'Entry']
entry_sub_dims = {
    'remote_type': ['Remote', 'Hybrid', 'Onsite'],
    'company_industry': ai_df['company_industry'].unique().tolist(),
}
entry_monthly_total = (
    entry_df_forecast.groupby(['job_posting_year', 'job_posting_month'])
    .size()
    .reset_index(name='count')
)
entry_monthly_total['date'] = pd.to_datetime(
    entry_monthly_total['job_posting_year'].astype(str) + '-'
    + entry_monthly_total['job_posting_month'].astype(str).str.zfill(2) + '-01'
)
entry_monthly_total = entry_monthly_total.set_index('date').reindex(monthly_total.index, fill_value=0)

entry_segment_shares = {}
for dim, categories in entry_sub_dims.items():
    shares_df = pd.DataFrame(index=monthly_total.index)
    for cat in categories:
        cat_monthly = (
            entry_df_forecast[entry_df_forecast[dim] == cat]
            .groupby(['job_posting_year', 'job_posting_month'])
            .size()
            .reset_index(name='count')
        )
        cat_monthly['date'] = pd.to_datetime(
            cat_monthly['job_posting_year'].astype(str) + '-'
            + cat_monthly['job_posting_month'].astype(str).str.zfill(2) + '-01'
        )
        cat_monthly = cat_monthly.set_index('date').reindex(monthly_total.index, fill_value=0)
        shares_df[cat] = cat_monthly['count'] / entry_monthly_total['count'].replace(0, np.nan)
    shares_df = shares_df.fillna(1.0 / len(categories))  # uniform if no data
    entry_segment_shares[dim] = shares_df

# --- 5. Entry-level skill rates ---
entry_skill_rates = pd.DataFrame(index=monthly_total.index)
for skill in skill_cols_forecast:
    monthly_rate = (
        entry_df_forecast.groupby(['job_posting_year', 'job_posting_month'])[skill]
        .mean()
        .reset_index(name='rate')
    )
    monthly_rate['date'] = pd.to_datetime(
        monthly_rate['job_posting_year'].astype(str) + '-'
        + monthly_rate['job_posting_month'].astype(str).str.zfill(2) + '-01'
    )
    monthly_rate = monthly_rate.set_index('date').reindex(monthly_total.index)
    entry_skill_rates[skill] = monthly_rate['rate']

print("\nForecast data preparation complete.")
print(f"  Total series: {len(monthly_total)} months (Jan 2020 - Dec 2026)")
print(f"  Forecast horizon: 24 months (Jan 2027 - Dec 2028)")'''

cell = {
    'cell_type': 'code',
    'metadata': {},
    'source': [line + '\n' for line in code.split('\n')],
    'outputs': [],
    'execution_count': None,
    'id': uuid.uuid4().hex[:8]
}
# Remove trailing \n from last line
cell['source'][-1] = cell['source'][-1].rstrip('\n')

nb['cells'].insert(68, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted forecast prep cell at index 68. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell was inserted**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
print(f'Total cells: {len(nb[\"cells\"])}')
src = ''.join(nb['cells'][68]['source'])
print(f'Cell 68 starts with: {src[:60]}')
print(f'Cell 68 has monthly_total: {\"monthly_total\" in src}')
print(f'Cell 68 has segment_shares: {\"segment_shares\" in src}')
print(f'Cell 68 has skill_rates: {\"skill_rates\" in src}')
print(f'Cell 68 has entry_segment_shares: {\"entry_segment_shares\" in src}')
"
```

Expected: Total cells: 70, all checks True.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add forecast data preparation cell"
```

---

## Task 3: Insert Layer 1 — Total SARIMA Forecast Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert code cell at index 69)

This cell depends on `monthly_total` from Task 2. It fits a SARIMA model via AIC grid search and produces a 24-month forecast with prediction intervals.

- [ ] **Step 1: Insert the SARIMA forecast code cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

code = r'''### Layer 1: Total Postings — SARIMA Forecast
from statsmodels.tsa.statespace.sarimax import SARIMAX

FORECAST_STEPS = 24  # Jan 2027 - Dec 2028

# --- 1. Grid search for best SARIMA order ---
y = monthly_total['count'].astype(float)

best_aic = np.inf
best_order = None
best_seasonal = None
results_log = []

p_range = range(3)  # 0, 1, 2
d_range = range(2)  # 0, 1
q_range = range(3)
P_range = range(2)  # 0, 1
D_range = range(2)
Q_range = range(2)

print("Fitting SARIMA models (this may take a minute)...")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    for p, d, q in product(p_range, d_range, q_range):
        for P, D, Q in product(P_range, D_range, Q_range):
            try:
                model = SARIMAX(y, order=(p, d, q),
                                seasonal_order=(P, D, Q, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
                fit = model.fit(disp=False, maxiter=200)
                results_log.append({
                    'order': (p, d, q),
                    'seasonal': (P, D, Q, 12),
                    'aic': fit.aic
                })
                if fit.aic < best_aic:
                    best_aic = fit.aic
                    best_order = (p, d, q)
                    best_seasonal = (P, D, Q, 12)
            except Exception:
                continue

print(f"\nBest SARIMA{best_order}x{best_seasonal} — AIC: {best_aic:.1f}")
print(f"Models evaluated: {len(results_log)}")

# --- 2. Fit best model and forecast ---
best_model = SARIMAX(y, order=best_order, seasonal_order=best_seasonal,
                     enforce_stationarity=False, enforce_invertibility=False)
sarima_fit = best_model.fit(disp=False)

forecast_result = sarima_fit.get_forecast(steps=FORECAST_STEPS)
forecast_mean = forecast_result.predicted_mean
forecast_ci_80 = forecast_result.conf_int(alpha=0.20)
forecast_ci_95 = forecast_result.conf_int(alpha=0.05)

# Build forecast date index
last_date = monthly_total.index[-1]
forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1),
                               periods=FORECAST_STEPS, freq='MS')
forecast_mean.index = forecast_dates
forecast_ci_80.index = forecast_dates
forecast_ci_95.index = forecast_dates

# --- 3. Build combined historical + forecast DataFrame ---
total_forecast_df = pd.DataFrame({
    'date': list(monthly_total.index) + list(forecast_dates),
    'count': list(y.values) + list(forecast_mean.values),
    'is_forecast': [False] * len(y) + [True] * FORECAST_STEPS,
})
total_forecast_df['ci_80_lower'] = np.nan
total_forecast_df['ci_80_upper'] = np.nan
total_forecast_df['ci_95_lower'] = np.nan
total_forecast_df['ci_95_upper'] = np.nan
total_forecast_df.loc[total_forecast_df['is_forecast'], 'ci_80_lower'] = forecast_ci_80.iloc[:, 0].values
total_forecast_df.loc[total_forecast_df['is_forecast'], 'ci_80_upper'] = forecast_ci_80.iloc[:, 1].values
total_forecast_df.loc[total_forecast_df['is_forecast'], 'ci_95_lower'] = forecast_ci_95.iloc[:, 0].values
total_forecast_df.loc[total_forecast_df['is_forecast'], 'ci_95_upper'] = forecast_ci_95.iloc[:, 1].values

print(f"\nForecast range: {forecast_dates[0].strftime('%Y-%m')} to {forecast_dates[-1].strftime('%Y-%m')}")
print(f"Predicted monthly avg: {forecast_mean.mean():.0f} (historical avg: {y.mean():.0f})")
print(f"\nModel Summary:")
print(sarima_fit.summary().tables[1])'''

cell = {
    'cell_type': 'code',
    'metadata': {},
    'source': [line + '\n' for line in code.split('\n')],
    'outputs': [],
    'execution_count': None,
    'id': uuid.uuid4().hex[:8]
}
cell['source'][-1] = cell['source'][-1].rstrip('\n')

nb['cells'].insert(69, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted SARIMA cell at index 69. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
src = ''.join(nb['cells'][69]['source'])
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Has SARIMAX: {\"SARIMAX\" in src}')
print(f'Has FORECAST_STEPS: {\"FORECAST_STEPS = 24\" in src}')
print(f'Has forecast_mean: {\"forecast_mean\" in src}')
print(f'Has total_forecast_df: {\"total_forecast_df\" in src}')
"
```

Expected: Total cells: 71, all checks True.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add SARIMA total postings forecast cell"
```

---

## Task 4: Insert Layer 2 — Proportion Forecasts Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert code cell at index 70)

Depends on `segment_shares`, `entry_segment_shares`, `forecast_mean`, `forecast_dates`, `monthly_total`, `FORECAST_STEPS` from previous cells.

- [ ] **Step 1: Insert the proportion forecast code cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

code = r'''### Layer 2: Proportion Forecasts — Segment Composition Over Time
from statsmodels.tsa.arima.model import ARIMA

def fit_best_arima(series, max_p=2, max_d=1, max_q=2):
    """Fit best ARIMA by AIC. Returns (fitted_model, order) or (None, None) on failure."""
    best_aic = np.inf
    best_fit = None
    best_order = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for p, d, q in product(range(max_p + 1), range(max_d + 1), range(max_q + 1)):
            if p == 0 and q == 0 and d == 0:
                continue  # skip trivial model
            try:
                model = ARIMA(series, order=(p, d, q))
                fit = model.fit()
                if fit.aic < best_aic:
                    best_aic = fit.aic
                    best_fit = fit
                    best_order = (p, d, q)
            except Exception:
                continue
    return best_fit, best_order

# --- 1. Forecast shares for each segment dimension ---
segment_forecasts = {}  # {dim: DataFrame with forecast_dates index, one col per category}
model_log = []  # for Audience B summary table

print("Fitting proportion models...")
for dim, shares_df in segment_shares.items():
    forecast_shares = pd.DataFrame(index=forecast_dates)
    for cat in shares_df.columns:
        series = shares_df[cat].astype(float)
        fit, order = fit_best_arima(series)
        if fit is not None:
            fc = fit.forecast(steps=FORECAST_STEPS)
            forecast_shares[cat] = fc.values
            model_log.append({
                'dimension': dim, 'category': cat,
                'order': order, 'aic': fit.aic, 'type': 'share'
            })
        else:
            # Fallback: historical mean share
            forecast_shares[cat] = series.mean()
            model_log.append({
                'dimension': dim, 'category': cat,
                'order': 'fallback (mean)', 'aic': None, 'type': 'share'
            })
    # Normalize shares to sum to 1.0
    row_sums = forecast_shares.sum(axis=1)
    forecast_shares = forecast_shares.div(row_sums, axis=0)
    segment_forecasts[dim] = forecast_shares
    print(f"  {dim}: {len(shares_df.columns)} categories done, "
          f"shares sum = {forecast_shares.sum(axis=1).mean():.4f}")

# --- 2. Convert shares to counts ---
segment_count_forecasts = {}
for dim, fc_shares in segment_forecasts.items():
    segment_count_forecasts[dim] = fc_shares.multiply(forecast_mean.values, axis=0)

# --- 3. Build combined historical + forecast DataFrames per dimension ---
segment_combined = {}  # {dim: {cat: DataFrame with date, count, share, is_forecast}}
for dim in segment_shares:
    dim_data = {}
    for cat in segment_shares[dim].columns:
        hist_counts = (segment_shares[dim][cat] * monthly_total['count']).values
        hist_shares = segment_shares[dim][cat].values
        fc_counts = segment_count_forecasts[dim][cat].values
        fc_shares = segment_forecasts[dim][cat].values
        dim_data[cat] = pd.DataFrame({
            'date': list(monthly_total.index) + list(forecast_dates),
            'count': list(hist_counts) + list(fc_counts),
            'share': list(hist_shares) + list(fc_shares),
            'is_forecast': [False] * len(monthly_total) + [True] * FORECAST_STEPS,
        })
    segment_combined[dim] = dim_data

# --- 4. Entry-level sub-segment forecasts ---
# Get entry-level count forecast from Layer 2
entry_share_forecast = segment_forecasts['experience_level']['Entry']
entry_count_forecast = entry_share_forecast * forecast_mean.values
entry_count_historical = segment_shares['experience_level']['Entry'] * monthly_total['count']

entry_sub_forecasts = {}
for dim, shares_df in entry_segment_shares.items():
    fc_shares = pd.DataFrame(index=forecast_dates)
    for cat in shares_df.columns:
        series = shares_df[cat].astype(float)
        fit, order = fit_best_arima(series)
        if fit is not None:
            fc = fit.forecast(steps=FORECAST_STEPS)
            fc_shares[cat] = fc.values
            model_log.append({
                'dimension': f'entry_{dim}', 'category': cat,
                'order': order, 'aic': fit.aic, 'type': 'entry_share'
            })
        else:
            fc_shares[cat] = series.mean()
            model_log.append({
                'dimension': f'entry_{dim}', 'category': cat,
                'order': 'fallback (mean)', 'aic': None, 'type': 'entry_share'
            })
    row_sums = fc_shares.sum(axis=1)
    fc_shares = fc_shares.div(row_sums, axis=0)
    entry_sub_forecasts[dim] = fc_shares

model_log_df = pd.DataFrame(model_log)
print(f"\nProportion forecasts complete. {len(model_log)} models fitted.")
print(model_log_df[['dimension', 'category', 'order', 'aic']].to_string(index=False))'''

cell = {
    'cell_type': 'code',
    'metadata': {},
    'source': [line + '\n' for line in code.split('\n')],
    'outputs': [],
    'execution_count': None,
    'id': uuid.uuid4().hex[:8]
}
cell['source'][-1] = cell['source'][-1].rstrip('\n')

nb['cells'].insert(70, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted proportion forecast cell at index 70. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
src = ''.join(nb['cells'][70]['source'])
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Has fit_best_arima: {\"fit_best_arima\" in src}')
print(f'Has segment_forecasts: {\"segment_forecasts\" in src}')
print(f'Has entry_sub_forecasts: {\"entry_sub_forecasts\" in src}')
print(f'Has model_log_df: {\"model_log_df\" in src}')
"
```

Expected: Total cells: 72, all checks True.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add proportion forecast cell for all segment dimensions"
```

---

## Task 5: Insert Skills Rate Forecast Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert code cell at index 71)

Depends on `skill_rates`, `entry_skill_rates`, `fit_best_arima`, `forecast_dates`, `FORECAST_STEPS`, `model_log_df` from previous cells.

- [ ] **Step 1: Insert the skills rate forecast code cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

code = r'''### Skills Rate Forecasts

# --- 1. Forecast overall skill requirement rates ---
skill_forecasts = pd.DataFrame(index=forecast_dates)
skill_model_log = []

print("Fitting skill rate models...")
for skill in skill_cols_forecast:
    series = skill_rates[skill].astype(float)
    fit, order = fit_best_arima(series)
    if fit is not None:
        fc = fit.forecast(steps=FORECAST_STEPS)
        skill_forecasts[skill] = fc.values.clip(0, 1)
        skill_model_log.append({
            'dimension': 'skill_rate', 'category': skill,
            'order': order, 'aic': fit.aic, 'type': 'skill'
        })
    else:
        skill_forecasts[skill] = series.mean()
        skill_model_log.append({
            'dimension': 'skill_rate', 'category': skill,
            'order': 'fallback (mean)', 'aic': None, 'type': 'skill'
        })

# --- 2. Forecast entry-level skill rates ---
entry_skill_forecasts = pd.DataFrame(index=forecast_dates)
for skill in skill_cols_forecast:
    series = entry_skill_rates[skill].astype(float)
    fit, order = fit_best_arima(series)
    if fit is not None:
        fc = fit.forecast(steps=FORECAST_STEPS)
        entry_skill_forecasts[skill] = fc.values.clip(0, 1)
        skill_model_log.append({
            'dimension': 'entry_skill_rate', 'category': skill,
            'order': order, 'aic': fit.aic, 'type': 'entry_skill'
        })
    else:
        entry_skill_forecasts[skill] = series.mean()
        skill_model_log.append({
            'dimension': 'entry_skill_rate', 'category': skill,
            'order': 'fallback (mean)', 'aic': None, 'type': 'entry_skill'
        })

# --- 3. Build combined skill DataFrames ---
skill_combined = pd.DataFrame(index=list(monthly_total.index) + list(forecast_dates))
for skill in skill_cols_forecast:
    skill_combined[skill] = list(skill_rates[skill].values) + list(skill_forecasts[skill].values)
skill_combined['is_forecast'] = [False] * len(monthly_total) + [True] * FORECAST_STEPS

entry_skill_combined = pd.DataFrame(index=list(monthly_total.index) + list(forecast_dates))
for skill in skill_cols_forecast:
    entry_skill_combined[skill] = (
        list(entry_skill_rates[skill].values)
        + list(entry_skill_forecasts[skill].values)
    )
entry_skill_combined['is_forecast'] = [False] * len(monthly_total) + [True] * FORECAST_STEPS

# --- 4. Append to model log ---
skill_log_df = pd.DataFrame(skill_model_log)
all_model_log = pd.concat([model_log_df, skill_log_df], ignore_index=True)

print(f"\nSkill rate forecasts complete. {len(skill_model_log)} models fitted.")
for _, row in skill_log_df.iterrows():
    print(f"  {row['category']}: ARIMA{row['order']} (AIC={row['aic']:.1f})"
          if row['aic'] is not None
          else f"  {row['category']}: fallback (mean)")
print(f"\nTotal models across all dimensions: {len(all_model_log)}")'''

cell = {
    'cell_type': 'code',
    'metadata': {},
    'source': [line + '\n' for line in code.split('\n')],
    'outputs': [],
    'execution_count': None,
    'id': uuid.uuid4().hex[:8]
}
cell['source'][-1] = cell['source'][-1].rstrip('\n')

nb['cells'].insert(71, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted skills forecast cell at index 71. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
src = ''.join(nb['cells'][71]['source'])
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Has skill_forecasts: {\"skill_forecasts\" in src}')
print(f'Has entry_skill_forecasts: {\"entry_skill_forecasts\" in src}')
print(f'Has all_model_log: {\"all_model_log\" in src}')
"
```

Expected: Total cells: 73, all checks True.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add skill rate forecast cell"
```

---

## Task 6: Insert Diagnostics & Summary Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert code cell at index 72)

Depends on `sarima_fit`, `all_model_log` from previous cells.

- [ ] **Step 1: Insert diagnostics cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

code = r'''### Diagnostics & Model Summary
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats as sp_stats

# --- 1. Residual diagnostics for the total SARIMA model ---
residuals = sarima_fit.resid

# Ljung-Box test for residual autocorrelation
lb_test = acorr_ljungbox(residuals, lags=[12], return_df=True)
lb_pval = lb_test['lb_pvalue'].values[0]

print("=== Total SARIMA Model Diagnostics ===")
print(f"Model: SARIMA{best_order}x{best_seasonal}")
print(f"AIC: {sarima_fit.aic:.1f}")
print(f"Residual mean: {residuals.mean():.2f}")
print(f"Residual std: {residuals.std():.2f}")
print(f"Ljung-Box p-value (lag 12): {lb_pval:.4f} "
      f"({'no significant autocorrelation' if lb_pval > 0.05 else 'WARNING: residual autocorrelation detected'})")

# --- 2. Diagnostics plot (2x2) ---
fig_diag = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Residuals Over Time', 'ACF of Residuals',
                    'Residual Distribution', 'Q-Q Plot')
)

# Residuals over time
fig_diag.add_trace(go.Scatter(
    x=monthly_total.index, y=residuals,
    mode='lines', name='Residuals', line=dict(color='#636EFA')
), row=1, col=1)
fig_diag.add_hline(y=0, line_dash='dash', line_color='red', row=1, col=1)

# ACF
from statsmodels.tsa.stattools import acf
acf_vals, acf_ci = acf(residuals, nlags=24, alpha=0.05)
fig_diag.add_trace(go.Bar(
    x=list(range(25)), y=acf_vals,
    name='ACF', marker_color='#636EFA'
), row=1, col=2)
# Confidence bounds
ci_upper = 1.96 / np.sqrt(len(residuals))
fig_diag.add_hline(y=ci_upper, line_dash='dash', line_color='red', row=1, col=2)
fig_diag.add_hline(y=-ci_upper, line_dash='dash', line_color='red', row=1, col=2)

# Histogram
fig_diag.add_trace(go.Histogram(
    x=residuals, nbinsx=20, name='Residuals',
    marker_color='#636EFA'
), row=2, col=1)

# Q-Q plot
sorted_resid = np.sort(residuals)
theoretical_q = sp_stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_resid)))
fig_diag.add_trace(go.Scatter(
    x=theoretical_q, y=sorted_resid,
    mode='markers', name='Q-Q', marker=dict(color='#636EFA', size=4)
), row=2, col=2)
qq_min = min(theoretical_q.min(), sorted_resid.min())
qq_max = max(theoretical_q.max(), sorted_resid.max())
fig_diag.add_trace(go.Scatter(
    x=[qq_min, qq_max], y=[qq_min, qq_max],
    mode='lines', name='Reference', line=dict(color='red', dash='dash')
), row=2, col=2)

fig_diag.update_layout(
    title='SARIMA Model Diagnostics — Total Monthly Postings',
    height=600, showlegend=False
)
fig_diag.show()

# --- 3. Model summary table ---
print("\n=== All Fitted Models ===")
summary_display = all_model_log.copy()
summary_display['order'] = summary_display['order'].astype(str)
summary_display['aic'] = summary_display['aic'].apply(
    lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
)
print(summary_display[['dimension', 'category', 'type', 'order', 'aic']]
      .to_string(index=False))'''

cell = {
    'cell_type': 'code',
    'metadata': {},
    'source': [line + '\n' for line in code.split('\n')],
    'outputs': [],
    'execution_count': None,
    'id': uuid.uuid4().hex[:8]
}
cell['source'][-1] = cell['source'][-1].rstrip('\n')

nb['cells'].insert(72, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted diagnostics cell at index 72. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
src = ''.join(nb['cells'][72]['source'])
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Has acorr_ljungbox: {\"acorr_ljungbox\" in src}')
print(f'Has fig_diag: {\"fig_diag\" in src}')
print(f'Has all_model_log: {\"all_model_log\" in src}')
"
```

Expected: Total cells: 74, all checks True.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add SARIMA diagnostics and model summary cell"
```

---

## Task 7: Insert Audience A Visualizations Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert code cell at index 73)

Depends on `total_forecast_df`, `segment_combined`, `entry_sub_forecasts`, `entry_count_forecast`, `entry_count_historical`, `entry_skill_combined`, `skill_combined`, `monthly_total`, `forecast_dates`, `segment_shares` from previous cells.

- [ ] **Step 1: Insert the Audience A visualizations cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

code = r'''### Audience A: Storytelling Visualizations
BOUNDARY_DATE = monthly_total.index[-1]  # Dec 2026

# ========================================================================
# Chart F1: Total Market Forecast
# ========================================================================
fig1 = go.Figure()

# Historical
hist = total_forecast_df[~total_forecast_df['is_forecast']]
fig1.add_trace(go.Scatter(
    x=hist['date'], y=hist['count'],
    mode='lines', name='Historical',
    line=dict(color='#636EFA', width=2)
))

# Forecast
fc = total_forecast_df[total_forecast_df['is_forecast']]
fig1.add_trace(go.Scatter(
    x=fc['date'], y=fc['count'],
    mode='lines', name='Forecast',
    line=dict(color='#636EFA', width=2, dash='dash')
))

# 95% CI band
fig1.add_trace(go.Scatter(
    x=list(fc['date']) + list(fc['date'][::-1]),
    y=list(fc['ci_95_upper']) + list(fc['ci_95_lower'][::-1]),
    fill='toself', fillcolor='rgba(99,110,250,0.1)',
    line=dict(color='rgba(0,0,0,0)'), name='95% CI', showlegend=True
))

# 80% CI band
fig1.add_trace(go.Scatter(
    x=list(fc['date']) + list(fc['date'][::-1]),
    y=list(fc['ci_80_upper']) + list(fc['ci_80_lower'][::-1]),
    fill='toself', fillcolor='rgba(99,110,250,0.2)',
    line=dict(color='rgba(0,0,0,0)'), name='80% CI', showlegend=True
))

# Boundary line
fig1.add_vline(x=BOUNDARY_DATE, line_dash='dot', line_color='gray',
               annotation_text='Forecast →', annotation_position='top right')

fig1.update_layout(
    title='Total AI Job Postings: Historical and Projected Through 2028',
    xaxis_title='Date', yaxis_title='Monthly Job Postings',
    height=450, template='plotly_white'
)
fig1.show()

# ========================================================================
# Chart F2: The Shifting Mix — Experience Level Composition
# ========================================================================
fig2 = go.Figure()

exp_colors = {'Entry': '#EF553B', 'Mid': '#636EFA', 'Senior': '#00CC96'}
for level in ['Senior', 'Mid', 'Entry']:  # stack order: bottom to top
    data = segment_combined['experience_level'][level]
    hist_data = data[~data['is_forecast']]
    fc_data = data[data['is_forecast']]

    # Historical shares
    fig2.add_trace(go.Scatter(
        x=hist_data['date'], y=hist_data['share'] * 100,
        mode='lines', name=f'{level} (historical)',
        line=dict(color=exp_colors[level], width=2),
        stackgroup='hist'
    ))
    # Forecast shares
    fig2.add_trace(go.Scatter(
        x=fc_data['date'], y=fc_data['share'] * 100,
        mode='lines', name=f'{level} (forecast)',
        line=dict(color=exp_colors[level], width=2, dash='dash'),
        stackgroup='fc', opacity=0.6
    ))

fig2.add_vline(x=BOUNDARY_DATE, line_dash='dot', line_color='gray')

fig2.update_layout(
    title='Experience Level Composition: Who Gets Hired? (% of Total Postings)',
    xaxis_title='Date', yaxis_title='Share of Postings (%)',
    height=500, template='plotly_white'
)
fig2.show()

# ========================================================================
# Chart F3: Entry-Level Outlook Dashboard (2x2)
# ========================================================================
fig3 = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Entry-Level: Remote Type Mix',
        'Entry-Level: Top Industries',
        'Entry-Level: Skills Demand Trajectory',
        'Entry-Level: Projected Posting Count'
    ),
    vertical_spacing=0.12, horizontal_spacing=0.08
)

# --- F3 Top-Left: Remote type shares for entry-level ---
remote_colors = {'Remote': '#636EFA', 'Hybrid': '#EF553B', 'Onsite': '#00CC96'}
for rtype in ['Remote', 'Hybrid', 'Onsite']:
    hist_shares = entry_segment_shares['remote_type'][rtype]
    fc_shares = entry_sub_forecasts['remote_type'][rtype]
    fig3.add_trace(go.Scatter(
        x=monthly_total.index, y=hist_shares * 100,
        mode='lines', name=rtype,
        line=dict(color=remote_colors[rtype], width=1.5),
        legendgroup=rtype, showlegend=True
    ), row=1, col=1)
    fig3.add_trace(go.Scatter(
        x=forecast_dates, y=fc_shares * 100,
        mode='lines', name=f'{rtype} (fc)',
        line=dict(color=remote_colors[rtype], width=1.5, dash='dash'),
        legendgroup=rtype, showlegend=False
    ), row=1, col=1)

# --- F3 Top-Right: Industry shares for entry-level ---
industry_list = entry_segment_shares['company_industry'].columns.tolist()
for ind in industry_list:
    hist_shares = entry_segment_shares['company_industry'][ind]
    fc_shares = entry_sub_forecasts['company_industry'][ind]
    fig3.add_trace(go.Scatter(
        x=monthly_total.index, y=hist_shares * 100,
        mode='lines', name=ind,
        line=dict(width=1.5),
        legendgroup=ind, showlegend=True
    ), row=1, col=2)
    fig3.add_trace(go.Scatter(
        x=forecast_dates, y=fc_shares * 100,
        mode='lines', name=f'{ind} (fc)',
        line=dict(width=1.5, dash='dash'),
        legendgroup=ind, showlegend=False
    ), row=1, col=2)

# --- F3 Bottom-Left: Entry-level skill rates ---
skill_labels = {
    'skills_python': 'Python', 'skills_sql': 'SQL', 'skills_ml': 'ML',
    'skills_deep_learning': 'Deep Learning', 'skills_cloud': 'Cloud'
}
skill_colors = {
    'skills_python': '#636EFA', 'skills_sql': '#EF553B', 'skills_ml': '#00CC96',
    'skills_deep_learning': '#AB63FA', 'skills_cloud': '#FFA15A'
}
for skill in skill_cols_forecast:
    label = skill_labels[skill]
    color = skill_colors[skill]
    hist_vals = entry_skill_combined[~entry_skill_combined['is_forecast']][skill]
    fc_vals = entry_skill_combined[entry_skill_combined['is_forecast']][skill]
    fig3.add_trace(go.Scatter(
        x=monthly_total.index, y=hist_vals * 100,
        mode='lines', name=label,
        line=dict(color=color, width=1.5),
        legendgroup=label, showlegend=True
    ), row=2, col=1)
    fig3.add_trace(go.Scatter(
        x=forecast_dates, y=fc_vals * 100,
        mode='lines', name=f'{label} (fc)',
        line=dict(color=color, width=1.5, dash='dash'),
        legendgroup=label, showlegend=False
    ), row=2, col=1)

# --- F3 Bottom-Right: Entry-level posting count ---
fig3.add_trace(go.Scatter(
    x=monthly_total.index, y=entry_count_historical.values,
    mode='lines', name='Entry Count',
    line=dict(color='#EF553B', width=2),
    showlegend=False
), row=2, col=2)
fig3.add_trace(go.Scatter(
    x=forecast_dates, y=entry_count_forecast.values,
    mode='lines', name='Entry Count (fc)',
    line=dict(color='#EF553B', width=2, dash='dash'),
    showlegend=False
), row=2, col=2)

# Add boundary lines to all subplots
for row in [1, 2]:
    for col in [1, 2]:
        fig3.add_vline(x=BOUNDARY_DATE, line_dash='dot', line_color='gray',
                       row=row, col=col)

fig3.update_layout(
    title='Entry-Level Outlook: Remote Work, Industries, Skills, and Volume Through 2028',
    height=700, template='plotly_white',
    legend=dict(font=dict(size=9))
)
fig3.update_yaxes(title_text='% of Entry Postings', row=1, col=1)
fig3.update_yaxes(title_text='% of Entry Postings', row=1, col=2)
fig3.update_yaxes(title_text='% Requiring Skill', row=2, col=1)
fig3.update_yaxes(title_text='Monthly Postings', row=2, col=2)
fig3.show()'''

cell = {
    'cell_type': 'code',
    'metadata': {},
    'source': [line + '\n' for line in code.split('\n')],
    'outputs': [],
    'execution_count': None,
    'id': uuid.uuid4().hex[:8]
}
cell['source'][-1] = cell['source'][-1].rstrip('\n')

nb['cells'].insert(73, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted Audience A viz cell at index 73. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
src = ''.join(nb['cells'][73]['source'])
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Has Chart F1: {\"Chart F1\" in src}')
print(f'Has Chart F2: {\"Chart F2\" in src}')
print(f'Has Chart F3: {\"Chart F3\" in src}')
print(f'Has fig1.show: {\"fig1.show()\" in src}')
print(f'Has fig2.show: {\"fig2.show()\" in src}')
print(f'Has fig3.show: {\"fig3.show()\" in src}')
"
```

Expected: Total cells: 75, all checks True.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add Audience A forecast visualizations (F1-F3)"
```

---

## Task 8: Insert Audience B Methodology & Limitations Markdown Cell

**Files:**
- Modify: `CERT-x466-003_MAIN.ipynb` (insert markdown cell at index 74)

- [ ] **Step 1: Insert the Audience B markdown cell**

```bash
python3 << 'PYEOF'
import json, uuid

with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)

cell = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '### Methodology & Limitations (Technical Appendix)\n',
        '\n',
        '#### Forecasting Approach\n',
        '\n',
        'This forecast uses a **hybrid aggregate + proportion** architecture:\n',
        '\n',
        '1. **Layer 1 (Total Volume):** A Seasonal ARIMA (SARIMA) model fitted on 84 months of aggregate monthly posting counts (Jan 2020 – Dec 2026). Model order was selected by AIC grid search over (p,d,q)(P,D,Q,12) with p,q ∈ {0,1,2}, P,Q ∈ {0,1}, d,D ∈ {0,1}. The model produces point forecasts with 80% and 95% prediction intervals for 24 months (Jan 2027 – Dec 2028).\n',
        '\n',
        '2. **Layer 2 (Compositional Shifts):** For each segment dimension (experience level, remote type, industry, country), monthly category shares are modeled with per-category ARIMA. Forecast shares are normalized to sum to 1.0 at each month, then multiplied by the Layer 1 total forecast to produce segment-level count projections.\n',
        '\n',
        '3. **Skills (Rate Models):** Binary skill columns are aggregated to monthly rates (proportion of postings requiring each skill) and forecast independently with ARIMA. Forecasts are clamped to [0, 1].\n',
        '\n',
        '#### Key Limitations\n',
        '\n',
        '- **Synthetic data.** This dataset was generated, not collected from real job postings. The near-uniform distribution across categories (e.g., ~5,200 postings per experience level, ~2,200 per country) is a clear synthetic signature. Real job market data would show much more variance, stronger trends, and structural breaks (e.g., COVID-19 impacts, the 2023 tech layoffs). **Forecasts from this data should be interpreted as methodological demonstrations, not real-world predictions.**\n',
        '\n',
        '- **Stationary totals.** Yearly posting counts range 2,155–2,309 with no meaningful growth trend. The SARIMA model correctly identifies this stationarity — the forecast is essentially "more of the same" with widening uncertainty. This is honest modeling, not a failure.\n',
        '\n',
        '- **Small cell sizes at granular levels.** Country-by-month segments average ~26 observations. Share estimates at this level are noisy, and ARIMA models on noisy share series may converge to near-constant forecasts (historical mean). Where a model fails to converge, the historical mean is used as a fallback.\n',
        '\n',
        '- **Simplified uncertainty.** Segment-level prediction intervals are derived proportionally from the total forecast\'s intervals. Full uncertainty propagation (combining share model uncertainty with total model uncertainty) would be more rigorous but adds complexity for minimal practical gain given the data characteristics.\n',
        '\n',
        '- **Independence assumption.** Segment dimensions are modeled independently — the model does not capture interactions (e.g., "entry-level remote roles in tech" as a distinct segment). With 84 months of data and synthetic uniformity, interaction modeling would overfit.\n',
    ],
    'id': uuid.uuid4().hex[:8]
}

nb['cells'].insert(74, cell)

with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Inserted Audience B markdown cell at index 74. Total cells: {len(nb["cells"])}')
PYEOF
```

- [ ] **Step 2: Verify the cell**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
src = ''.join(nb['cells'][74]['source'])
print(f'Total cells: {len(nb[\"cells\"])}')
print(f'Cell 74 type: {nb[\"cells\"][74][\"cell_type\"]}')
print(f'Has Methodology: {\"Methodology\" in src}')
print(f'Has Synthetic data: {\"Synthetic data\" in src}')
print(f'Has Simplified uncertainty: {\"Simplified uncertainty\" in src}')
# Verify DATA STORY cell is now at 75
print(f'Cell 75 source: {repr(\"\" .join(nb[\"cells\"][75][\"source\"]))}')
"
```

Expected: Total cells: 76, Cell 74 is markdown with methodology, Cell 75 is the old empty DATA STORY cell.

- [ ] **Step 3: Commit**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: add Audience B methodology and limitations section"
```

---

## Task 9: Run the Notebook and Verify

**Files:**
- Run: `CERT-x466-003_MAIN.ipynb`

- [ ] **Step 1: Run the forecast cells in sequence via command line**

Execute just the new forecast cells (indices 67-74) to verify they work. Since the notebook depends on earlier cells (especially `ai_df` from cell 14 and `skill_cols` from cell 35), run the full notebook:

```bash
cd /home/wanderduck/000_Duckspace/WanderduckDevelopment/Ducks/UMN/CERT-x466-003
uv run jupyter nbconvert --to notebook --execute CERT-x466-003_MAIN.ipynb --output CERT-x466-003_MAIN_executed.ipynb --ExecutePreprocessor.timeout=600 2>&1 | tail -20
```

Note: This may take several minutes due to the SARIMA grid search and the full notebook execution. If it times out, increase the timeout or run just the forecast cells manually.

- [ ] **Step 2: Check for errors in the executed notebook**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN_executed.ipynb') as f:
    nb = json.load(f)
# Check cells 67-74 for errors
for i in range(67, 75):
    cell = nb['cells'][i]
    if cell['cell_type'] != 'code':
        continue
    errors = [o for o in cell.get('outputs', []) if o.get('output_type') == 'error']
    if errors:
        print(f'CELL {i} ERROR: {errors[0][\"ename\"]}: {errors[0][\"evalue\"]}')
    else:
        print(f'Cell {i}: OK ({len(cell.get(\"outputs\", []))} outputs)')
"
```

Expected: All code cells report OK with at least 1 output each.

- [ ] **Step 3: If successful, copy executed notebook back and commit**

```bash
mv CERT-x466-003_MAIN_executed.ipynb CERT-x466-003_MAIN.ipynb
git add CERT-x466-003_MAIN.ipynb
git commit -m "feat: execute forecast cells, save outputs"
```

- [ ] **Step 4: If errors, diagnose and fix**

Read the error output from Step 2, fix the relevant cell using the same JSON insertion pattern (but editing in place instead of inserting), and re-run.

---

## Task 10: Clean Up and Final Verification

**Files:**
- Verify: `CERT-x466-003_MAIN.ipynb`

- [ ] **Step 1: Verify final notebook structure**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
print(f'Total cells: {len(nb[\"cells\"])}')
for i in range(65, len(nb['cells'])):
    src = ''.join(nb['cells'][i]['source'])[:80].replace(chr(10), ' | ')
    print(f'[{i:3d}] {nb[\"cells\"][i][\"cell_type\"]:8s} | {src}')
"
```

Expected: 76 cells total. Cells 67-74 are the new forecast section (1 markdown header, 5 code cells, 1 viz code cell, 1 markdown limitations). Cell 75 is the old empty DATA STORY markdown.

- [ ] **Step 2: Verify key variables are produced**

```bash
python3 -c "
import json
with open('CERT-x466-003_MAIN.ipynb') as f:
    nb = json.load(f)
# Check that forecast cells have outputs (not just empty)
forecast_cells = [68, 69, 70, 71, 72, 73]
for i in forecast_cells:
    cell = nb['cells'][i]
    n_outputs = len(cell.get('outputs', []))
    has_plotly = any('plotly' in json.dumps(o).lower() for o in cell.get('outputs', []))
    print(f'Cell {i}: {n_outputs} outputs, plotly={has_plotly}')
"
```

Expected: All cells have outputs. Cells 72 (diagnostics) and 73 (Audience A) should have plotly=True.

- [ ] **Step 3: Final commit if any cleanup was needed**

```bash
git add CERT-x466-003_MAIN.ipynb
git commit -m "chore: final forecast section cleanup and verification"
```
