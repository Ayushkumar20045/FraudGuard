"use client";

import { useState } from "react";

import {
  predictTransaction,
  type TransactionRequest,
  type PredictionResult,
} from "../lib/api";

type TransactionFormProps = {
  onResult: (result: PredictionResult) => void;
  onLoading: (loading: boolean) => void;
  onError: (error: string) => void;
};

export default function TransactionForm({
  onResult,
  onLoading,
  onError,
}: TransactionFormProps) {
  const [transactionId, setTransactionId] =
    useState("");

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    onLoading(true);
    onError("");

    try {
      const parsedTransactionId =
        Number(transactionId);

      if (
        !Number.isInteger(parsedTransactionId) ||
        parsedTransactionId <= 0
      ) {
        throw new Error(
          "Please enter a valid TransactionID."
        );
      }

      const payload: TransactionRequest = {
        TransactionID: parsedTransactionId,
      };

      const result =
        await predictTransaction(payload);

      onResult(result);
    } catch (error) {
      onError(
        error instanceof Error
          ? error.message
          : "Unable to connect to FraudGuard API."
      );
    } finally {
      onLoading(false);
    }
  }

  return (
    <section className="dashboard-panel investigation-panel">
      <div className="panel-header">
        <div>
          <span className="section-number">
            01
          </span>

          <span className="section-name">
            TRANSACTION INVESTIGATION
          </span>
        </div>

        <span className="panel-meta">
          LIVE TRANSACTION ANALYSIS
        </span>
      </div>

      <form
        className="transaction-form"
        onSubmit={handleSubmit}
      >
        <div className="form-grid">
          <div className="form-field">
            <label>
              TRANSACTION ID
            </label>

            <div className="input-wrapper">
              <span className="input-prefix">
                TX
              </span>

              <input
                type="number"
                min="1"
                value={transactionId}
                onChange={(event) =>
                  setTransactionId(
                    event.target.value
                  )
                }
                placeholder="2987000"
                required
              />
            </div>

            <span className="field-hint">
              IEEE-CIS transaction identifier
            </span>
          </div>
        </div>

        <div className="form-actions">
          <div className="form-status">
            <span className="status-dot" />

            <span>
              MODEL READY
            </span>

            <span className="status-divider">
              /
            </span>

            <span>
              XGBOOST DAY 7 CHAMPION
            </span>
          </div>

          <button
            type="submit"
            className="analyze-button"
          >
            INVESTIGATE TRANSACTION

            <span>
              →
            </span>
          </button>
        </div>
      </form>
    </section>
  );
}
