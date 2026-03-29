# **Assignment 03**
- Completed by: Logan R. Sloan

## **Assignment Details**
In this assignment, you will start to develop your data story using the data that you found and begin to analyze in Module 2. You will first define the objectives and audience of your data story, and then start to build out the narrative.

- **Part 1: Objectives and Audience**
    - What is the purpose of this data story? Define 1-2 clear objectives that you hope the data story will achieve. If your story is intended to influence decisions, make sure you describe what decisions it might influence.
    - Who are the intended audience(s) for the data story you’re considering?
    - What do you know about these audiences, and how will that impact the way that you might prepare and present the data story?
- **Part 2: Narrative**
    - Create an outline of your data story narrative that includes the key points and the data that you will use to make those key points

## **Assignment Submission**
### **Part 1: Objectives and Audience Submission**

#### Purpose and Objectives

The purpose of this data story is to give people who are about to enter the AI job market — recent graduates, career changers, and early-career professionals — a practical, evidence-based picture of what that market actually looks like and where it appears to be heading. Rather than relying on hype or anecdote, I want to ground the narrative in what 15,518 job postings from 2020 through 2026 actually reveal.

- **Objective 1: Clarify what entry-level AI roles realistically demand and offer.** The dataset lets me show how salaries break down by experience level, which skills appear most frequently in entry-level postings, and how factors like remote work, company size, and industry shift the picture. My EDA surfaces concrete findings here — the salary-by-experience box plots, skills-by-experience-level breakdowns, and the education-versus-experience salary heatmap all speak directly to someone wondering "What should I expect, and what should I prioritize learning?" This objective is meant to influence preparation decisions: which skills to invest in, what salary range to target, and whether to focus on remote, hybrid, or onsite roles.
- **Objective 2: Identify trends that signal where entry-level opportunity is growing or shrinking.** The time-series charts — experience level distribution over time, entry-level postings by month, entry-level share of total postings, industry hiring trends, and the ML-based job market growth analysis — let me move beyond a static snapshot and show direction. If entry-level postings are becoming a larger or smaller share of the market, or if certain industries are accelerating their junior hiring, that matters for someone deciding when to enter the market and which sectors to target. This objective is meant to influence timing and positioning decisions.

#### Intended Audiences

I have two primary audiences in mind:

- **Audience A: Aspiring AI professionals with little to no work experience.** This includes students finishing degrees in data science, computer science, or adjacent fields, as well as people pivoting from other careers through bootcamps or self-study. They are the people the project is fundamentally for.
- **Audience B: Career advisors, bootcamp instructors, and university program coordinators** who guide Audience A. These people need credible, up-to-date information about market conditions so their advice stays grounded in reality rather than lagging indicators.

#### How Audience Knowledge Shapes Presentation

- **Audience A** is generally data-literate enough to read a chart but not necessarily experienced with statistical modeling. They are motivated and action-oriented — they want to know what to *do*, not just what is interesting. They are also likely skeptical of overly rosy narratives about AI careers, because they have seen plenty of those. This means I need to:

    - Lead with clear, interactive visualizations (Plotly) rather than dense tables or raw model outputs. The salary distributions, skill trend lines, and seasonal hiring patterns should be visually intuitive.
    - Translate ML results into plain-language takeaways. Saying "the Random Forest achieved R² = 0.996 on salary prediction" matters less to this audience than saying "years of experience and skill set are by far the strongest predictors of salary, and here is how that breaks down for entry-level roles specifically." The Integrated Gradients attribution analysis is particularly useful here because it shows *which features matter most* at the entry level versus other tiers.
    - Be honest about limitations. The dataset is synthetic, and I need to say so clearly. Credibility with a skeptical audience depends on transparency.

- **Audience B** is comfortable with more methodological detail and wants to know *how confident* they should be in the findings before passing them along as guidance. For this audience, I will include a section on methodology — the ML model performance metrics, the forecasting approach, and the caveats around synthetic data — so they can evaluate the rigor themselves. I also plan to structure the story so the high-level narrative works on its own for Audience A, while the supporting technical detail is accessible but not in the way for Audience B.

    - In practice, this means a layered presentation: lead with the story and the visuals, back it up with the models and the numbers, and be upfront about what the data can and cannot tell us.

---
### **Part 2: Narrative Submission**
#### Data Story Narrative: Breaking Into AI — What the Job Market Actually Tells New Entrants
##### I. Hook — The AI Gold Rush Has a Gate
- Everyone hears that AI is booming and hiring is through the roof. But if you are someone without years of experience trying to break in, the picture is more complicated than the headlines suggest. Using a dataset of over 15,000 job postings from 2020 through 2026, I set out to answer a simple question: what does the AI job market actually look like for people just getting started?

---
##### II. Context — The Landscape Is Growing, But Unevenly

- **Key Point 1: The AI job market is expanding rapidly, but growth is not uniform across experience levels.**
    - The total volume of job postings has climbed year over year (**EDA Chart 10**), and industry hiring trends confirm that growth spans multiple sectors, not just tech (**EDA Chart 19**). However, when we break postings down by experience level over time, the share allocated to entry-level roles has not kept pace with mid and senior demand (**EDA Chart 9, EDA Chart 25**). A dedicated view of the entry-level share of total postings over time (**EDA Chart 30**) makes this divergence unmistakable. The market is growing, but the door for newcomers is not opening as wide as the overall numbers imply.

- **Key Point 2: Salary expectations need to be grounded in reality.**
    - The overall salary distribution is broad (**EDA Chart 1**), and the gap between experience levels is stark. Entry-level salaries cluster well below mid and senior ranges (**EDA Chart 2**), and the scatter of salary against years of experience shows a clear ramp that steepens after the first few years (**EDA Chart 3**). For someone entering the market, understanding this baseline prevents discouragement and sets realistic financial planning targets.

---
##### III. Entry-Level Deep Dive — What the Data Says About Getting Your Foot in the Door

- **Key Point 3: Seasonal hiring patterns create windows of opportunity for entry-level candidates.**
    - Monthly posting volumes reveal seasonal rhythms in the broader market (**EDA Chart 16**), and when we isolate entry and junior-level postings specifically, those rhythms sharpen into identifiable hiring windows (**EDA Chart 17**). Timing an application push around these peaks is a concrete, data-backed strategy.

- **Key Point 4: The skills that matter most at the entry level are not the same as those that dominate senior roles.**
    - Skill requirements have shifted over time (**EDA Chart 13**), and an entry-level-specific view of those trends confirms that the skills demanded of juniors have their own trajectory (**EDA Chart 29**). The breakdown by experience level tells the real story: Python and SQL dominate entry-level requirements, while deep learning and cloud skills become more critical at the senior level (**EDA Chart 14, EDA Chart 15**). For a new entrant, this means prioritizing foundational technical fluency over chasing advanced specializations too early.

- **Key Point 5: Remote work and location still shape opportunity and pay.**
    - Remote, hybrid, and onsite roles carry different salary profiles (**EDA Chart 5, EDA Chart 26**), and when we isolate entry-level postings specifically, those differences persist — but the gaps and rankings may shift (**EDA Chart 27**). Similarly, entry-level salary varies meaningfully by industry (**EDA Chart 28**), which helps new entrants target sectors where junior compensation is strongest. The prevalence of each remote type has shifted meaningfully since 2020 (**EDA Chart 12**), and salary also varies by country (**EDA Chart 6**). For entry-level candidates, willingness to consider hybrid or onsite positions — or to target specific geographies and industries — can meaningfully expand the pool of realistic opportunities.

---
##### IV. Predictive Insights — What the Models Forecast

- **Key Point 6: Machine learning models confirm that experience level is the single strongest lever on salary, but skills and context matter too.**
    - A Random Forest regressor achieved an R² of 0.996 on salary prediction (**ML Model 1**), and an experience-level classifier reached 97.6% accuracy with an entry-level F1 score of 0.98 (**ML Model 2**). The PyTorch Integrated Gradients analysis (**ML Model 6**) goes further, quantifying how each feature's contribution to salary shifts across entry, mid, and senior subgroups. For new entrants, this reveals which levers — education, skill acquisition, remote flexibility — have the most marginal impact on compensation at the start of a career.

- **Key Point 7: The market trajectory suggests continued growth in posting volume, but entry-level candidates should prepare for sustained competition.**
    - A linear trend and year-over-year growth analysis (**ML Model 5**) quantifies the overall growth trajectory and, critically, compares total market growth against entry-level growth side by side — revealing whether junior opportunities are keeping pace. Hiring urgency trends (**EDA Chart 21**) suggest employers are filling roles with varying degrees of pressure. The autoencoder anomaly detection (**DNN Model 2**) also surfaces structurally unusual postings — outliers that may represent emerging niches or roles where competition is thinner. Watching for these atypical opportunities could be a strategic advantage.

---
##### V. Resolution — Actionable Takeaways for New Market Entrants

The data story resolves into a practical framework. The AI job market is genuinely growing, but entry-level candidates face a specific set of conditions: a narrower share of overall openings, a defined skill profile that favors Python and SQL fluency over premature specialization, seasonal hiring windows worth targeting, and geographic and remote-work dynamics that reward flexibility. The predictive models reinforce that experience level dominates early-career salary outcomes, but they also reveal that strategic choices around skills and role type can move the needle. The path in is real — but it rewards candidates who approach the market with the same analytical rigor they would bring to the work itself.