import os

report_content = """# AI Job Market Dataset Analysis

## Executive Summary
This report presents a comprehensive analysis of the AI Job Market dataset (`boot_ai_job_market_dataset.csv`). The analysis pipeline was divided into three main stages: Exploratory Data Analysis (EDA), Machine Learning & Deep Learning (ML & DL) evaluation, and Time Series Forecasting. This document synthesizes the findings from these analytical phases, focusing on trends relevant to entry-level candidates entering the AI field.

---

## Part 1: Exploratory Data Analysis (EDA)
*Prepared by Agent 1 (Reviewer) and Agent 2 (Writer)*

### 1.1 Overview & Salary Trends
The EDA phase generated 31 distinct visualizations exploring the distribution of salaries, experience levels, and skills across the AI job market.
*   **Overall Distribution:** The target variable, salary, exhibits a right-skewed distribution.
*   **Salary vs. Experience:** There is a clear positive correlation between years of experience and salary. Senior roles command the highest median salaries, while entry-level salaries form the baseline distribution. 
*   **Remote Work:** The data analyzes variations across 'Remote', 'Hybrid', and 'Onsite' work setups, mapping changes over time. Remote roles frequently compete with or exceed onsite compensation depending on the experience level.
*   **Geography:** Salaries vary significantly by country, reflecting differences in local tech economies and cost-of-living adjustments.

### 1.2 Temporal Trends & Market Growth
*   **Postings Over Time:** The dataset tracks job postings from 2020 through the beginning of 2026. The job market experienced notable growth in 2023 (+28.7% overall, +31.6% for entry-level) but flattened out in 2024 and 2025.
*   **2026 Surge:** Based on annualized data for Q1 2026, the market is pacing for massive growth, potentially +80.3% overall and +71.7% for entry-level roles specifically. 
*   **Seasonality:** An analysis of postings per month highlights seasonal hiring patterns, providing actionable insight for when entry-level candidates should be applying for roles.

### 1.3 Skill Requirements
*   **Evolving Demand:** The breakdown of required skills (Python, SQL, ML, Deep Learning, Cloud) reveals shifting technical demands over time.
*   **Experience Nuance:** Entry-level roles prioritize baseline skills (e.g., Python and SQL), whereas mid-to-senior roles heavily index on advanced architectures (Deep Learning) and infrastructure (Cloud).

---

## Part 2: Machine Learning & Deep Learning
*Prepared by Agent 3 (Reviewer) and Agent 4 (Writer)*

### 2.1 Salary Prediction Models
Three primary models were evaluated to predict the continuous `salary` variable:
1.  **Gradient Boosting (sklearn):** Achieved the best performance with an $R^2$ of 0.375, a Mean Absolute Error (MAE) of $21,259, and an RMSE of $29,649.
2.  **Random Forest (cuML):** Performed similarly with an $R^2$ of 0.347 and an MAE of $22,002.
3.  **Linear Regression (cuML):** Severely underperformed with an $R^2$ of 0.182, proving that the relationships within the dataset are non-linear.

### 2.2 Categorical Classification
Random Forest models (accelerated via cuML) were tasked with predicting discrete job features:
*   **Experience Level Prediction:** Achieved 65.5% accuracy. The model was highly capable of identifying Entry-level roles (F1-score: 0.81) but struggled to distinguish between Mid-level (F1-score: 0.52) and Senior roles (F1-score: 0.68).
*   **Hiring Urgency:** Achieved 56.8% accuracy. The model was heavily skewed towards predicting 'High' urgency (F1: 0.72) and performed poorly on 'Low' and 'Medium'.
*   **Remote Type:** Achieved 48.6% accuracy, indicating that remote/hybrid/onsite designations are not easily inferred from standard tabular features like industry or company size alone.

### 2.3 Deep Learning & Advanced Techniques
*   **Autoencoder Anomaly Detection (Keras):** A deep neural network was trained to reconstruct job postings to identify "structurally unusual" entries based on Mean Squared Error (MSE). The model stopped at epoch 34 with a scaled validation MSE of 0.6716.
*   **Entity Embeddings (Keras):** Used to map and learn the hidden geometric relationships between different job categories.
*   **Integrated Gradients (PyTorch):** A PyTorch MLP was built to attribute per-feature impacts to salary predictions (MAE: $22,156, $R^2$: 0.3383). Using Integrated Gradients, the analysis demonstrated that while random forests output a global feature importance, neural networks map *how* feature importance shifts across subgroups (e.g., 'years_experience' driving senior salaries vs 'education_level' driving entry salaries).

---

## Part 3: Time Series Forecasting
*Prepared by Agent 5 (Reviewer) and Agent 6 (Writer)*

### 3.1 Overall Market Projection
The forecasting section utilized 75 months of historical data (Jan 2020 - Mar 2026) to project 33 months into the future (Apr 2026 - Dec 2028).
*   **Model Selected:** SARIMA(0, 1, 2)x(0, 1, 1, 12). The model achieved an AIC of 513.8.
*   **Prediction:** The model forecasts significant sustained growth in the AI job market. The predicted monthly average for the 2026-2028 horizon is 507 job postings per month, compared to the historical average of 225.
*   **Diagnostics:** Residual diagnostics (Ljung-Box p-value: 0.0000) indicated some remaining autocorrelation, suggesting market volatility or exogenous shocks not perfectly captured by the univariate model.

### 3.2 Sub-Category Forecasts
Proportion models were fit across categorical dimensions to estimate the future composition of the job market:
*   **Experience Level:** Entry, Mid, and Senior-level shares were forecasted using ARMA-based share models to track whether the market will lean more senior or open up to juniors.
*   **Remote Type:** Forecasts for Remote, Hybrid, and Onsite roles mapped out the long-term structural shift in work environments post-2025.
*   **Industry & Geography:** Projected which specific industries (e.g., Technology, Finance, Education) and countries will drive the most hiring volume through 2028.
*   **Skill Demand:** Forecasted the expected requirement rates for 5 distinct skill vectors.

---

## Conclusion
The AI job market demonstrates a clear trajectory of high-volume growth heading into the late 2020s. While salary modeling proves that compensation is highly non-linear and dependent on nuanced feature intersections (best predicted via Gradient Boosting), the time-series forecasting indicates that opportunity volume itself will more than double its historical baseline. For entry-level applicants, the data emphasizes the importance of mastering core technical prerequisites, targeting specific high-growth months, and aligning with industries showing the highest long-term forecasted share of junior postings.
"""

os.makedirs('docs/reports', exist_ok=True)
with open('docs/reports/ai_job_market_dataset_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(report_content)

print("Report successfully generated at docs/reports/ai_job_market_dataset_analysis_report.md")
