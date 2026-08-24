import requests
import pandas as pd
from pathlib import Path


# ============================================================
# FRAUDGUARD — REAL TRANSACTION CUSTOM MODEL VALIDATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"

API_URL = "http://127.0.0.1:8000/predict/custom"


print("=" * 105)
print("FRAUDGUARD — REAL TRANSACTION CUSTOM MODEL VALIDATION")
print("=" * 105)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\nLoading transaction data...")

transactions = pd.read_csv(
    DATA_RAW / "train_transaction.csv"
)

identity = pd.read_csv(
    DATA_RAW / "train_identity.csv"
)

print(f"Transaction data: {transactions.shape}")
print(f"Identity data:    {identity.shape}")


# ============================================================
# 2. MERGE DATA
# ============================================================

data = transactions.merge(
    identity,
    on="TransactionID",
    how="left"
)


# ============================================================
# 3. SELECT REAL FRAUD + LEGITIMATE TRANSACTIONS
# ============================================================

fraud = (
    data[data["isFraud"] == 1]
    .head(10)
)

legitimate = (
    data[data["isFraud"] == 0]
    .head(10)
)

test_data = pd.concat(
    [fraud, legitimate],
    ignore_index=True
)


# ============================================================
# 4. CONVERT REAL DATA → FRONTEND FORMAT
# ============================================================

def build_payload(row):

    transaction_dt = row["TransactionDT"]

    transaction_hour = int(
        (transaction_dt // 3600) % 24
    )

    return {
        "transaction_amount": float(
            row["TransactionAmt"]
        ),

        "transaction_hour": transaction_hour,

        "card_network": (
            str(row["card4"])
            if pd.notna(row["card4"])
            else "unknown"
        ),

        "card_type": (
            str(row["card6"])
            if pd.notna(row["card6"])
            else "unknown"
        ),

        "transaction_distance": (
            float(row["dist1"])
            if pd.notna(row["dist1"])
            else None
        ),

        "purchaser_email_domain": (
            str(row["P_emaildomain"])
            if pd.notna(row["P_emaildomain"])
            else None
        ),

        "device_type": (
            str(row["DeviceType"])
            if pd.notna(row["DeviceType"])
            else None
        ),

        "device_info": (
            str(row["DeviceInfo"])
            if pd.notna(row["DeviceInfo"])
            else None
        ),

        "identity_available": bool(
            pd.notna(row["id_01"])
        ),
    }


# ============================================================
# 5. TEST TRANSACTIONS
# ============================================================

results = []


print("\nTesting real transactions...\n")

for _, row in test_data.iterrows():

    transaction_id = int(
        row["TransactionID"]
    )

    actual = int(
        row["isFraud"]
    )

    payload = build_payload(row)

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

        probability = float(
            result["fraud_probability"]
        )

        prediction = int(
            result["prediction"]
        )

        risk = result["risk_level"]

        correct = (
            prediction == actual
        )

        results.append({
            "TransactionID": transaction_id,
            "Actual": actual,
            "Probability": probability,
            "Prediction": prediction,
            "Risk": risk,
            "Result": (
                "PASS"
                if correct
                else "MISS"
            ),
        })

    except Exception as error:

        print(
            f"ERROR — Transaction "
            f"{transaction_id}: {error}"
        )


# ============================================================
# 6. DISPLAY RESULTS
# ============================================================

results_df = pd.DataFrame(results)


print("=" * 105)

print(
    f"{'TRANSACTION ID':<17}"
    f"{'ACTUAL':<12}"
    f"{'PROBABILITY':<16}"
    f"{'PREDICTION':<14}"
    f"{'RISK':<10}"
    f"{'RESULT':<10}"
)

print("-" * 105)


for _, row in results_df.iterrows():

    actual_text = (
        "FRAUD"
        if row["Actual"] == 1
        else "LEGITIMATE"
    )

    prediction_text = (
        "FRAUD"
        if row["Prediction"] == 1
        else "LEGITIMATE"
    )

    print(
        f"{int(row['TransactionID']):<17}"
        f"{actual_text:<12}"
        f"{row['Probability'] * 100:>7.2f}%"
        f"{'':<9}"
        f"{prediction_text:<14}"
        f"{row['Risk']:<10}"
        f"{row['Result']:<10}"
    )


# ============================================================
# 7. METRICS
# ============================================================

fraud_results = results_df[
    results_df["Actual"] == 1
]

legitimate_results = results_df[
    results_df["Actual"] == 0
]

fraud_detected = (
    fraud_results["Prediction"] == 1
).sum()

fraud_missed = (
    fraud_results["Prediction"] == 0
).sum()

legitimate_correct = (
    legitimate_results["Prediction"] == 0
).sum()

false_positives = (
    legitimate_results["Prediction"] == 1
).sum()


fraud_detection_rate = (
    fraud_detected / len(fraud_results)
    if len(fraud_results)
    else 0
)

legitimate_detection_rate = (
    legitimate_correct / len(legitimate_results)
    if len(legitimate_results)
    else 0
)

overall_accuracy = (
    (results_df["Result"] == "PASS").sum()
    / len(results_df)
    if len(results_df)
    else 0
)


# ============================================================
# 8. SUMMARY
# ============================================================

print("\n")
print("=" * 105)
print("VALIDATION SUMMARY")
print("=" * 105)

print(
    f"Fraud transactions tested       : "
    f"{len(fraud_results)}"
)

print(
    f"Fraud correctly detected        : "
    f"{fraud_detected}"
)

print(
    f"Fraud missed                    : "
    f"{fraud_missed}"
)

print(
    f"Fraud detection rate            : "
    f"{fraud_detection_rate * 100:.2f}%"
)

print()

print(
    f"Legitimate transactions tested  : "
    f"{len(legitimate_results)}"
)

print(
    f"Legitimate correctly identified : "
    f"{legitimate_correct}"
)

print(
    f"False positives                 : "
    f"{false_positives}"
)

print(
    f"Legitimate detection rate       : "
    f"{legitimate_detection_rate * 100:.2f}%"
)

print()

print(
    f"Overall accuracy                : "
    f"{overall_accuracy * 100:.2f}%"
)

print("=" * 105)


if fraud_missed == 0:

    print(
        "\nSTATUS: ALL TESTED FRAUD TRANSACTIONS DETECTED"
    )

else:

    print(
        f"\nSTATUS: {fraud_missed} FRAUD TRANSACTION(S) MISSED"
    )


print("=" * 105)