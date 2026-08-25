export type RiskLevel =
  | "LOW"
  | "MEDIUM"
  | "HIGH";

export type TransactionRequest = {
  TransactionID: number;
};

export type PredictionResult = {
  transaction_id: number;

  fraud_probability: number;

  prediction: number;

  risk_level: RiskLevel;

  model: string;

  features: number;

  classification_threshold?: number;
};

const API_URL =
  "http://127.0.0.1:8000";

export async function predictTransaction(
  transaction: TransactionRequest
): Promise<PredictionResult> {

  const response = await fetch(
    `${API_URL}/predict`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        transaction
      ),
    }
  );

  let data: unknown;

  try {

    data = await response.json();

  } catch {

    throw new Error(
      "Invalid response received from FraudGuard API."
    );

  }

  if (!response.ok) {

    const errorData =
      data as {
        detail?: string;
      };

    throw new Error(
      errorData.detail ||
        "Transaction analysis failed."
    );

  }

  return data as PredictionResult;
}