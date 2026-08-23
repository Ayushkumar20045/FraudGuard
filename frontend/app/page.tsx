"use client";

import { useState } from "react";

export default function Home() {
  const [transactionId, setTransactionId] = useState("");

  return (
    <main className="fraudguard-shell">
      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <span>F</span>
          </div>

          <div>
            <div className="brand-name">FRAUDGUARD</div>
            <div className="brand-subtitle">
              TRANSACTION RISK ENGINE
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          <span>SYSTEM ONLINE</span>
          <span className="status-divider" />
          <span className="status-model">XGB-CHAMPION</span>
        </div>
      </header>

      {/* =====================================================
          MAIN
      ===================================================== */}

      <div className="workspace">

        {/* Eyebrow */}

        <div className="workspace-intro">
          <div className="section-index">
            CASE / 001
          </div>

          <div className="intro-copy">
            <h1>
              Transaction
              <span> investigation</span>
            </h1>

            <p>
              Evaluate a transaction through FraudGuard&apos;s
              behavioral and identity risk engine.
            </p>
          </div>
        </div>

        {/* =================================================
            QUERY BAR
        ================================================= */}

        <section className="query-section">

          <div className="query-label">
            <span className="query-number">01</span>
            TRANSACTION LOOKUP
          </div>

          <div className="query-row">

            <div className="query-input-wrap">
              <span className="input-prefix">TX</span>

              <input
                type="text"
                value={transactionId}
                onChange={(e) =>
                  setTransactionId(e.target.value)
                }
                placeholder="Enter TransactionID"
              />

              <span className="input-hint">
                IEEE-FRAUD / TRANSACTION
              </span>
            </div>

            <button className="investigate-button">
              <span>INVESTIGATE</span>
              <span className="button-arrow">↗</span>
            </button>

          </div>

        </section>

        {/* =================================================
            PRIMARY ANALYSIS
        ================================================= */}

        <section className="analysis-grid">

          {/* -----------------------------------------------
              TRANSACTION PROFILE
          ----------------------------------------------- */}

          <div className="panel transaction-panel">

            <div className="panel-header">
              <div>
                <span className="panel-index">02</span>
                <span className="panel-title">
                  TRANSACTION PROFILE
                </span>
              </div>

              <span className="panel-state">
                AWAITING INPUT
              </span>
            </div>

            <div className="profile-content">

              <div className="amount-block">
                <span className="data-label">
                  TRANSACTION AMOUNT
                </span>

                <div className="amount">
                  <span>$</span>—
                </div>
              </div>

              <div className="profile-grid">

                <DataPoint
                  label="TRANSACTION ID"
                  value="—"
                  mono
                />

                <DataPoint
                  label="CARD REFERENCE"
                  value="—"
                  mono
                />

                <DataPoint
                  label="BILLING ADDRESS"
                  value="—"
                  mono
                />

                <DataPoint
                  label="IDENTITY SIGNAL"
                  value="—"
                />

              </div>

            </div>
          </div>

          {/* -----------------------------------------------
              RISK ENGINE
          ----------------------------------------------- */}

          <div className="panel risk-panel">

            <div className="panel-header">
              <div>
                <span className="panel-index">03</span>
                <span className="panel-title">
                  RISK ENGINE
                </span>
              </div>

              <span className="engine-label">
                XGBOOST
              </span>
            </div>

            <div className="risk-content">

              <div className="risk-score">
                <span className="score-value">—</span>
                <span className="score-percent">%</span>
              </div>

              <div className="risk-caption">
                ESTIMATED FRAUD PROBABILITY
              </div>

              <div className="risk-track">
                <div className="risk-fill" />
              </div>

              <div className="risk-footer">
                <span>LOW</span>
                <span>MEDIUM</span>
                <span>HIGH</span>
              </div>

              <div className="verdict">
                <span className="verdict-dot" />
                <span>AWAITING VERDICT</span>
              </div>

            </div>
          </div>

        </section>

        {/* =================================================
            SIGNAL MATRIX
        ================================================= */}

        <section className="signals-section">

          <div className="section-heading-row">

            <div>
              <span className="section-number">
                04
              </span>

              <span className="section-title">
                SIGNAL MATRIX
              </span>
            </div>

            <span className="section-meta">
              MODEL INPUT GROUPS
            </span>

          </div>

          <div className="signal-grid">

            <Signal
              name="AMOUNT"
              description="Transaction value"
            />

            <Signal
              name="CARD"
              description="Payment identity"
            />

            <Signal
              name="ADDRESS"
              description="Location consistency"
            />

            <Signal
              name="IDENTITY"
              description="Customer identity"
            />

            <Signal
              name="DEVICE"
              description="Device fingerprint"
            />

            <Signal
              name="BEHAVIOR"
              description="Transaction behavior"
            />

          </div>

        </section>

        {/* =================================================
            MODEL TRACE
        ================================================= */}

        <section className="trace-section">

          <div className="trace-header">

            <div>
              <span className="section-number">
                05
              </span>

              <span className="section-title">
                MODEL TRACE
              </span>
            </div>

            <span className="section-meta">
              INFERENCE PIPELINE
            </span>

          </div>

          <div className="trace-line">

            <TraceStep
              number="01"
              title="INPUT"
              description="Transaction data"
            />

            <div className="trace-connector" />

            <TraceStep
              number="02"
              title="FEATURES"
              description="891 dimensions"
            />

            <div className="trace-connector" />

            <TraceStep
              number="03"
              title="XGBOOST"
              description="Champion model"
            />

            <div className="trace-connector" />

            <TraceStep
              number="04"
              title="VERDICT"
              description="Risk classification"
            />

          </div>

        </section>

      </div>

      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer className="footer">

        <div>
          FRAUDGUARD
          <span> / </span>
          MODEL INFERENCE SYSTEM
        </div>

        <div>
          891 FEATURES
          <span> · </span>
          XGB-CHAMPION
        </div>

      </footer>

    </main>
  );
}


/* ============================================================
   COMPONENTS
   ============================================================ */

function DataPoint({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="data-point">

      <span className="data-label">
        {label}
      </span>

      <span
        className={
          mono
            ? "data-value mono"
            : "data-value"
        }
      >
        {value}
      </span>

    </div>
  );
}


function Signal({
  name,
  description,
}: {
  name: string;
  description: string;
}) {
  return (
    <div className="signal-card">

      <div className="signal-top">

        <span className="signal-indicator" />

        <span className="signal-name">
          {name}
        </span>

        <span className="signal-status">
          —
        </span>

      </div>

      <div className="signal-description">
        {description}
      </div>

    </div>
  );
}


function TraceStep({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="trace-step">

      <div className="trace-number">
        {number}
      </div>

      <div>
        <div className="trace-title">
          {title}
        </div>

        <div className="trace-description">
          {description}
        </div>
      </div>

    </div>
  );
}