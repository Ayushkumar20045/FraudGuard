# FraudGuard — Project Log

## Day 1 — Dataset Audit
- Loaded and verified the IEEE-CIS Fraud Detection dataset.
- Analyzed dataset dimensions, target distribution, data types, and categorical features.
- Investigated transaction and identity feature missingness.
- Identified severe class imbalance (~3.5% fraud).
- Explored identity data availability and initial missingness patterns.
- Completed initial dataset audit.

## Day 2 — Exploratory Data Analysis
- Analyzed transaction amount, transaction time, card features, ProductCD, email domains, and M1–M9.
- Studied missingness and found that missing values/feature availability can carry fraud-related information.
- Analyzed identity availability and found identity-present transactions have a significantly higher fraud rate.
- Explored numerical identity features and identified promising candidates.
- Explored categorical identity features and identified important fraud-rate differences.
- Completed EDA and prepared findings for feature engineering.