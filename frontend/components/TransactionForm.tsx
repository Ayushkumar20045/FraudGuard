"use client";

import { FormEvent, useState } from "react";
import { predictTransaction } from "../lib/api";

interface TransactionFormProps {
  onResult: (result: any) => void;
  onLoading?: (loading: boolean) => void;
}

const MIN_TRANSACTION_ID = 2987000;
const MAX_TRANSACTION_ID = 3577539;

const SAMPLE_TRANSACTION_IDS = [
  2987000,
  2988250,
  3000000,
  3200000,
  3400000,
  3577539,
];

export default function TransactionForm({
  onResult,
  onLoading,
}: TransactionFormProps) {
  const [transactionId, setTransactionId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");

    const parsedTransactionId = Number(transactionId);

    if (
      !Number.isInteger(parsedTransactionId) ||
      parsedTransactionId < MIN_TRANSACTION_ID ||
      parsedTransactionId > MAX_TRANSACTION_ID
    ) {
      setError(
        `Transaction ID must be between ${MIN_TRANSACTION_ID} and ${MAX_TRANSACTION_ID}.`
      );
      return;
    }

    try {
      setLoading(true);
      onLoading?.(true);

      const result = await predictTransaction({
        TransactionID: parsedTransactionId,
      });

      onResult(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze transaction."
      );
    } finally {
      setLoading(false);
      onLoading?.(false);
    }
  }

  return (
    <section className="investigation-panel">
      <div className="section-header">
        <div>
          <span className="section-number">01</span>
          <span className="section-name">
            TRANSACTION INVESTIGATION
          </span>
        </div>

        <span className="section-source">
          IEEE-CIS FRAUD DETECTION
        </span>
      </div>

      <form
        className="investigation-main"
        onSubmit={handleSubmit}
      >
        <div className="investigation-input-area">
          <span className="data-label">
            TRANSACTION ID
          </span>

          <div className="transaction-input">
            <span className="tx-label">TX</span>

            <span className="input-divider" />

            <input
              type="number"
              min={MIN_TRANSACTION_ID}
              max={MAX_TRANSACTION_ID}
              step="1"
              value={transactionId}
              onChange={(event) =>
                setTransactionId(event.target.value)
              }
              placeholder="2987000"
              list="transaction-id-suggestions"
              required
            />

            <span className="input-type">
              INTEGER
            </span>
          </div>

          <datalist id="transaction-id-suggestions">
            {SAMPLE_TRANSACTION_IDS.map((id) => (
              <option key={id} value={id} />
            ))}
          </datalist>

          <span className="transaction-helper">
            Valid IEEE-CIS IDs: {MIN_TRANSACTION_ID} —{" "}
            {MAX_TRANSACTION_ID}
          </span>
        </div>

        {error && (
          <div className="api-error">
            <span>!</span>
            {error}
          </div>
        )}

        <div className="system-status-strip">
          <div className="status-block">
            <span className="status-indicator" />

            <div>
              <small>INFERENCE ENGINE</small>
              <strong>
                XGBOOST DAY 7 CHAMPION
              </strong>
            </div>
          </div>

          <div className="status-divider" />

          <div className="status-block">
            <span className="status-indicator" />

            <div>
              <small>FEATURE SPACE</small>
              <strong>891 FEATURES</strong>
            </div>
          </div>

          <div className="status-divider" />

          <div className="status-block">
            <span className="status-indicator" />

            <div>
              <small>CLASSIFICATION</small>
              <strong>
                LEGITIMATE / FRAUD
              </strong>
            </div>
          </div>
        </div>

        <div className="investigation-action">
          <div className="model-ready">
            <span className="ready-pulse" />

            <span>
              {loading
                ? "ANALYZING TRANSACTION..."
                : "MODEL READY FOR INFERENCE"}
            </span>
          </div>

          <button
            type="submit"
            className="analyze-button"
            disabled={loading}
          >
            <span className="button-label">
              {loading
                ? "ANALYZING..."
                : "INVESTIGATE TRANSACTION"}
            </span>

            <span className="button-arrow">
              →
            </span>
          </button>
        </div>
      </form>
    </section>
  );
}