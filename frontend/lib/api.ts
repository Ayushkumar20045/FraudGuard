export type RiskLevel =
  | "LOW"
  | "MEDIUM"
  | "HIGH";


export type CustomTransaction = {
  transaction_amount: number;

  transaction_hour: number;

  card_network: string;

  card_type: string;

  transaction_distance:
    | number
    | null;

  purchaser_email_domain:
    | string
    | null;

  device_type:
    | string
    | null;

  device_info:
    | string
    | null;

  identity_available: boolean;
};


export type PredictionResult = {
  fraud_probability: number;

  prediction: number;

  risk_level: RiskLevel;

  model: string;

  features: number;
};


const API_URL =
  "http://127.0.0.1:8000";


export async function predictCustomTransaction(
  transaction: CustomTransaction
): Promise<PredictionResult> {

  const response = await fetch(
    `${API_URL}/predict/custom`,
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


  let data: any;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Invalid response received from FraudGuard API."
    );
  }


  if (!response.ok) {
    throw new Error(
      data?.detail ||
        "Transaction analysis failed."
    );
  }


  return data as PredictionResult;
}