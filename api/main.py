import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# FRAUDGUARD API
# ============================================================
# Supports:
#
# 1. Original IEEE-CIS TransactionID prediction
# 2. Custom user-input transaction screening
#
# CUSTOM MODEL FEATURES MUST MATCH:
#
# TransactionAmt
# amount_log
# transaction_hour
# hour_sin
# hour_cos
# dist1
# distance_log
# identity_available
# distance_available
# email_available
# device_available
# card4
# card6
# P_emaildomain
# DeviceType
# DeviceInfo
#
# LABEL MAPPING:
# 0 = LEGITIMATE
# 1 = FRAUD
# ============================================================


# ============================================================
# 1. PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "api" / "model"


# ============================================================
# 2. LOAD MODELS
# ============================================================

print("=" * 70)
print("FRAUDGUARD — LOADING MODELS")
print("=" * 70)


# ============================================================
# ORIGINAL IEEE-CIS MODEL
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
# CUSTOM SCREENING MODEL
# ============================================================

custom_model_path = (
    MODEL_DIR / "custom_screening_model.pkl"
)

custom_metadata_path = (
    MODEL_DIR / "custom_screening_metadata.pkl"
)


custom_model = joblib.load(
    custom_model_path
)

custom_metadata = joblib.load(
    custom_metadata_path
)


# ============================================================
# CUSTOM MODEL METADATA
# ============================================================

custom_numeric_features = (
    custom_metadata["numeric_features"]
)

custom_categorical_features = (
    custom_metadata["categorical_features"]
)

custom_selected_features = (
    custom_metadata["selected_features"]
)

custom_threshold = float(
    custom_metadata.get(
        "threshold",
        0.50,
    )
)

custom_label_mapping = (
    custom_metadata.get(
        "label_mapping",
        {
            "0": "LEGITIMATE",
            "1": "FRAUD",
        },
    )
)


print(
    f"Original model features: "
    f"{len(numerical_features) + len(categorical_features)}"
)

print(
    f"Custom model features: "
    f"{len(custom_selected_features)}"
)

print("Custom feature list:")

for feature in custom_selected_features:
    print(f"  - {feature}")

print(
    f"Custom threshold: "
    f"{custom_threshold}"
)

print(
    "Label mapping:"
)

print(
    f"  0 = {custom_label_mapping.get('0', 'LEGITIMATE')}"
)

print(
    f"  1 = {custom_label_mapping.get('1', 'FRAUD')}"
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
    train_transaction.shape,
)


print("Loading identity data...")

train_identity = pd.read_csv(
    DATA_RAW / "train_identity.csv"
)

print(
    "Identity data:",
    train_identity.shape,
)


# ============================================================
# 4. CREATE TRANSACTION LOOKUP DATASET
# ============================================================

transaction_data = train_transaction.merge(
    train_identity,
    on="TransactionID",
    how="left",
)


print(
    "Merged data:",
    transaction_data.shape,
)

print("=" * 70)
print("FRAUDGUARD MODELS READY")
print("=" * 70)


# ============================================================
# 5. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FraudGuard API",
    description="Credit Card Fraud Detection API",
    version="2.0.0",
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

        "model": (
            "XGBOOST CUSTOM SCREENING MODEL"
        ),

        "custom_features": len(
            custom_selected_features
        ),

        "original_features": (
            len(numerical_features)
            + len(categorical_features)
        ),

        "custom_threshold": (
            custom_threshold
        ),

        "label_mapping": (
            custom_label_mapping
        ),
    }


# ============================================================
# 9. ORIGINAL MODEL FEATURE ENGINEERING
# ============================================================

def engineer_features(
    sample: pd.DataFrame,
) -> pd.DataFrame:

    sample = sample.copy()

    seconds_per_hour = 60 * 60

    seconds_per_day = (
        24 * seconds_per_hour
    )


    # --------------------------------------------------------
    # Transaction time
    # --------------------------------------------------------

    sample["transaction_hour"] = (
        (
            sample["TransactionDT"]
            // seconds_per_hour
        )
        % 24
    )


    sample["transaction_day"] = (
        sample["TransactionDT"]
        // seconds_per_day
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
            "isFraud",
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
        "M6",
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
# 10. ORIGINAL MODEL PREPROCESSING
# ============================================================

def preprocess_transaction(
    sample: pd.DataFrame,
):

    sample = engineer_features(
        sample.copy()
    )


    X_sample = sample.drop(
        columns=[
            "TransactionID",
            "isFraud",
        ],
        errors="ignore",
    )


    # --------------------------------------------------------
    # Ensure numerical features exist
    # --------------------------------------------------------

    for feature in numerical_features:

        if feature not in X_sample.columns:

            X_sample[feature] = np.nan


    # --------------------------------------------------------
    # Ensure categorical features exist
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
                "__RARE__",
            )
        )


    X_cat_encoded = (
        categorical_encoder.transform(
            X_cat
        )
    )


    from scipy.sparse import hstack


    X_final = hstack([
        X_num,
        X_cat_encoded,
    ]).tocsr()


    return X_final


# ============================================================
# 11. BUILD CUSTOM TRANSACTION
# ============================================================

def build_custom_transaction(
    request: CustomTransactionRequest,
) -> pd.DataFrame:

    # --------------------------------------------------------
    # Validate transaction hour
    # --------------------------------------------------------

    hour = int(
        request.transaction_hour
    )


    if hour < 0 or hour > 23:

        raise HTTPException(
            status_code=400,
            detail=(
                "transaction_hour must "
                "be between 0 and 23."
            ),
        )


    # --------------------------------------------------------
    # Validate amount
    # --------------------------------------------------------

    amount = float(
        request.transaction_amount
    )


    if amount < 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "transaction_amount "
                "cannot be negative."
            ),
        )


    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    distance = (
        None
        if request.transaction_distance
        is None
        else float(
            request.transaction_distance
        )
    )


    if distance is not None and distance < 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "transaction_distance "
                "cannot be negative."
            ),
        )


    # --------------------------------------------------------
    # Normalize strings
    # --------------------------------------------------------

    card_network = (
        request.card_network
        .strip()
        .lower()
        if request.card_network
        else None
    )


    card_type = (
        request.card_type
        .strip()
        .lower()
        if request.card_type
        else None
    )


    email_domain = (
        request.purchaser_email_domain
        .strip()
        .lower()
        if request.purchaser_email_domain
        else None
    )


    device_type = (
        request.device_type
        .strip()
        .lower()
        if request.device_type
        else None
    )


    device_info = (
        request.device_info
        .strip()
        if request.device_info
        else None
    )


    # --------------------------------------------------------
    # Build EXACTLY the same 16 features used during
    # training.
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Do NOT add transaction_day.
    # Do NOT add transaction_week.
    #
    # The current model does not use them.
    # --------------------------------------------------------

    sample = pd.DataFrame([
        {

            # -------------------------------
            # Numeric features
            # -------------------------------

            "TransactionAmt":
                amount,

            "amount_log":
                np.log1p(amount),

            "transaction_hour":
                hour,

            "hour_sin":
                np.sin(
                    2
                    * np.pi
                    * hour
                    / 24
                ),

            "hour_cos":
                np.cos(
                    2
                    * np.pi
                    * hour
                    / 24
                ),

            "dist1":
                distance,

            "distance_log":
                (
                    np.log1p(distance)
                    if distance is not None
                    else np.nan
                ),

            "identity_available":
                int(
                    request.identity_available
                ),

            "distance_available":
                int(
                    distance is not None
                ),

            "email_available":
                int(
                    email_domain is not None
                ),

            "device_available":
                int(
                    device_info is not None
                ),


            # -------------------------------
            # Categorical features
            # -------------------------------

            "card4":
                card_network,

            "card6":
                card_type,

            "P_emaildomain":
                email_domain,

            "DeviceType":
                device_type,

            "DeviceInfo":
                device_info,
        }
    ])


    return sample


# ============================================================
# 12. CUSTOM MODEL PREPROCESSING
# ============================================================

def preprocess_custom_transaction(
    sample: pd.DataFrame,
) -> pd.DataFrame:

    # --------------------------------------------------------
    # Validate exact feature set
    # --------------------------------------------------------

    missing_columns = [
        feature
        for feature in custom_selected_features
        if feature not in sample.columns
    ]


    if missing_columns:

        raise HTTPException(
            status_code=500,
            detail=(
                "Custom feature construction "
                "failed. Missing features: "
                + ", ".join(
                    missing_columns
                )
            ),
        )


    # --------------------------------------------------------
    # Check for unexpected feature mismatch
    # --------------------------------------------------------

    X = sample[
        custom_selected_features
    ].copy()


    return X


# ============================================================
# 13. RISK CLASSIFICATION
# ============================================================

def classify_risk(
    fraud_probability: float,
) -> str:

    # --------------------------------------------------------
    # Risk levels are intentionally separate from the model
    # classification threshold.
    #
    # Model classification:
    #     probability >= 0.14 -> FRAUD
    #
    # Risk display:
    #     >= 0.70 -> HIGH
    #     >= 0.30 -> MEDIUM
    #     <  0.30 -> LOW
    #
    # This allows the UI to distinguish model probability
    # from broader risk presentation.
    # --------------------------------------------------------

    if fraud_probability >= 0.70:

        return "HIGH"


    if fraud_probability >= 0.30:

        return "MEDIUM"


    return "LOW"


# ============================================================
# 14. ORIGINAL TRANSACTIONID PREDICTION
# ============================================================

@app.post("/predict")
def predict(
    transaction: TransactionRequest,
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


    if sample.empty:

        raise HTTPException(
            status_code=404,
            detail=(
                f"TransactionID "
                f"{transaction_id} "
                f"not found"
            ),
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

    expected_original_features = (
        len(numerical_features)
        + len(categorical_features)
    )


    if X_final.shape[1] != expected_original_features:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature count mismatch. "
                f"Expected "
                f"{expected_original_features}, "
                f"got "
                f"{X_final.shape[1]}"
            ),
        )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    fraud_probability = float(
        original_model.predict_proba(
            X_final
        )[0, 1]
    )


    prediction = int(
        fraud_probability >= 0.50
    )


    risk_level = classify_risk(
        fraud_probability
    )


    return {

        "transaction_id":
            transaction_id,

        "fraud_probability":
            round(
                fraud_probability,
                6,
            ),

        "prediction":
            prediction,

        "risk_level":
            risk_level,

        "model":
            "XGBOOST DAY 7 CHAMPION",

        "features":
            X_final.shape[1],

        "label_mapping": {
            "0": "LEGITIMATE",
            "1": "FRAUD",
        },
    }


# ============================================================
# 15. CUSTOM TRANSACTION PREDICTION
# ============================================================

@app.post("/predict/custom")
def predict_custom(
    transaction: CustomTransactionRequest,
):

    # --------------------------------------------------------
    # Build custom transaction
    # --------------------------------------------------------

    sample = build_custom_transaction(
        transaction
    )


    # --------------------------------------------------------
    # Prepare custom features
    # --------------------------------------------------------

    X_custom = (
        preprocess_custom_transaction(
            sample
        )
    )


    # --------------------------------------------------------
    # Verify feature count
    # --------------------------------------------------------

    expected_custom_features = len(
        custom_selected_features
    )


    if X_custom.shape[1] != expected_custom_features:

        raise HTTPException(
            status_code=500,
            detail=(
                "Custom feature count "
                "mismatch. "
                f"Expected "
                f"{expected_custom_features}, "
                f"got "
                f"{X_custom.shape[1]}"
            ),
        )


    # --------------------------------------------------------
    # Prediction
    #
    # The saved sklearn Pipeline performs:
    #
    # numeric imputation
    # categorical imputation
    # one-hot encoding
    # XGBoost prediction
    # --------------------------------------------------------

    fraud_probability = float(
        custom_model.predict_proba(
            X_custom
        )[0, 1]
    )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # The CURRENT trained model metadata says:
    #
    # threshold = 0.14
    #
    # Therefore we MUST NOT use 0.50 here.
    # --------------------------------------------------------

    prediction = int(
        fraud_probability
        >= custom_threshold
    )


    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

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
                6,
            ),

        "prediction":
            prediction,

        "risk_level":
            risk_level,

        "model":
            "XGBOOST CUSTOM SCREENING MODEL",

        "features":
            X_custom.shape[1],

        "classification_threshold":
            custom_threshold,

        "label_mapping":
            custom_label_mapping,
    }