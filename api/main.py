import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scipy.sparse import hstack


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "api" / "model"


# ============================================================
# LOAD ORIGINAL MODEL + PREPROCESSING
# ============================================================

original_model = joblib.load(
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


# ============================================================
# LOAD CUSTOM SCREENING MODEL
# ============================================================

custom_model = joblib.load(
    MODEL_DIR / "custom_screening_model.pkl"
)

custom_metadata = joblib.load(
    MODEL_DIR / "custom_screening_metadata.pkl"
)

custom_selected_features = (
    custom_metadata["selected_features"]
)

custom_threshold = float(
    custom_metadata.get("threshold", 0.50)
)

custom_label_mapping = custom_metadata.get(
    "label_mapping",
    {
        "0": "LEGITIMATE",
        "1": "FRAUD",
    },
)


# ============================================================
# LOAD DATASET FOR TRANSACTIONID PREDICTION
# ============================================================

train_transaction = pd.read_csv(
    DATA_RAW / "train_transaction.csv"
)

train_identity = pd.read_csv(
    DATA_RAW / "train_identity.csv"
)

transaction_data = train_transaction.merge(
    train_identity,
    on="TransactionID",
    how="left",
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="FraudGuard API",
    description="Credit Card Fraud Detection API",
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class TransactionRequest(BaseModel):
    TransactionID: int


class CustomTransactionRequest(BaseModel):
    transaction_amount: float
    transaction_hour: int
    card_network: str
    card_type: str
    transaction_distance: float | None = None
    purchaser_email_domain: str | None = None
    device_type: str | None = None
    device_info: str | None = None
    identity_available: bool = False


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "FraudGuard API is running",
        "status": "healthy",
        "model": "XGBOOST CUSTOM SCREENING MODEL",
        "custom_features": len(custom_selected_features),
        "original_features": original_model.n_features_in_,
        "custom_threshold": custom_threshold,
        "label_mapping": custom_label_mapping,
    }


# ============================================================
# ORIGINAL MODEL FEATURE ENGINEERING
# ============================================================

def engineer_features(
    sample: pd.DataFrame,
) -> pd.DataFrame:

    sample = sample.copy()

    seconds_per_hour = 60 * 60
    seconds_per_day = 24 * seconds_per_hour

    sample["transaction_hour"] = (
        (sample["TransactionDT"] // seconds_per_hour)
        % 24
    )

    sample["transaction_day"] = (
        sample["TransactionDT"]
        // seconds_per_day
    )

    sample["transaction_week"] = (
        sample["transaction_day"] // 7
    )

    sample["hour_sin"] = np.sin(
        2 * np.pi * sample["transaction_hour"] / 24
    )

    sample["hour_cos"] = np.cos(
        2 * np.pi * sample["transaction_hour"] / 24
    )

    if "id_01" in sample.columns:
        sample["identity_present"] = (
            sample["id_01"]
            .notna()
            .astype(int)
        )
    else:
        sample["identity_present"] = 0

    missingness_features = [
        col
        for col in sample.columns
        if col not in [
            "TransactionID",
            "isFraud",
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
        "M6",
    ]

    for feature in selected_missing_features:

        if feature in sample.columns:
            sample[f"{feature}_missing"] = (
                sample[feature]
                .isna()
                .astype(int)
            )
        else:
            sample[f"{feature}_missing"] = 1

    return sample


# ============================================================
# ORIGINAL MODEL PREPROCESSING
# ============================================================

def preprocess_transaction(
    sample: pd.DataFrame,
):

    sample = engineer_features(sample)

    X_sample = sample.drop(
        columns=[
            "TransactionID",
            "isFraud",
        ],
        errors="ignore",
    )

    for feature in numerical_features:

        if feature not in X_sample.columns:
            X_sample[feature] = np.nan

    for feature in categorical_features:

        if feature not in X_sample.columns:
            X_sample[feature] = np.nan

    X_num = numerical_imputer.transform(
        X_sample[numerical_features]
    )

    X_cat = X_sample[
        categorical_features
    ].copy()

    for feature in categorical_features:

        X_cat[feature] = (
            X_cat[feature]
            .fillna("__MISSING__")
        )

        X_cat[feature] = (
            X_cat[feature]
            .where(
                X_cat[feature].isin(
                    categorical_maps[feature]
                ),
                "__RARE__",
            )
        )

    X_cat_encoded = (
        categorical_encoder.transform(
            X_cat
        )
    )

    return hstack([
        X_num,
        X_cat_encoded,
    ]).tocsr()


# ============================================================
# CUSTOM TRANSACTION FEATURE CONSTRUCTION
# ============================================================

def build_custom_transaction(
    request: CustomTransactionRequest,
) -> pd.DataFrame:

    hour = int(request.transaction_hour)

    if hour < 0 or hour > 23:
        raise HTTPException(
            status_code=400,
            detail=(
                "transaction_hour must "
                "be between 0 and 23."
            ),
        )

    amount = float(request.transaction_amount)

    if amount < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "transaction_amount "
                "cannot be negative."
            ),
        )

    distance = (
        None
        if request.transaction_distance is None
        else float(request.transaction_distance)
    )

    if distance is not None and distance < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "transaction_distance "
                "cannot be negative."
            ),
        )

    card_network = (
        request.card_network.strip().lower()
        if request.card_network
        else None
    )

    card_type = (
        request.card_type.strip().lower()
        if request.card_type
        else None
    )

    email_domain = (
        request.purchaser_email_domain.strip().lower()
        if request.purchaser_email_domain
        else None
    )

    device_type = (
        request.device_type.strip().lower()
        if request.device_type
        else None
    )

    device_info = (
        request.device_info.strip()
        if request.device_info
        else None
    )

    return pd.DataFrame([
        {
            "TransactionAmt": amount,

            "amount_log": np.log1p(amount),

            "transaction_hour": hour,

            "hour_sin": np.sin(
                2 * np.pi * hour / 24
            ),

            "hour_cos": np.cos(
                2 * np.pi * hour / 24
            ),

            "dist1": distance,

            "distance_log": (
                np.log1p(distance)
                if distance is not None
                else np.nan
            ),

            "identity_available": int(
                request.identity_available
            ),

            "distance_available": int(
                distance is not None
            ),

            "email_available": int(
                email_domain is not None
            ),

            "device_available": int(
                device_info is not None
            ),

            "card4": card_network,

            "card6": card_type,

            "P_emaildomain": email_domain,

            "DeviceType": device_type,

            "DeviceInfo": device_info,
        }
    ])


# ============================================================
# CUSTOM MODEL PREPROCESSING
# ============================================================

def preprocess_custom_transaction(
    sample: pd.DataFrame,
) -> pd.DataFrame:

    missing_columns = [
        feature
        for feature in custom_selected_features
        if feature not in sample.columns
    ]

    if missing_columns:

        raise HTTPException(
            status_code=500,
            detail=(
                "Custom feature construction failed. "
                "Missing features: "
                + ", ".join(missing_columns)
            ),
        )

    return sample[
        custom_selected_features
    ].copy()


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(
    fraud_probability: float,
) -> str:

    if fraud_probability >= 0.70:
        return "HIGH"

    if fraud_probability >= 0.30:
        return "MEDIUM"

    return "LOW"


# ============================================================
# ORIGINAL TRANSACTIONID PREDICTION
# ============================================================

@app.post("/predict")
def predict(
    transaction: TransactionRequest,
):

    transaction_id = transaction.TransactionID

    sample = transaction_data[
        transaction_data["TransactionID"]
        == transaction_id
    ]

    if sample.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"TransactionID "
                f"{transaction_id} not found"
            ),
        )

    X_final = preprocess_transaction(
        sample
    )

    expected_features = (
        original_model.n_features_in_
    )

    if X_final.shape[1] != expected_features:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature count mismatch. "
                f"Expected {expected_features}, "
                f"got {X_final.shape[1]}"
            ),
        )

    fraud_probability = float(
        original_model.predict_proba(
            X_final
        )[0, 1]
    )

    prediction = int(
        fraud_probability >= 0.50
    )

    return {
        "transaction_id": transaction_id,

        "fraud_probability": round(
            fraud_probability,
            6,
        ),

        "prediction": prediction,

        "risk_level": classify_risk(
            fraud_probability
        ),

        "model": "XGBOOST DAY 7 CHAMPION",

        "features": X_final.shape[1],

        "label_mapping": {
            "0": "LEGITIMATE",
            "1": "FRAUD",
        },
    }


# ============================================================
# CUSTOM TRANSACTION PREDICTION
# ============================================================

@app.post("/predict/custom")
def predict_custom(
    transaction: CustomTransactionRequest,
):

    sample = build_custom_transaction(
        transaction
    )

    X_custom = preprocess_custom_transaction(
        sample
    )

    expected_features = len(
        custom_selected_features
    )

    if X_custom.shape[1] != expected_features:

        raise HTTPException(
            status_code=500,
            detail=(
                "Custom feature count mismatch. "
                f"Expected {expected_features}, "
                f"got {X_custom.shape[1]}"
            ),
        )

    fraud_probability = float(
        custom_model.predict_proba(
            X_custom
        )[0, 1]
    )

    prediction = int(
        fraud_probability >= custom_threshold
    )

    return {
        "fraud_probability": round(
            fraud_probability,
            6,
        ),

        "prediction": prediction,

        "risk_level": classify_risk(
            fraud_probability
        ),

        "model": "XGBOOST CUSTOM SCREENING MODEL",

        "features": X_custom.shape[1],

        "classification_threshold": custom_threshold,

        "label_mapping": custom_label_mapping,
    }