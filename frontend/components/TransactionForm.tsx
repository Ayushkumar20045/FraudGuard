"use client";

import { useState } from "react";

import {
  predictCustomTransaction,
  type CustomTransaction,
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
  const [form, setForm] = useState({
    transaction_amount: 250.5,
    transaction_hour: new Date().getHours(),

    card_network: "visa",
    card_type: "credit",

    transaction_distance: 12.5,

    purchaser_email_domain: "gmail.com",

    device_type: "mobile",
    device_info: "iPhone",

    identity_available: true,
  });

  function updateField(
    field: keyof typeof form,
    value: string | number | boolean | null
  ) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    onLoading(true);
    onError("");

    try {
      const payload: CustomTransaction = {
        transaction_amount: Number(
          form.transaction_amount
        ),

        transaction_hour: Number(
          form.transaction_hour
        ),

        card_network: form.card_network,

        card_type: form.card_type,

        transaction_distance:
          form.transaction_distance === null
            ? null
            : Number(form.transaction_distance),

        purchaser_email_domain:
          form.purchaser_email_domain
            ?.trim()
            .toLowerCase() || null,

        device_type:
          form.device_type || null,

        device_info:
          form.device_info?.trim() || null,

        identity_available:
          form.identity_available,
      };

      const result =
        await predictCustomTransaction(payload);

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
      {/* HEADER */}

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

      {/* FORM */}

      <form
        className="transaction-form"
        onSubmit={handleSubmit}
      >
        <div className="form-grid">

          {/* TRANSACTION AMOUNT */}

          <div className="form-field">
            <label>
              TRANSACTION AMOUNT
            </label>

            <div className="input-wrapper">
              <span className="input-prefix">
                ₹
              </span>

              <input
                type="number"
                min="0"
                step="0.01"
                value={
                  form.transaction_amount
                }
                onChange={(event) =>
                  updateField(
                    "transaction_amount",
                    event.target.value === ""
                      ? 0
                      : Number(event.target.value)
                  )
                }
                placeholder="250.50"
                required
              />
            </div>

            <span className="field-hint">
              Transaction amount in INR
            </span>
          </div>

          {/* TRANSACTION HOUR */}

          <div className="form-field">
            <label>
              TRANSACTION HOUR
            </label>

            <input
              type="number"
              min="0"
              max="23"
              value={
                form.transaction_hour
              }
              onChange={(event) =>
                updateField(
                  "transaction_hour",
                  event.target.value === ""
                    ? 0
                    : Number(event.target.value)
                )
              }
              required
            />

            <span className="field-hint">
              0–23 hour format
            </span>
          </div>

          {/* CARD NETWORK */}

          <div className="form-field">
            <label>
              CARD NETWORK
            </label>

            <select
              value={
                form.card_network
              }
              onChange={(event) =>
                updateField(
                  "card_network",
                  event.target.value
                )
              }
            >
              <option value="visa">
                Visa
              </option>

              <option value="mastercard">
                Mastercard
              </option>

              <option value="american express">
                American Express
              </option>

              <option value="discover">
                Discover
              </option>
            </select>
          </div>

          {/* CARD TYPE */}

          <div className="form-field">
            <label>
              CARD TYPE
            </label>

            <select
              value={
                form.card_type
              }
              onChange={(event) =>
                updateField(
                  "card_type",
                  event.target.value
                )
              }
            >
              <option value="credit">
                Credit
              </option>

              <option value="debit">
                Debit
              </option>
            </select>
          </div>

          {/* TRANSACTION DISTANCE */}

          <div className="form-field">
            <label>
              TRANSACTION DISTANCE
            </label>

            <div className="input-wrapper">
              <input
                type="number"
                min="0"
                step="0.1"
                value={
                  form.transaction_distance ??
                  ""
                }
                onChange={(event) =>
                  updateField(
                    "transaction_distance",
                    event.target.value === ""
                      ? null
                      : Number(
                          event.target.value
                        )
                  )
                }
                placeholder="12.5"
              />

              <span className="input-suffix">
                KM
              </span>
            </div>

            <span className="field-hint">
              Distance associated with transaction
            </span>
          </div>

          {/* EMAIL DOMAIN */}

          <div className="form-field">
            <label>
              PURCHASER EMAIL DOMAIN
            </label>

            <input
              type="text"
              value={
                form.purchaser_email_domain ??
                ""
              }
              onChange={(event) =>
                updateField(
                  "purchaser_email_domain",
                  event.target.value
                )
              }
              placeholder="gmail.com"
            />

            <span className="field-hint">
              Example: gmail.com
            </span>
          </div>

          {/* DEVICE TYPE */}

          <div className="form-field">
            <label>
              DEVICE TYPE
            </label>

            <select
              value={
                form.device_type ?? ""
              }
              onChange={(event) =>
                updateField(
                  "device_type",
                  event.target.value
                )
              }
            >
              <option value="mobile">
                Mobile
              </option>

              <option value="desktop">
                Desktop
              </option>

              <option value="tablet">
                Tablet
              </option>
            </select>
          </div>

          {/* DEVICE INFORMATION */}

          <div className="form-field">
            <label>
              DEVICE INFORMATION
            </label>

            <input
              type="text"
              value={
                form.device_info ?? ""
              }
              onChange={(event) =>
                updateField(
                  "device_info",
                  event.target.value
                )
              }
              placeholder="iPhone"
            />

            <span className="field-hint">
              Device or browser information
            </span>
          </div>

          {/* IDENTITY INFORMATION */}

          <div className="form-field">
            <label>
              IDENTITY INFORMATION
            </label>

            <select
              value={
                form.identity_available
                  ? "available"
                  : "unavailable"
              }
              onChange={(event) =>
                updateField(
                  "identity_available",
                  event.target.value ===
                    "available"
                )
              }
            >
              <option value="available">
                Available
              </option>

              <option value="unavailable">
                Unavailable
              </option>
            </select>

            <span className="field-hint">
              Whether identity data is available
            </span>
          </div>

        </div>

        {/* FORM FOOTER */}

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
              XGBOOST CUSTOM SCREENING MODEL
            </span>
          </div>

          <button
            type="submit"
            className="analyze-button"
          >
            RUN FRAUD ANALYSIS

            <span>
              →
            </span>
          </button>
        </div>
      </form>
    </section>
  );
}