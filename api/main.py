import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from scipy.sparse import hstack
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "api" / "model"


# ============================================================
# 2. LOAD MODEL ARTIFACTS
# ============================================================

print("=" * 70)
print("FRAUDGUARD — LOADING MODEL")
print("=" * 70)

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

print(
    f"Numerical features:   {len(numerical_features)}"
)

print(
    f"Categorical features: {len(categorical_features)}"
)

print(
    f"Total raw features:   "
    f"{len(numerical_features) + len(categorical_features)}"
)

print("=" * 70)


# ============================================================
# 3. LOAD DATASET
# ============================================================

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


# ============================================================
# 4. CREATE TRANSACTION LOOKUP DATASET
# ============================================================

transaction_data = train_transaction.merge(
    train_identity,
    on="TransactionID",
    how="left"
)

print(
    "Merged data:",
    transaction_data.shape
)

print("=" * 70)
print("FRAUDGUARD MODEL READY")
print("=" * 70)


# ============================================================
# 5. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FraudGuard API",
    description="Credit Card Fraud Detection API",
    version="1.0.0"
)


# ============================================================
# 6. CORS
# ============================================================

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
# 7. REQUEST MODELS
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
# 8. ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "FraudGuard API is running",
        "status": "healthy",
        "model": "XGBOOST DAY 7 CHAMPION",
        "features": 891
    }


# ============================================================
# 9. FEATURE ENGINEERING
# EXACT DAY 3 LOGIC
# ============================================================

def engineer_features(
    sample: pd.DataFrame
) -> pd.DataFrame:

    sample = sample.copy()

    SECONDS_PER_HOUR = 60 * 60

    SECONDS_PER_DAY = (
        24 * SECONDS_PER_HOUR
    )

    # --------------------------------------------------------
    # Transaction time
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Cyclical time encoding
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Identity availability
    # --------------------------------------------------------

    if "id_01" in sample.columns:

        sample["identity_present"] = (
            sample["id_01"]
            .notna()
            .astype(int)
        )

    else:

        sample["identity_present"] = 0

    # --------------------------------------------------------
    # Missing feature count
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Selected missingness features
    # --------------------------------------------------------

    selected_missing_features = [
        "addr1",
        "addr2",
        "M1",
        "M2",
        "M3",
        "M6"
    ]

    for feature in selected_missing_features:

        if feature in sample.columns:

            sample[
                f"{feature}_missing"
            ] = (
                sample[feature]
                .isna()
                .astype(int)
            )

        else:

            sample[
                f"{feature}_missing"
            ] = 1

    return sample


# ============================================================
# 10. PREPROCESSING
# ============================================================

def preprocess_transaction(
    sample: pd.DataFrame
):

    # --------------------------------------------------------
    # Feature engineering
    # --------------------------------------------------------

    sample = engineer_features(
        sample.copy()
    )

    # --------------------------------------------------------
    # Remove target and transaction ID
    # --------------------------------------------------------

    X_sample = sample.drop(
        columns=[
            "TransactionID",
            "isFraud"
        ],
        errors="ignore"
    )

    # --------------------------------------------------------
    # Ensure every numerical feature exists
    # --------------------------------------------------------

    for feature in numerical_features:

        if feature not in X_sample.columns:

            X_sample[feature] = np.nan

    # --------------------------------------------------------
    # Ensure every categorical feature exists
    # --------------------------------------------------------

    for feature in categorical_features:

        if feature not in X_sample.columns:

            X_sample[feature] = np.nan

    # --------------------------------------------------------
    # Numerical preprocessing
    # --------------------------------------------------------

    X_num = numerical_imputer.transform(
        X_sample[
            numerical_features
        ]
    )

    # --------------------------------------------------------
    # Categorical preprocessing
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # One-hot encoding
    # --------------------------------------------------------

    X_cat_encoded = (
        categorical_encoder.transform(
            X_cat
        )
    )

    # --------------------------------------------------------
    # Final feature matrix
    # --------------------------------------------------------

    X_final = hstack([
        X_num,
        X_cat_encoded
    ]).tocsr()

    return X_final


# ============================================================
# 11. BUILD CUSTOM TRANSACTION
# USER INPUT → IEEE-CIS REPRESENTATION
# ============================================================

def build_custom_transaction(
    request: CustomTransactionRequest
) -> pd.DataFrame:

    sample = pd.DataFrame([{

        # ----------------------------------------------------
        # User-facing transaction amount
        # ----------------------------------------------------

        "TransactionAmt":
            request.transaction_amount,

        # ----------------------------------------------------
        # Convert hour into TransactionDT-like representation
        # ----------------------------------------------------

        "TransactionDT":
            request.transaction_hour
            * 60
            * 60,

        # ----------------------------------------------------
        # Backend-controlled ProductCD
        #
        # Hidden from the user for now.
        # ----------------------------------------------------

        "ProductCD":
            "W",

        # ----------------------------------------------------
        # Card information
        # ----------------------------------------------------

        "card4":
            request.card_network,

        "card6":
            request.card_type,

        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        "dist1":
            request.transaction_distance,

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        "P_emaildomain":
            request.purchaser_email_domain,

        # ----------------------------------------------------
        # Device
        # ----------------------------------------------------

        "DeviceType":
            request.device_type,

        "DeviceInfo":
            request.device_info,

        # ----------------------------------------------------
        # Identity availability
        #
        # id_01 is used by the existing feature engineering
        # logic to determine identity availability.
        # ----------------------------------------------------

        "id_01":
            1
            if request.identity_available
            else np.nan,

    }])

    return sample


# ============================================================
# 12. RISK CLASSIFICATION
# ============================================================

def classify_risk(
    fraud_probability: float
) -> str:

    if fraud_probability >= 0.70:

        return "HIGH"

    if fraud_probability >= 0.30:

        return "MEDIUM"

    return "LOW"


# ============================================================
# 13. ORIGINAL TRANSACTIONID PREDICTION
# ============================================================

@app.post("/predict")
def predict(
    transaction: TransactionRequest
):

    transaction_id = (
        transaction.TransactionID
    )

    # --------------------------------------------------------
    # Find transaction
    # --------------------------------------------------------

    sample = transaction_data[
        transaction_data[
            "TransactionID"
        ]
        == transaction_id
    ]

    # --------------------------------------------------------
    # Transaction not found
    # --------------------------------------------------------

    if sample.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"TransactionID "
                f"{transaction_id} "
                f"not found"
            )
        )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    X_final = preprocess_transaction(
        sample
    )

    # --------------------------------------------------------
    # Validate feature count
    # --------------------------------------------------------

    if X_final.shape[1] != 891:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature count mismatch. "
                f"Expected 891, "
                f"got {X_final.shape[1]}"
            )
        )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    fraud_probability = float(
        model.predict_proba(
            X_final
        )[0, 1]
    )

    prediction = int(
        fraud_probability >= 0.5
    )

    risk_level = classify_risk(
        fraud_probability
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "transaction_id":
            transaction_id,

        "fraud_probability":
            round(
                fraud_probability,
                6
            ),

        "prediction":
            prediction,

        "risk_level":
            risk_level,

        "model":
            "XGBOOST DAY 7 CHAMPION",

        "features":
            X_final.shape[1]
    }


# ============================================================
# 14. CUSTOM TRANSACTION PREDICTION
# USER-FACING INFERENCE ENDPOINT
# ============================================================

@app.post("/predict/custom")
def predict_custom(
    transaction: CustomTransactionRequest
):

    # --------------------------------------------------------
    # Convert simplified user input into the model's
    # expected IEEE-CIS-style representation.
    # --------------------------------------------------------

    sample = build_custom_transaction(
        transaction
    )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    X_final = preprocess_transaction(
        sample
    )

    # --------------------------------------------------------
    # Validate feature count
    # --------------------------------------------------------

    if X_final.shape[1] != 891:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature count mismatch. "
                f"Expected 891, "
                f"got {X_final.shape[1]}"
            )
        )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    fraud_probability = float(
        model.predict_proba(
            X_final
        )[0, 1]
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    prediction = int(
        fraud_probability >= 0.5
    )

    risk_level = classify_risk(
        fraud_probability
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "fraud_probability":
            round(
                fraud_probability,
                6
            ),

        "prediction":
            prediction,

        "risk_level":
            risk_level,

        "model":
            "XGBOOST DAY 7 CHAMPION",

        "features":
            X_final.shape[1]
    }