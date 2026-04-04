# Job Posting Forecast Model — Design Spec

**Date**: 2026-04-03
**Project**: CERT x466-003 Data Storytelling
**Purpose**: Build a hybrid forecasting model that projects AI job postings through Dec 2028, serving both as a technical demonstration and a narrative tool for the data story.

---

## 1. Context

### Data Characteristics
- **Source**: `data/boot_ai_job_market_dataset.csv` (15,518 rows, synthetic)
- **Time range**: Jan 2020 – Dec 2026 (84 months, all 12 months of 2026 present)
- **Forecast horizon**: Jan 2027 – Dec 2028 (24 months)
- **Key observation**: The data is near-stationary. Yearly totals range 2,155–2,309 with no meaningful growth trend. Monthly counts average ~185 with std ~22. This flatness is characteristic of synthetic data and must be acknowledged transparently.

### Segment Dimensions (all to be forecasted)
| Dimension | Categories | Monthly cell size (mean) |
|---|---|---|
| Experience level | Entry, Mid, Senior (3) | ~62 |
| Remote type | Remote, Hybrid, Onsite (3) | ~62 |
| Industry | Technology, Healthcare, Finance, E-commerce, Retail, Education (6) | ~31 |
| Country | USA, UK, Canada, Germany, India, Australia, Singapore (7) | ~26 |
| Skills | Python, SQL, ML, Deep Learning, Cloud (5 binary columns) | N/A (rates) |

### Existing Work
- **ML5 (cell 60)**: Linear trend + YoY growth analysis on annual totals. The new forecast builds on this with monthly granularity and compositional modeling.
- **Dependencies**: `statsmodels 0.14.6` (already installed). No Prophet (not installed, heavy dependency).

---

## 2. Architecture: Hybrid Aggregate + Proportion Model

### Layer 1 — Total Postings Forecast (SARIMA)
- Model: `statsmodels.tsa.statespace.SARIMAX` on the 84-month aggregate series
- Order selection: Grid search over (p,d,q)(P,D,Q,12) with p,q in [0,2], P,Q in [0,1], d in [0,1], D in [0,1]. Select by lowest AIC.
- Expected outcome: Low-order model (likely d=0 given stationarity), near-flat forecast with widening prediction intervals
- Output: 24-month point forecast + 80% and 95% prediction intervals

### Layer 2 — Proportion Forecasts
For each segment dimension (experience level, remote type, industry, country):
1. Compute monthly share = category_count / total_count for each category
2. Fit ARIMA on each category's share series (low order, auto-selected by AIC over a small grid)
3. Forecast 24 months of shares
4. **Normalize**: At each forecast month, divide each category's share by the sum of all category shares so they sum to 1.0
5. Multiply: `segment_count_forecast = total_forecast × normalized_share_forecast`
6. **Fallback**: If an individual ARIMA fails to converge, use the historical mean share for that category

### Skills Rate Forecasts
- Compute monthly rate = `mean()` of each binary skill column per month
- Fit ARIMA on each rate series independently
- Clamp forecasts to [0, 1]
- These are independent proportions (not a partition), so no normalization needed

### Uncertainty Propagation
- Report the total forecast's prediction intervals applied proportionally to each segment
- Full error propagation (combining share uncertainty with total uncertainty) is omitted — it adds complexity for minimal gain with near-stationary data

---

## 3. Notebook Structure

New cells inserted after cell 66 (PyTorch Integrated Gradients), before the DATA STORY section (cell 67).

| Cell | Type | Content |
|---|---|---|
| New 1 | markdown | Section header: `## FORECASTING — Job Market Projections Through 2028`. Brief intro explaining the hybrid approach. |
| New 2 | code | **Forecast preparation**: Build monthly time series from `ai_df`. Construct proportion series for each dimension. Construct skill rate series. |
| New 3 | code | **Layer 1: Total SARIMA**: Order selection grid search, fit best model, generate 24-month forecast with prediction intervals. Print model summary. |
| New 4 | code | **Layer 2: Proportion forecasts**: Loop over dimensions. Fit per-category ARIMA, forecast shares, normalize, multiply by total. Collect results into DataFrames. |
| New 5 | code | **Skills rate forecasts**: Fit ARIMA per skill, forecast rates, clamp to [0,1]. |
| New 6 | code | **Diagnostics & summary**: Residual analysis for total model. Summary table of all models (order, AIC). |
| New 7 | code | **Audience A visualizations**: 4 Plotly charts (total forecast, composition shift, entry-level dashboard, key findings). |
| New 8 | markdown | **Audience B: Methodology & Limitations**: Model selection rationale, synthetic data caveats, small cell size discussion, interpretation guidance. |

---

## 4. Visualizations

### Audience A — Storytelling Charts

**Chart F1: Total Market Forecast**
- Line chart: historical monthly postings (solid) transitioning to forecast (dashed)
- Shaded bands for 80% (darker) and 95% (lighter) prediction intervals
- Vertical line at Dec 2026 marking the historical/forecast boundary
- Takeaway annotation: market trajectory summary

**Chart F2: The Shifting Mix — Experience Level Composition**
- Stacked area chart showing Entry/Mid/Senior as % of total, 2020–2028
- Historical region: full opacity. Forecast region: reduced opacity
- Centerpiece chart — shows whether entry-level share is growing, shrinking, or stable

**Chart F3: Entry-Level Outlook Dashboard**
- 2x2 Plotly subplot grid:
  - Top-left: Remote type share forecast for entry-level roles
  - Top-right: Top industries for entry-level hiring (projected shares)
  - Bottom-left: Skills demand trajectory (5 lines: Python, SQL, ML, DL, Cloud)
  - Bottom-right: Entry-level postings count forecast with confidence interval
- Each subplot shows historical (solid) + forecast (dashed) with the boundary line

**Key Findings Callouts (embedded in F1–F3, not a separate chart)**
- Add Plotly annotations directly onto Charts F1, F2, and F3 highlighting the 2–3 most notable projected shifts
- Examples: arrows pointing to crossover points in composition, callout boxes with plain-language takeaways
- Tied to the narrative arc from Assignment 03

### Audience B — Methodology

**Table F5: Model Summary**
- HTML-rendered table: each model's dimension, category, ARIMA order, AIC, one-line interpretation

**Chart F6: Diagnostics Panel**
- 2x2 subplot for the total postings SARIMA model: residuals over time, ACF of residuals, histogram of residuals, Q-Q plot

**Markdown F7: Limitations**
- Synthetic data caveat and what it means for forecast credibility
- Flat-trend implications (the forecast is "more of the same" by design)
- Small cell sizes for country-level and industry-level segments
- Uncertainty propagation simplification

---

## 5. Technical Details

### Color Scheme
Consistent with existing notebook charts:
- Primary: `#636EFA` (blue)
- Secondary: `#EF553B` (red)
- Additional Plotly defaults for multi-category charts

### Dependencies
- `statsmodels` (already installed, v0.14.6) — SARIMAX, acf/pacf, diagnostic plots
- `scipy.stats` — Q-Q plot data
- No new packages required

### Data Flow
```
ai_df (raw dataset)
  |
  +-> monthly_total (84-point time series)
  |     |-> SARIMA fit -> 24-month total forecast + PIs
  |
  +-> monthly_shares[dimension][category] (84-point share series each)
  |     |-> ARIMA fit per category -> 24-month share forecasts
  |     |-> Normalize across categories per month
  |     |-> Multiply by total forecast -> segment count forecasts
  |
  +-> monthly_skill_rates[skill] (84-point rate series each)
        |-> ARIMA fit per skill -> 24-month rate forecasts
        |-> Clamp to [0, 1]
```

### ARIMA Order Selection Grid
- Total SARIMA: p in [0,2], d in [0,1], q in [0,2], P in [0,1], D in [0,1], Q in [0,1], s=12
- Proportion/rate ARIMA: p in [0,2], d in [0,1], q in [0,2] (non-seasonal, as shares may not exhibit strong seasonality)
- Selection criterion: AIC (with convergence check)
- Suppress convergence warnings during grid search; log failed fits

### Entry-Level Cross-Dimension Forecasts
For Chart F3, entry-level breakdowns by remote type and industry are modeled as proportions within the entry-level subset specifically (not the overall population). This means:
1. Filter to `experience_level == 'Entry'`
2. Compute monthly shares of remote type and industry within entry-level postings
3. Forecast those shares
4. Multiply by the entry-level count forecast (from Layer 2)
