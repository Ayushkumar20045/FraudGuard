import PanelHeader from "./ui/PanelHeader";
import VerdictStat from "./ui/VerdictStat";
import type { PredictionResult } from "../lib/api";

type VerdictPanelProps = {
  result: PredictionResult | null;
};

export default function VerdictPanel({
  result,
}: VerdictPanelProps) {
  const probability = result
    ? result.fraud_probability * 100
    : 0;

  const isFraud =
    result?.prediction === 1;

  const verdict = result
    ? isFraud
      ? "FRAUD DETECTED"
      : "TRANSACTION CLEARED"
    : "AWAITING VERDICT";

  const prediction = result
    ? isFraud
      ? "FRAUD"
      : "LEGITIMATE"
    : "—";

  const threshold =
    result?.classification_threshold !== undefined
      ? result.classification_threshold
      : null;

  return (
    <section className="dashboard-panel verdict-panel">

      <PanelHeader
        number="03"
        title="RISK VERDICT"
        meta="MODEL OUTPUT"
      />

      <div className="verdict-content">

        {/* ==========================================
            FRAUD PROBABILITY
        ========================================== */}

        <div className="probability-section">

          <span className="data-label">
            ESTIMATED FRAUD PROBABILITY
          </span>

          <div className="probability">

            {result
              ? probability.toFixed(2)
              : "—"}

            <span>
              %
            </span>

          </div>

          <ProbabilityBar
            probability={probability}
          />

        </div>

        {/* ==========================================
            MODEL VERDICT
        ========================================== */}

        <div className="verdict-box">

          <div className="verdict-icon">
            {result
              ? isFraud
                ? "!"
                : "✓"
              : "!"}
          </div>

          <div className="verdict-message">

            <span className="data-label">
              MODEL VERDICT
            </span>

            <strong>
              {verdict}
            </strong>

          </div>

        </div>

        {/* ==========================================
            MODEL STATISTICS
        ========================================== */}

        <div className="verdict-stats">

          <VerdictStat
            label="RISK"
            value={
              result?.risk_level || "—"
            }
          />

          <VerdictStat
            label="PREDICTION"
            value={prediction}
          />

          <VerdictStat
            label="THRESHOLD"
            value={
              threshold !== null
                ? threshold.toFixed(2)
                : "—"
            }
          />

          <VerdictStat
            label="FEATURES"
            value={
              result
                ? String(result.features)
                : "—"
            }
          />

        </div>

      </div>

    </section>
  );
}

/* =========================================================
   PROBABILITY BAR
   ========================================================= */

type ProbabilityBarProps = {
  probability: number;
};

function ProbabilityBar({
  probability,
}: ProbabilityBarProps) {
  return (
    <>
      <div className="probability-bar">

        <div
          className="probability-fill"
          style={{
            width: `${Math.min(
              Math.max(probability, 0),
              100
            )}%`,
          }}
        />

      </div>

      <div className="probability-scale">

        <span>
          0
        </span>

        <span>
          25
        </span>

        <span>
          50
        </span>

        <span>
          75
        </span>

        <span>
          100
        </span>

      </div>
    </>
  );
}