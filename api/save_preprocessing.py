import joblib
import numpy as np
import pandas as pd

from pathlib import Path
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "api" / "model"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# 2. Load raw data
# --------------------------------------------------

print("Loading training transaction data...")

train_transaction = pd.read_csv(
    DATA_RAW / "train_transaction.csv"
)

print(
    "Transaction shape:",
    train_transaction.shape
)


print("Loading training identity data...")

train_identity = pd.read_csv(
    DATA_RAW / "train_identity.csv"
)

print(
    "Identity shape:",
    train_identity.shape
)


# --------------------------------------------------
# 3. Merge
# --------------------------------------------------

train = train_transaction.merge(
    train_identity,
    on="TransactionID",
    how="left"
)

print(
    "Merged training shape:",
    train.shape
)


# --------------------------------------------------
# 4. EXACT Day 3 feature engineering
# --------------------------------------------------

SECONDS_PER_HOUR = 60 * 60
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR


train["transaction_hour"] = (
    (train["TransactionDT"] // SECONDS_PER_HOUR) % 24
)


train["transaction_day"] = (
    train["TransactionDT"] // SECONDS_PER_DAY
)


train["transaction_week"] = (
    train["transaction_day"] // 7
)


train["hour_sin"] = np.sin(
    2 * np.pi * train["transaction_hour"] / 24
)


train["hour_cos"] = np.cos(
    2 * np.pi * train["transaction_hour"] / 24
)


train["identity_present"] = (
    train["id_01"].notna().astype(int)
)


missingness_features = [
    col
    for col in train.columns
    if col not in [
        "TransactionID",
        "isFraud"
    ]
]


train["missing_feature_count"] = (
    train[missingness_features]
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

    train[f"{feature}_missing"] = (
        train[feature]
        .isna()
        .astype(int)
    )


# --------------------------------------------------
# 5. EXACT Day 7 train/validation split
# --------------------------------------------------

TRAIN_END_DAY = 145


train_data = train[
    train["transaction_day"] <= TRAIN_END_DAY
].copy()


validation_data = train[
    train["transaction_day"] > TRAIN_END_DAY
].copy()


TARGET = "isFraud"
ID_COLUMN = "TransactionID"


X_train = train_data.drop(
    columns=[
        TARGET,
        ID_COLUMN
    ]
)


y_train = train_data[TARGET]


X_validation = validation_data.drop(
    columns=[
        TARGET,
        ID_COLUMN
    ]
)


y_validation = validation_data[TARGET]


print(
    "Training shape:",
    X_train.shape
)

print(
    "Validation shape:",
    X_validation.shape
)


# --------------------------------------------------
# 6. Feature definitions
# --------------------------------------------------

numerical_features = (
    X_train
    .select_dtypes(
        include=["number"]
    )
    .columns
    .tolist()
)


categorical_features = (
    X_train
    .select_dtypes(
        include=["object", "category"]
    )
    .columns
    .tolist()
)


print(
    "Numerical features:",
    len(numerical_features)
)

print(
    "Categorical features:",
    len(categorical_features)
)


# --------------------------------------------------
# 7. Numerical preprocessing
# EXACT Day 7 logic
# --------------------------------------------------

numerical_imputer = SimpleImputer(
    strategy="median"
)


X_train_num = (
    numerical_imputer
    .fit_transform(
        X_train[numerical_features]
    )
)


X_validation_num = (
    numerical_imputer
    .transform(
        X_validation[numerical_features]
    )
)


print(
    "Numerical matrix:",
    X_train_num.shape
)


# --------------------------------------------------
# 8. Categorical rare-category mapping
# EXACT Day 7 logic
# --------------------------------------------------

RARE_THRESHOLD = 50

categorical_maps = {}


for feature in categorical_features:

    values = (
        X_train[feature]
        .fillna("__MISSING__")
    )

    counts = values.value_counts()

    frequent_categories = counts[
        counts >= RARE_THRESHOLD
    ].index

    categorical_maps[feature] = set(
        frequent_categories
    )


print(
    "Categorical mappings created:",
    len(categorical_maps)
)


# --------------------------------------------------
# 9. Categorical transformation
# --------------------------------------------------

def transform_categorical(
    df,
    categorical_columns,
    categorical_maps
):

    df = df[
        categorical_columns
    ].copy()

    for feature in categorical_columns:

        df[feature] = (
            df[feature]
            .fillna("__MISSING__")
        )

        frequent_categories = (
            categorical_maps[feature]
        )

        df[feature] = (
            df[feature]
            .where(
                df[feature].isin(
                    frequent_categories
                ),
                "__RARE__"
            )
        )

    return df


X_train_cat = transform_categorical(
    X_train,
    categorical_features,
    categorical_maps
)


X_validation_cat = transform_categorical(
    X_validation,
    categorical_features,
    categorical_maps
)


# --------------------------------------------------
# 10. One-hot encoding
# EXACT Day 7 logic
# --------------------------------------------------

categorical_encoder = OneHotEncoder(
    handle_unknown="ignore",
    sparse_output=True,
    dtype=np.float32
)


X_train_cat_encoded = (
    categorical_encoder
    .fit_transform(
        X_train_cat
    )
)


X_validation_cat_encoded = (
    categorical_encoder
    .transform(
        X_validation_cat
    )
)


print(
    "Categorical encoded matrix:",
    X_train_cat_encoded.shape
)


# --------------------------------------------------
# 11. Final feature verification
# --------------------------------------------------

total_features = (
    X_train_num.shape[1]
    + X_train_cat_encoded.shape[1]
)


print(
    "Total model features:",
    total_features
)


if X_train.shape[0] != 484847:
    raise ValueError(
        f"Expected 484847 training rows, "
        f"got {X_train.shape[0]}"
    )


if X_validation.shape[0] != 105693:
    raise ValueError(
        f"Expected 105693 validation rows, "
        f"got {X_validation.shape[0]}"
    )


if len(numerical_features) != 414:
    raise ValueError(
        f"Expected 414 numerical features, "
        f"got {len(numerical_features)}"
    )


if X_train_cat_encoded.shape[1] != 477:
    raise ValueError(
        f"Expected 477 categorical features, "
        f"got {X_train_cat_encoded.shape[1]}"
    )


if total_features != 891:
    raise ValueError(
        f"Expected 891 total features, "
        f"got {total_features}"
    )


# --------------------------------------------------
# 12. Save preprocessing artifacts
# --------------------------------------------------

joblib.dump(
    numerical_imputer,
    MODEL_DIR / "numerical_imputer.pkl"
)


joblib.dump(
    categorical_maps,
    MODEL_DIR / "categorical_maps.pkl"
)


joblib.dump(
    categorical_encoder,
    MODEL_DIR / "categorical_encoder.pkl"
)


joblib.dump(
    numerical_features,
    MODEL_DIR / "numerical_features.pkl"
)


joblib.dump(
    categorical_features,
    MODEL_DIR / "categorical_features.pkl"
)


# --------------------------------------------------
# 13. Save feature names
# --------------------------------------------------

encoded_feature_names = (
    categorical_encoder
    .get_feature_names_out(
        categorical_features
    )
    .tolist()
)


all_feature_names = (
    numerical_features
    + encoded_feature_names
)


pd.DataFrame({
    "feature": all_feature_names
}).to_csv(
    MODEL_DIR / "feature_names.csv",
    index=False
)


# --------------------------------------------------
# 14. Final confirmation
# --------------------------------------------------

print("\n" + "=" * 50)
print("PREPROCESSING ARTIFACTS SAVED")
print("=" * 50)

print(
    "Training rows:",
    X_train.shape[0]
)

print(
    "Validation rows:",
    X_validation.shape[0]
)

print(
    "Numerical features:",
    len(numerical_features)
)

print(
    "Categorical features:",
    len(categorical_features)
)

print(
    "Encoded categorical features:",
    len(encoded_feature_names)
)

print(
    "Total model features:",
    len(all_feature_names)
)

print(
    "Artifacts directory:",
    MODEL_DIR
)

print("=" * 50)