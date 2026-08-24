import requests


API_URL = "http://127.0.0.1:8000/predict"


FRAUD_TRANSACTION_IDS = [
    2987203,
    2987240,
    2987243,
    2987245,
    2987288,
    2987367,
    2987405,
    2987630,
    2987683,
    2987736,
]


def test_fraud_transactions():
    print()
    print("=" * 90)
    print("FRAUDGUARD — REAL FRAUD TRANSACTION VALIDATION")
    print("=" * 90)

    print(
        f"{'TRANSACTION ID':<18}"
        f"{'ACTUAL':<12}"
        f"{'PROBABILITY':<16}"
        f"{'PREDICTION':<14}"
        f"{'RISK':<12}"
        f"{'RESULT':<10}"
    )

    print("-" * 90)

    correct = 0
    failed = 0

    for transaction_id in FRAUD_TRANSACTION_IDS:

        try:
            response = requests.post(
                API_URL,
                json={
                    "TransactionID": transaction_id
                },
                timeout=30,
            )

            response.raise_for_status()

            result = response.json()

            probability = (
                result["fraud_probability"] * 100
            )

            prediction = result["prediction"]
            risk = result["risk_level"]

            actual = "FRAUD"

            if prediction == 1:
                status = "PASS"
                correct += 1
            else:
                status = "MISS"
                failed += 1

            print(
                f"{transaction_id:<18}"
                f"{actual:<12}"
                f"{probability:>8.2f}%{'':<7}"
                f"{'FRAUD' if prediction == 1 else 'LEGIT':<14}"
                f"{risk:<12}"
                f"{status:<10}"
            )

        except requests.exceptions.RequestException as error:

            failed += 1

            print(
                f"{transaction_id:<18}"
                f"{'FRAUD':<12}"
                f"{'API ERROR':<16}"
                f"{'-':<14}"
                f"{'-':<12}"
                f"FAIL"
            )

            print(f"  Error: {error}")

    total = len(FRAUD_TRANSACTION_IDS)

    accuracy = (
        (correct / total) * 100
        if total > 0
        else 0
    )

    print("-" * 90)

    print()
    print("VALIDATION SUMMARY")
    print("-" * 40)

    print(f"Fraud transactions tested : {total}")
    print(f"Correctly detected         : {correct}")
    print(f"Missed fraud transactions  : {failed}")
    print(f"Detection rate             : {accuracy:.2f}%")

    print()

    if correct == total:
        print("STATUS: ALL FRAUD TRANSACTIONS DETECTED")
    elif correct > 0:
        print("STATUS: PARTIAL FRAUD DETECTION")
    else:
        print("STATUS: FRAUD DETECTION FAILED")

    print()
    print("=" * 90)


if __name__ == "__main__":
    test_fraud_transactions()