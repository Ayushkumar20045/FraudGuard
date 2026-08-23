import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from scipy.sparse import hstack
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ==================================================
# 1. Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "api" / "model"


# ==================================================
# 2. Load model artifacts
# ==================================================

print("Loading FraudGuard model artifacts...")

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


# ==================================================
# 3. Load raw datasets
# ==================================================

print("Loading transaction data...")

train_transaction = pd.read_csv(
    DATA_RAW / "train_transaction.csv"
)

print(
    "Transaction data:",
    train_transaction.shape
)


print("Loading identity data...")

train_identity = pd.read_csv(
    DATA_RAW / "train_identity.csv"
)

print(
    "Identity data:",
    train_identity.shape
)


# ==================================================
# 4. Create lookup dataset
# ==================================================

transaction_data = train_transaction.merge(
    train_identity,
    on="TransactionID",
    how="left"
)

print(
    "Merged data:",
    transaction_data.shape
)


# ==================================================
# 5. FastAPI
# ==================================================

app = FastAPI(
    title="FraudGuard API",
    description="Credit Card Fraud Detection API",
    version="1.0.0"
)


# ==================================================
# 6. Request schema
# ==================================================

class TransactionRequest(BaseModel):

    TransactionID: int


# ==================================================
# 7. Root endpoint
# ==================================================

@app.get("/")
def root():

    return {
        "message": "FraudGuard API is running",
        "status": "healthy"
    }


# ==================================================
# 8. Feature engineering
# EXACT Day 3 logic
# ==================================================

def engineer_features(
    sample: pd.DataFrame
) -> pd.DataFrame:

    SECONDS_PER_HOUR = 60 * 60

    SECONDS_PER_DAY = (
        24 * SECONDS_PER_HOUR
    )

    sample["transaction_hour"] = (
        (
            sample["TransactionDT"]
            // SECONDS_PER_HOUR
        )
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
        2
        * np.pi
        * sample["transaction_hour"]
        / 24
    )

    sample["hour_cos"] = np.cos(
        2
        * np.pi
        * sample["transaction_hour"]
        / 24
    )

    sample["identity_present"] = (
        sample["id_01"]
        .notna()
        .astype(int)
    )

    # ----------------------------------------------
    # Missing feature count
    # ----------------------------------------------

    missingness_features = [
        col
        for col in sample.columns
        if col not in [
            "TransactionID",
            "isFraud"
        ]
    ]

    sample["missing_feature_count"] = (
        sample[
            missingness_features
        ]
        .isna()
        .sum(axis=1)
    )

    # ----------------------------------------------
    # Selected missingness features
    # ----------------------------------------------

    selected_missing_features = [
        "addr1",
        "addr2",
        "M1",
        "M2",
        "M3",
        "M6"
    ]

    for feature in selected_missing_features:

        sample[
            f"{feature}_missing"
        ] = (
            sample[feature]
            .isna()
            .astype(int)
        )

    return sample


# ==================================================
# 9. Preprocessing
# ==================================================

def preprocess_transaction(
    sample: pd.DataFrame
):

    # ----------------------------------------------
    # Feature engineering
    # ----------------------------------------------

    sample = engineer_features(
        sample.copy()
    )

    # ----------------------------------------------
    # Remove target + ID
    # ----------------------------------------------

    X_sample = sample.drop(
        columns=[
            "TransactionID",
            "isFraud"
        ],
        errors="ignore"
    )

    # ----------------------------------------------
    # Ensure numerical columns exist
    # ----------------------------------------------

    for feature in numerical_features:

        if feature not in X_sample.columns:

            X_sample[feature] = np.nan

    # ----------------------------------------------
    # Ensure categorical columns exist
    # ----------------------------------------------

    for feature in categorical_features:

        if feature not in X_sample.columns:

            X_sample[feature] = np.nan

    # ----------------------------------------------
    # Numerical preprocessing
    # ----------------------------------------------

    X_num = numerical_imputer.transform(
        X_sample[
            numerical_features
        ]
    )

    # ----------------------------------------------
    # Categorical preprocessing
    # ----------------------------------------------

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

    # ----------------------------------------------
    # One-hot encoding
    # ----------------------------------------------

    X_cat_encoded = (
        categorical_encoder.transform(
            X_cat
        )
    )

    # ----------------------------------------------
    # Final 891-feature matrix
    # ----------------------------------------------

    X_final = hstack([
        X_num,
        X_cat_encoded
    ]).tocsr()

    return X_final


# ==================================================
# 10. Prediction endpoint
# ==================================================

@app.post("/predict")
def predict(
    transaction: TransactionRequest
):

    transaction_id = (
        transaction.TransactionID
    )

    # ----------------------------------------------
    # Find transaction
    # ----------------------------------------------

    sample = transaction_data[
        transaction_data[
            "TransactionID"
        ]
        == transaction_id
    ]

    # ----------------------------------------------
    # Transaction not found
    # ----------------------------------------------

    if sample.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"TransactionID "
                f"{transaction_id} "
                f"not found"
            )
        )

    # ----------------------------------------------
    # Preprocess
    # ----------------------------------------------

    X_final = preprocess_transaction(
        sample
    )

    # ----------------------------------------------
    # Validate feature count
    # ----------------------------------------------

    if X_final.shape[1] != 891:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature count mismatch. "
                f"Expected 891, "
                f"got {X_final.shape[1]}"
            )
        )

    # ----------------------------------------------
    # Prediction
    # ----------------------------------------------

    fraud_probability = float(
        model.predict_proba(
            X_final
        )[0, 1]
    )

    prediction = int(
        fraud_probability >= 0.5
    )

    # ----------------------------------------------
    # Risk level
    # ----------------------------------------------

    if fraud_probability >= 0.70:

        risk_level = "HIGH"

    elif fraud_probability >= 0.30:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    # ----------------------------------------------
    # Response
    # ----------------------------------------------

    return {
        "transaction_id": transaction_id,
        "fraud_probability": round(
            fraud_probability,
            6
        ),
        "prediction": prediction,
        "risk_level": risk_level
    }