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

## Day 3 — Feature Engineering & Baseline Modeling
- Built the master dataset and engineered time, identity-availability, and missingness features.
- Created a leakage-safe chronological split with 484,847 training and 105,693 validation transactions.
- Built numerical median imputation and categorical rare-category grouping with one-hot encoding.
- Produced a final sparse feature matrix with 891 features.
- Trained a Logistic Regression baseline achieving ROC-AUC 0.8054 and PR-AUC 0.1622.
- At threshold 0.80, the model caught 1,309 frauds with 23.39% precision and 36.25% recall.

## Day 4 — Model Improvement

- Recreated and saved the leakage-safe 891-feature training/validation matrices.
- Trained XGBoost as the first nonlinear challenger to the Logistic Regression baseline.
- XGBoost improved ROC-AUC from 0.8054 to 0.9049 and PR-AUC from 0.1622 to 0.5391.
- Threshold 0.30 gave the best tested F1 of 0.5200 with 62.82% precision and 44.36% recall.
- XGBoost caught 1,602 frauds with 948 false positives on validation data.
- Feature analysis revealed strong nonlinear signals, especially V258, and PR-AUC remained stable across time periods.

## Day 5 — Model Explainability & Error Analysis

- Analyzed XGBoost validation errors: 1,602 true positives, 948 false positives, 2,009 false negatives, and 101,134 true negatives.
- Found that 899 of 2,009 missed frauds received probability below 0.05, showing that most false negatives are difficult cases rather than simple threshold misses.
- Threshold analysis confirmed 0.30 as the best tested F1 point (0.5200), while lower thresholds provide higher recall at the cost of precision.
- Investigated borderline false negatives and found that only 108 missed frauds had probabilities between 0.25–0.30.
- V258 strongly separates detected fraud from borderline misses: true-positive probability increased from 0.70 to 0.86 across V258 ranges, while borderline fraud remained around 0.27.
- Concluded that future improvement should focus on feature interactions and hard-to-detect fraud patterns rather than threshold tuning alone.

## Day 6 — Hard-Fraud Feature Engineering

- Tested five targeted features based on Day 5 findings: V258 risk bands, V258 missingness, V294 risk band, and V294 missingness.
- Rebuilt the preprocessing pipeline with 896 features while preserving the original 891-feature representation.
- Trained an XGBoost challenger using the same hyperparameters as the Day 4 champion.
- Day 6 performance decreased from ROC-AUC 0.9049 to 0.9038 and PR-AUC 0.5391 to 0.5331.
- At threshold 0.30, the model caught 1,568 frauds versus 1,602 for the Day 4 model and produced 2,043 false negatives.
- Rejected the engineered features because they added redundant information already captured by XGBoost.
- Day 4 XGBoost remains the FraudGuard champion.

## Day 7 — XGBoost Hyperparameter Optimization

- Performed systematic XGBoost tuning across estimators, learning rate, depth, min child weight, subsampling, and column sampling.
- Improved PR-AUC from 0.5391 to **0.6031** and ROC-AUC to **0.9219**.
- Selected Experiment 11 as the champion: 1,500 estimators, max_depth=8, learning_rate=0.07, subsample=0.8, colsample_bytree=0.9.
- Tested additional regularization settings (`gamma=0.05` and `0.1`), but both performed worse and were rejected.
- Selected threshold **0.20**, achieving 71.87% precision, 49.24% recall, and 0.5844 F1-score.
- Saved the final XGBoost model and validation predictions as the Day 7 champion.