import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.sparse import hstack


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "api" / "model"


# --------------------------------------------------
# 2. Load model artifacts
# --------------------------------------------------

print("Loading model artifacts...")

model = joblib.load(
    MODEL_DIR / "xgb_day7_champion.pkl"
)

numerical_imputer = joblib.load(
    MODEL_DIR / "numerical_imputer.pkl"
)

categorical_maps = joblib.load(
    MODEL_DIR / "categorical_maps.pkl"
)

categorical_encoder = joblib.load(
    MODEL_DIR / "categorical_encoder.pkl"
)

numerical_features = joblib.load(
    MODEL_DIR / "numerical_features.pkl"
)

categorical_features = joblib.load(
    MODEL_DIR / "categorical_features.pkl"
)

print("Artifacts loaded successfully.")


# --------------------------------------------------
# 3. Load one known FRAUD transaction
# --------------------------------------------------

print("Loading raw fraud transaction...")

transaction_data = pd.read_csv(
    DATA_RAW / "train_transaction.csv"
)

transaction = transaction_data[
    transaction_data["isFraud"] == 1
].iloc[[0]].copy()

identity = pd.read_csv(
    DATA_RAW / "train_identity.csv"
)

transaction_id = transaction["TransactionID"].iloc[0]

identity_row = identity[
    identity["TransactionID"] == transaction_id
]

sample = transaction.merge(
    identity_row,
    on="TransactionID",
    how="left"
)

print(
    "Sample TransactionID:",
    transaction_id
)

print(
    "Actual label:",
    int(transaction["isFraud"].iloc[0])
)

print(
    "Merged sample shape:",
    sample.shape
)


# --------------------------------------------------
# 4. Feature engineering
# EXACT Day 3 logic
# --------------------------------------------------

SECONDS_PER_HOUR = 60 * 60

SECONDS_PER_DAY = (
    24 * SECONDS_PER_HOUR
)


sample["transaction_hour"] = (
    (sample["TransactionDT"] // SECONDS_PER_HOUR)
    % 24
)


sample["transaction_day"] = (
    sample["TransactionDT"]
    // SECONDS_PER_DAY
)


sample["transaction_week"] = (
    sample["transaction_day"]
    // 7
)


sample["hour_sin"] = np.sin(
    2 * np.pi
    * sample["transaction_hour"]
    / 24
)


sample["hour_cos"] = np.cos(
    2 * np.pi
    * sample["transaction_hour"]
    / 24
)


sample["identity_present"] = (
    sample["id_01"]
    .notna()
    .astype(int)
)


# --------------------------------------------------
# 5. Missingness features
# EXACT Day 3 logic
# --------------------------------------------------

missingness_features = [
    col
    for col in sample.columns
    if col not in [
        "TransactionID",
        "isFraud"
    ]
]


sample["missing_feature_count"] = (
    sample[missingness_features]
    .isna()
    .sum(axis=1)
)


selected_missing_features = [
    "addr1",
    "addr2",
    "M1",
    "M2",
    "M3",
    "M6"
]


for feature in selected_missing_features:

    sample[f"{feature}_missing"] = (
        sample[feature]
        .isna()
        .astype(int)
    )


# --------------------------------------------------
# 6. Remove ID and target
# --------------------------------------------------

X_sample = sample.drop(
    columns=[
        "TransactionID",
        "isFraud"
    ],
    errors="ignore"
)


print(
    "Feature matrix before preprocessing:",
    X_sample.shape
)


# --------------------------------------------------
# 7. Numerical preprocessing
# --------------------------------------------------

X_num = numerical_imputer.transform(
    X_sample[numerical_features]
)


print(
    "Numerical matrix:",
    X_num.shape
)


# --------------------------------------------------
# 8. Categorical preprocessing
# --------------------------------------------------

X_cat = X_sample[
    categorical_features
].copy()


for feature in categorical_features:

    X_cat[feature] = (
        X_cat[feature]
        .fillna("__MISSING__")
    )

    frequent_categories = (
        categorical_maps[feature]
    )

    X_cat[feature] = (
        X_cat[feature]
        .where(
            X_cat[feature].isin(
                frequent_categories
            ),
            "__RARE__"
        )
    )


# --------------------------------------------------
# 9. One-hot encoding
# --------------------------------------------------

X_cat_encoded = (
    categorical_encoder.transform(
        X_cat
    )
)


print(
    "Categorical encoded matrix:",
    X_cat_encoded.shape
)


# --------------------------------------------------
# 10. Combine numerical + categorical
# --------------------------------------------------

X_final = hstack([
    X_num,
    X_cat_encoded
]).tocsr()


print(
    "Final inference shape:",
    X_final.shape
)


# --------------------------------------------------
# 11. Validate feature count
# --------------------------------------------------

expected_features = (
    len(numerical_features)
    + X_cat_encoded.shape[1]
)


if X_final.shape[1] != expected_features:

    raise ValueError(
        f"Feature count mismatch: "
        f"expected {expected_features}, "
        f"got {X_final.shape[1]}"
    )


if X_final.shape[1] != 891:

    raise ValueError(
        f"Model expects 891 features, "
        f"but inference produced "
        f"{X_final.shape[1]}"
    )


# --------------------------------------------------
# 12. Prediction
# --------------------------------------------------

fraud_probability = (
    model.predict_proba(X_final)[0, 1]
)


prediction = int(
    fraud_probability >= 0.5
)


# --------------------------------------------------
# 13. Risk level
# --------------------------------------------------

if fraud_probability >= 0.70:

    risk_level = "HIGH"

elif fraud_probability >= 0.30:

    risk_level = "MEDIUM"

else:

    risk_level = "LOW"


# --------------------------------------------------
# 14. Result
# --------------------------------------------------

print("\n" + "=" * 50)

print("INFERENCE TEST")

print("=" * 50)

print(
    "TransactionID:",
    transaction_id
)

print(
    "Actual label:",
    int(transaction["isFraud"].iloc[0])
)

print(
    "Features:",
    X_final.shape[1]
)

print(
    "Fraud probability:",
    round(
        float(fraud_probability),
        6
    )
)

print(
    "Prediction:",
    "FRAUD"
    if prediction == 1
    else "LEGITIMATE"
)

print(
    "Risk level:",
    risk_level
)

print("=" * 50)