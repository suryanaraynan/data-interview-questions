# Data Scientist (DS): interview prep

SQL, statistics, experiments, ML and product sense.

**4 of 76 questions answered** · **0 case files** · Tier 1 = asked most often, so start there.

← [All interview types](../README.md#prep-by-interview-type)

## Start here: most-asked (tier 1)

- [Find the highest-paid employee in each department. Then the top 3. What changes with ties?](../questions/001-top-earner-per-department/)
- [What is a p-value? Explain it to a non-technical person.](../questions/002-what-is-a-p-value/)
- [INNER JOIN vs LEFT JOIN: when do you use each, and what goes wrong with LEFT JOIN filters?](../questions/003-inner-vs-left-join/)
- [Explain the bias-variance trade-off. How do you diagnose overfitting?](../questions/004-bias-variance-trade-off/)
- Calculate a 7-day rolling average and a running total with window functions. *(answer coming)*
- How would you design an A/B test? Walk through hypothesis, metric, sample size and duration. *(answer coming)*
- Tell me about a time you made a mistake. *(answer coming)*
- Find and remove duplicate rows, keeping the first record. *(answer coming)*
- Data warehouse vs data lake vs lakehouse: what's the difference and when would you choose each? *(answer coming)*
- Your dataset is 99% one class. How do you handle the imbalance, and which metrics do you use? *(answer coming)*
- Calculate month-over-month growth in revenue or active users. *(answer coming)*
- Type I vs Type II errors: what are they, and which is worse for a given business problem? *(answer coming)*
- A key metric dropped 10% overnight. How do you investigate? *(answer coming)*
- Calculate 30-day user retention by signup cohort. *(answer coming)*
- Explain precision, recall, F1 and ROC-AUC. When is accuracy misleading? *(answer coming)*
- What is RAG, and why use it instead of fine-tuning or a bigger prompt? *(answer coming)*
- Mean vs median: which do you report for skewed data like salaries or house prices? *(answer coming)*
- Tell me about yourself (for a data role). *(answer coming)*
- How do you handle NULLs in SQL: in filters, aggregates, joins and comparisons? *(answer coming)*
- Explain the Central Limit Theorem and why it matters. *(answer coming)*
- What are the assumptions of linear regression, and what happens when they break? *(answer coming)*
- How do you calculate a ratio metric safely in SQL (e.g. conversion rate) and avoid division errors? *(answer coming)*
- Tell me about a time you disagreed with a stakeholder or colleague. *(answer coming)*
- How do you evaluate a RAG system? Retrieval vs generation metrics. *(answer coming)*
- What is a confidence interval? What does '95% confidence' actually mean? *(answer coming)*
- Explain how k-fold cross-validation works and why you'd use it. *(answer coming)*
- What is the project you're most proud of? *(answer coming)*

## All questions by topic

### SQL

- [Find the highest-paid employee in each department. Then the top 3. What changes with ties?](../questions/001-top-earner-per-department/) · tier 1
- [INNER JOIN vs LEFT JOIN: when do you use each, and what goes wrong with LEFT JOIN filters?](../questions/003-inner-vs-left-join/) · tier 1
- Calculate a 7-day rolling average and a running total with window functions. *(answer coming)* · tier 1
- Find and remove duplicate rows, keeping the first record. *(answer coming)* · tier 1
- Calculate month-over-month growth in revenue or active users. *(answer coming)* · tier 1
- Calculate 30-day user retention by signup cohort. *(answer coming)* · tier 1
- How do you handle NULLs in SQL: in filters, aggregates, joins and comparisons? *(answer coming)* · tier 1
- How do you calculate a ratio metric safely in SQL (e.g. conversion rate) and avoid division errors? *(answer coming)* · tier 1
- Find the second-highest (or Nth highest) value without using LIMIT/OFFSET. *(answer coming)* · tier 2
- CTEs vs subqueries vs temp tables: when do you use each? *(answer coming)* · tier 2
- GROUP BY with HAVING vs WHERE: what's the difference? *(answer coming)* · tier 2
- When do you use CASE WHEN? Show conditional aggregation. *(answer coming)* · tier 2
- Find customers with more than 3 transactions in each of two years. *(answer coming)* · tier 2
- Gaps and islands: find each user's longest streak of consecutive active days. *(answer coming)* · tier 2
- UNION vs UNION ALL. *(answer coming)* · tier 2
- Find records that have no match in another table (anti-join). *(answer coming)* · tier 2
- Self-joins: when would you use one? *(answer coming)* · tier 3

### Statistics

- [What is a p-value? Explain it to a non-technical person.](../questions/002-what-is-a-p-value/) · tier 1
- Type I vs Type II errors: what are they, and which is worse for a given business problem? *(answer coming)* · tier 1
- Mean vs median: which do you report for skewed data like salaries or house prices? *(answer coming)* · tier 1
- Explain the Central Limit Theorem and why it matters. *(answer coming)* · tier 1
- What is a confidence interval? What does '95% confidence' actually mean? *(answer coming)* · tier 1
- How do you detect and treat outliers? *(answer coming)* · tier 2
- Correlation vs causation: a correlation of 0.8, what can and can't you conclude? *(answer coming)* · tier 2
- What is selection bias? Give a real example. *(answer coming)* · tier 2
- MLE vs MAP. *(answer coming)* · tier 3
- Explain Bayes' theorem with a real example. *(answer coming)* · tier 3

### Experimentation & A/B testing

- How would you design an A/B test? Walk through hypothesis, metric, sample size and duration. *(answer coming)* · tier 1
- How do you choose the sample size for an experiment? *(answer coming)* · tier 2
- What can go wrong in an A/B test? (peeking, novelty effect, network effects, multiple testing) *(answer coming)* · tier 2
- When can't you run an A/B test, and what do you do instead? *(answer coming)* · tier 2
- What is the multiple testing problem? *(answer coming)* · tier 3

### Machine learning

- [Explain the bias-variance trade-off. How do you diagnose overfitting?](../questions/004-bias-variance-trade-off/) · tier 1
- Your dataset is 99% one class. How do you handle the imbalance, and which metrics do you use? *(answer coming)* · tier 1
- Explain precision, recall, F1 and ROC-AUC. When is accuracy misleading? *(answer coming)* · tier 1
- What are the assumptions of linear regression, and what happens when they break? *(answer coming)* · tier 1
- Explain how k-fold cross-validation works and why you'd use it. *(answer coming)* · tier 1
- Explain logistic regression and how to interpret its coefficients. *(answer coming)* · tier 2
- Random forest vs gradient boosting (XGBoost): how do they differ? *(answer coming)* · tier 2
- How does a decision tree decide where to split? *(answer coming)* · tier 2
- How do you handle missing data in a model? *(answer coming)* · tier 2
- How do you encode categorical variables? One-hot vs target encoding. *(answer coming)* · tier 2
- What is data leakage and how do you prevent it? *(answer coming)* · tier 2
- How do you explain a model's predictions to stakeholders? (feature importance, SHAP) *(answer coming)* · tier 2
- Regularisation: L1 vs L2. *(answer coming)* · tier 2
- Classification vs regression, with an example of each. *(answer coming)* · tier 2
- K-means: how it works and how you choose k. *(answer coming)* · tier 3
- PCA and dimensionality reduction, explained simply. *(answer coming)* · tier 3
- Gradient descent: batch vs mini-batch vs stochastic. *(answer coming)* · tier 3
- Which metric would you use for a regression model: MAE, RMSE or MAPE? *(answer coming)* · tier 3
- How would you forecast next year's revenue? *(answer coming)* · tier 3

### Python

- pandas: merge vs join vs concat. How do you avoid row explosion? *(answer coming)* · tier 2
- pandas: groupby with multiple aggregations, then filter groups. *(answer coming)* · tier 2
- Lists vs tuples; mutable vs immutable. *(answer coming)* · tier 2
- Remove duplicates and fill missing timestamps in a time series with pandas. *(answer coming)* · tier 2
- Generators and iterators in Python, and why they save memory. *(answer coming)* · tier 3

### Data engineering & pipelines

- Data warehouse vs data lake vs lakehouse: what's the difference and when would you choose each? *(answer coming)* · tier 1

### LLM / RAG

- What is RAG, and why use it instead of fine-tuning or a bigger prompt? *(answer coming)* · tier 1
- How do you evaluate a RAG system? Retrieval vs generation metrics. *(answer coming)* · tier 1
- What is chunking in RAG, and how do you choose chunk size? *(answer coming)* · tier 2
- What are embeddings? Semantic vs keyword (BM25) search, and hybrid search. *(answer coming)* · tier 2
- How do you reduce hallucinations in an LLM application? *(answer coming)* · tier 2
- Design a RAG system for customer support. *(answer coming)* · tier 2
- Prompting vs RAG vs fine-tuning: how do you decide? *(answer coming)* · tier 3
- What is the 'lost in the middle' problem? *(answer coming)* · tier 3

### Product sense & metrics

- A key metric dropped 10% overnight. How do you investigate? *(answer coming)* · tier 1
- How would you measure the success of a new feature? *(answer coming)* · tier 2
- Estimate customer lifetime value for a young company. *(answer coming)* · tier 3
- Would a 50% discount for riders be a good idea? How do you evaluate it? *(answer coming)* · tier 3

### Behavioural

- Tell me about a time you made a mistake. *(answer coming)* · tier 1
- Tell me about yourself (for a data role). *(answer coming)* · tier 1
- Tell me about a time you disagreed with a stakeholder or colleague. *(answer coming)* · tier 1
- What is the project you're most proud of? *(answer coming)* · tier 1
- Explain a technical concept to a non-technical audience. *(answer coming)* · tier 2
- Tell me about an analysis that drove a business decision. *(answer coming)* · tier 2
- Tell me about a time you cleaned and organised a messy dataset. *(answer coming)* · tier 3

## Case files for this track

Worked, real-world examples with a STAR interview script (`INTERVIEW.md`) in each folder.

*None yet.*
