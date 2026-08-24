import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from xgboost import XGBClassifier


# ============================================================
# FRAUDGUARD — CUSTOM TRANSACTION SCREENING MODEL
# USER-INPUT MODEL
# ============================================================

print("=" * 80)
print("FRAUDGUARD — CUSTOM TRANSACTION SCREENING MODEL")
print("USER-INPUT MODEL")
print("=" * 80)


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"

MODEL_DIR = PROJECT_ROOT / "api" / "model"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\n[1/10] Loading transaction data...")

transaction_path = (
    DATA_RAW / "train_transaction.csv"
)

identity_path = (
    DATA_RAW / "train_identity.csv"
)


transactions = pd.read_csv(
    transaction_path
)

identity = pd.read_csv(
    identity_path
)


print(
    f"Transaction data: {transactions.shape}"
)

print(
    f"Identity data:    {identity.shape}"
)


# ============================================================
# 3. MERGE IDENTITY DATA
# ============================================================

print(
    "\n[2/10] Merging identity information..."
)


data = transactions.merge(
    identity,
    on="TransactionID",
    how="left",
)


print(
    f"Merged dataset: {data.shape}"
)


# ============================================================
# 4. FEATURE ENGINEERING
# ============================================================

print(
    "\n[3/10] Building transaction features..."
)


# ------------------------------------------------------------
# Transaction hour
# ------------------------------------------------------------

data["transaction_hour"] = (
    (
        data["TransactionDT"]
        // (60 * 60)
    )
    % 24
)


# ------------------------------------------------------------
# Cyclical hour encoding
# ------------------------------------------------------------

data["hour_sin"] = np.sin(
    2
    * np.pi
    * data["transaction_hour"]
    / 24
)


data["hour_cos"] = np.cos(
    2
    * np.pi
    * data["transaction_hour"]
    / 24
)


# ------------------------------------------------------------
# Identity availability
# ------------------------------------------------------------

if "id_01" in data.columns:

    data["identity_available"] = (
        data["id_01"]
        .notna()
        .astype(int)
    )

else:

    data["identity_available"] = 0


# ------------------------------------------------------------
# Distance availability
# ------------------------------------------------------------

data["distance_available"] = (
    data["dist1"]
    .notna()
    .astype(int)
)


# ------------------------------------------------------------
# Email availability
# ------------------------------------------------------------

data["email_available"] = (
    data["P_emaildomain"]
    .notna()
    .astype(int)
)


# ------------------------------------------------------------
# Device availability
# ------------------------------------------------------------

data["device_available"] = (
    data["DeviceInfo"]
    .notna()
    .astype(int)
)


# ============================================================
# 5. USER-FACING FEATURES
# ============================================================

print(
    "\n[4/10] Selecting user-facing features..."
)


# ------------------------------------------------------------
# IMPORTANT
#
# TransactionAmt is intentionally kept as the ONLY amount
# representation.
#
# We previously used:
#
#     TransactionAmt
#     amount_log
#
# Having two correlated amount representations allowed the
# model to behave unexpectedly when testing different amounts.
#
# The custom API provides TransactionAmt directly, so we use
# that single source of truth.
# ------------------------------------------------------------


numeric_features = [

    "TransactionAmt",

    "transaction_hour",

    "hour_sin",

    "hour_cos",

    "dist1",

    "identity_available",

    "distance_available",

    "email_available",

    "device_available",

]


categorical_features = [

    "card4",

    "card6",

    "P_emaildomain",

    "DeviceType",

    "DeviceInfo",

]


selected_features = (
    numeric_features
    + categorical_features
)


print("\nNumeric features:")

for feature in numeric_features:

    print(
        f"  - {feature}"
    )


print("\nCategorical features:")

for feature in categorical_features:

    print(
        f"  - {feature}"
    )


print(
    f"\nTotal custom model features: "
    f"{len(selected_features)}"
)


# ============================================================
# 6. PREPARE DATA
# ============================================================

print(
    "\n[5/10] Preparing training data..."
)


X = data[
    selected_features
].copy()


y = data[
    "isFraud"
].astype(int)


print(
    f"Samples:     {len(X):,}"
)

print(
    f"Legitimate:  {(y == 0).sum():,}"
)

print(
    f"Fraudulent:  {(y == 1).sum():,}"
)

print(
    f"Fraud rate:  {y.mean() * 100:.3f}%"
)


# ============================================================
# 7. TRAIN / VALIDATION SPLIT
# ============================================================

print(
    "\n[6/10] Creating train/validation split..."
)


X_train, X_valid, y_train, y_valid = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
)


print(
    f"Training samples:   {len(X_train):,}"
)

print(
    f"Validation samples: {len(X_valid):,}"
)


# ============================================================
# 8. PREPROCESSING
# ============================================================

print(
    "\n[7/10] Building preprocessing pipeline..."
)


# ------------------------------------------------------------
# Numeric preprocessing
# ------------------------------------------------------------

numeric_pipeline = Pipeline(

    steps=[

        (
            "imputer",

            SimpleImputer(
                strategy="median"
            ),
        ),

    ]

)


# ------------------------------------------------------------
# Categorical preprocessing
# ------------------------------------------------------------

categorical_pipeline = Pipeline(

    steps=[

        (
            "imputer",

            SimpleImputer(
                strategy="most_frequent"
            ),
        ),

        (
            "encoder",

            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=True,
            ),
        ),

    ]

)


# ------------------------------------------------------------
# Column transformer
# ------------------------------------------------------------

preprocessor = ColumnTransformer(

    transformers=[

        (
            "numeric",

            numeric_pipeline,

            numeric_features,
        ),

        (
            "categorical",

            categorical_pipeline,

            categorical_features,
        ),

    ]

)


# ============================================================
# 9. XGBOOST MODEL
# ============================================================

print(
    "\nBuilding XGBoost model..."
)


# ------------------------------------------------------------
# AMOUNT MONOTONICITY
#
# TransactionAmt is the FIRST numeric feature.
#
# Constraint:
#
#     +1 = increasing
#      0 = unconstrained
#     -1 = decreasing
#
# Therefore:
#
#     TransactionAmt -> +1
#
# All other original features -> 0
#
# This tells XGBoost:
#
# "When every other feature remains identical, increasing
# transaction amount must NEVER decrease the fraud score."
# ------------------------------------------------------------


monotonic_constraints = (
    "(1,0,0,0,0,0,0,0,0)"
)


model = XGBClassifier(

    n_estimators=600,

    max_depth=5,

    learning_rate=0.04,

    min_child_weight=5,

    subsample=0.85,

    colsample_bytree=0.85,

    objective="binary:logistic",

    eval_metric="aucpr",

    random_state=42,

    n_jobs=-1,

    tree_method="hist",

    monotone_constraints=(
        monotonic_constraints
    ),

)


# ============================================================
# 10. FULL PIPELINE
# ============================================================

pipeline = Pipeline(

    steps=[

        (
            "preprocessor",

            preprocessor,
        ),

        (
            "model",

            model,
        ),

    ]

)


# ============================================================
# 11. TRAIN
# ============================================================

print(
    "\n[8/10] Training custom screening model..."
)

print(
    "-" * 80
)


pipeline.fit(
    X_train,
    y_train,
)


print(
    "-" * 80
)

print(
    "Training complete."
)


# ============================================================
# 12. VALIDATION PROBABILITIES
# ============================================================

print(
    "\n[9/10] Evaluating model..."
)

print(
    "=" * 80
)


probabilities = (
    pipeline.predict_proba(
        X_valid
    )[:, 1]
)


# ============================================================
# 13. ROC-AUC / PR-AUC
# ============================================================

roc_auc = roc_auc_score(
    y_valid,
    probabilities,
)


pr_auc = average_precision_score(
    y_valid,
    probabilities,
)


print(
    f"\nROC-AUC : {roc_auc:.4f}"
)

print(
    f"PR-AUC  : {pr_auc:.4f}"
)


# ============================================================
# 14. FIND BEST F1 THRESHOLD
# ============================================================

print(
    "\nSearching for classification threshold..."
)


thresholds = np.arange(
    0.05,
    0.91,
    0.01,
)


best_threshold = 0.50

best_f1 = 0.0


for threshold in thresholds:

    threshold_predictions = (
        probabilities >= threshold
    ).astype(int)

    current_f1 = f1_score(

        y_valid,

        threshold_predictions,

        zero_division=0,

    )


    if current_f1 > best_f1:

        best_f1 = current_f1

        best_threshold = float(
            threshold
        )


print(
    f"Best validation threshold: "
    f"{best_threshold:.2f}"
)

print(
    f"Best validation F1: "
    f"{best_f1:.4f}"
)


# ============================================================
# 15. FINAL CLASSIFICATION
# ============================================================

predictions = (
    probabilities >= best_threshold
).astype(int)


# ============================================================
# 16. CLASSIFICATION METRICS
# ============================================================

precision = precision_score(
    y_valid,
    predictions,
    zero_division=0,
)


recall = recall_score(
    y_valid,
    predictions,
    zero_division=0,
)


f1 = f1_score(
    y_valid,
    predictions,
    zero_division=0,
)


print(
    "\nFINAL CLASSIFICATION METRICS"
)

print(
    "-" * 80
)

print(
    f"Threshold: {best_threshold:.2f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall:    {recall:.4f}"
)

print(
    f"F1 Score:  {f1:.4f}"
)


# ============================================================
# 17. CONFUSION MATRIX
# ============================================================

matrix = confusion_matrix(
    y_valid,
    predictions,
)


print(
    "\nCONFUSION MATRIX"
)

print(
    "-" * 40
)

print(
    "                 Predicted"
)

print(
    "                 Legit   Fraud"
)

print(
    f"Actual Legit     "
    f"{matrix[0, 0]:7,} "
    f"{matrix[0, 1]:7,}"
)

print(
    f"Actual Fraud     "
    f"{matrix[1, 0]:7,} "
    f"{matrix[1, 1]:7,}"
)


# ============================================================
# 18. CLASSIFICATION REPORT
# ============================================================

print(
    "\nCLASSIFICATION REPORT"
)

print(
    "-" * 80
)

print(
    classification_report(

        y_valid,

        predictions,

        target_names=[
            "LEGITIMATE",
            "FRAUD",
        ],

        zero_division=0,

    )
)


# ============================================================
# 19. SAMPLE VALIDATION PREDICTIONS
# ============================================================

print(
    "\nSAMPLE VALIDATION PREDICTIONS"
)

print(
    "-" * 80
)


sample_results = X_valid.copy()


sample_results["actual"] = (
    y_valid.values
)


sample_results["fraud_probability"] = (
    probabilities
)


sample_results["prediction"] = (
    predictions
)


print(

    sample_results[

        [
            "TransactionAmt",

            "transaction_hour",

            "card4",

            "card6",

            "dist1",

            "actual",

            "fraud_probability",

            "prediction",

        ]

    ]

    .head(10)

    .to_string(
        index=False
    )

)


# ============================================================
# 20. AMOUNT MONOTONICITY TEST
# ============================================================

print(
    "\nAMOUNT MONOTONICITY TEST"
)

print(
    "-" * 80
)


# ------------------------------------------------------------
# Use a real validation transaction.
#
# Change ONLY TransactionAmt.
#
# Every other feature stays exactly the same.
# ------------------------------------------------------------

reference_transaction = (
    X_valid.iloc[[0]].copy()
)


amount_values = [

    10.0,

    100.0,

    500.0,

    1000.0,

    2500.0,

    5000.0,

    10000.0,

]


print(
    "\nSame transaction context, "
    "different amounts:"
)

print(
    "Amount          Fraud Probability"
)


previous_probability = None

monotonicity_passed = True


for amount in amount_values:

    test_transaction = (
        reference_transaction.copy()
    )


    test_transaction[
        "TransactionAmt"
    ] = amount


    probability = float(

        pipeline.predict_proba(

            test_transaction

        )[0, 1]

    )


    print(

        f"₹{amount:10.2f}"
        f"          "
        f"{probability * 100:7.2f}%"

    )


    if (

        previous_probability is not None

        and probability
        < previous_probability - 1e-9

    ):

        monotonicity_passed = False


        print(
            "WARNING: Probability decreased."
        )


    previous_probability = (
        probability
    )


print()


if monotonicity_passed:

    print(
        "Amount monotonicity check: PASSED"
    )

else:

    print(
        "Amount monotonicity check: FAILED"
    )


# ============================================================
# 21. SAVE MODEL
# ============================================================

print(
    "\n[10/10] Saving model..."
)


model_path = (
    MODEL_DIR
    / "custom_screening_model.pkl"
)


joblib.dump(
    pipeline,
    model_path,
)


# ============================================================
# 22. SAVE METADATA
# ============================================================

metadata = {

    "numeric_features":
        numeric_features,

    "categorical_features":
        categorical_features,

    "selected_features":
        selected_features,

    "threshold":
        float(best_threshold),

    "model_type":
        "XGBoost Custom Screening Model",

    "training_dataset":
        "IEEE-CIS Fraud Detection",

    "label_mapping": {

        "0":
            "LEGITIMATE",

        "1":
            "FRAUD",

    },

    "user_facing_features_only":
        True,

    "probability_calibration":
        "Unweighted XGBoost probability",

    "amount_monotonic":
        True,

    "amount_feature":
        "TransactionAmt",

    "amount_log_used":
        False,

    "monotonicity_test":
        monotonicity_passed,

}


metadata_path = (
    MODEL_DIR
    / "custom_screening_metadata.pkl"
)


joblib.dump(
    metadata,
    metadata_path,
)


# ============================================================
# 23. FINAL SUMMARY
# ============================================================

print(
    "\n" + "=" * 80
)

print(
    "CUSTOM SCREENING MODEL READY"
)

print(
    "=" * 80
)


print(
    f"Model saved to:"
    f"\n{model_path}"
)


print(
    f"\nMetadata saved to:"
    f"\n{metadata_path}"
)


print(
    f"\nFeatures used:"
    f" {len(selected_features)}"
)


print(
    "\nLabel mapping:"
)

print(
    "0 = LEGITIMATE"
)

print(
    "1 = FRAUD"
)


print(
    f"\nClassification threshold:"
    f" {best_threshold:.2f}"
)


print(
    f"\nROC-AUC : {roc_auc:.4f}"
)

print(
    f"PR-AUC  : {pr_auc:.4f}"
)

print(
    f"F1 Score: {f1:.4f}"
)


print(
    "\nAmount monotonicity:"
)

print(
    "ENABLED"
)


print(
    "\nMonotonicity test:"
)

print(
    "PASSED"
    if monotonicity_passed
    else "FAILED"
)


print(
    "=" * 80
)