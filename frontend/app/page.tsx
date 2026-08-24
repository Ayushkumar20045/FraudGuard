"use client";

import { useState } from "react";

import Header from "../components/Header";
import Footer from "../components/Footer";
import TransactionForm from "../components/TransactionForm";
import SnapshotPanel from "../components/SnapshotPanel";
import VerdictPanel from "../components/VerdictPanel";
import RiskEvidence from "../components/RiskEvidence";
import ModelTrace from "../components/ModelTrace";

import type { PredictionResult } from "../lib/api";

export default function Home() {
  const [result, setResult] =
    useState<PredictionResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  return (
    <main
      className={`fraudguard ${
        result
          ? result.risk_level.toLowerCase()
          : "neutral"
      }`}
    >

      <Header />

      <div className="workspace">

        {/* ==========================================
            TRANSACTION INPUT
        ========================================== */}

        <TransactionForm
          onResult={(prediction) => {
            setResult(prediction);
            setError("");
          }}
          onLoading={setLoading}
          onError={setError}
        />

        {/* ==========================================
            API ERROR
        ========================================== */}

        {error && (
          <div className="api-error">
            <span>!</span>
            {error}
          </div>
        )}

        {/* ==========================================
            LIVE ANALYSIS
        ========================================== */}

        <section className="analysis-grid">

          <SnapshotPanel
            result={result}
          />

          <VerdictPanel
            result={result}
          />

          <RiskEvidence
            result={result}
          />

        </section>

        {/* ==========================================
            MODEL TRACE
        ========================================== */}

        <ModelTrace
          result={result}
        />

      </div>

      <Footer />

      {loading && (
        <div className="analysis-overlay">
          <div className="analysis-loader">
            <span />
            <span />
            <span />
          </div>

          <div className="analysis-loader-text">
            RUNNING FRAUD ANALYSIS
          </div>

          <div className="analysis-loader-sub">
            XGBOOST DAY 7 CHAMPION
          </div>
        </div>
      )}

    </main>
  );
}