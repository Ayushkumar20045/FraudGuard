import type { PredictionResult } from "../lib/api";
import PanelHeader from "./ui/PanelHeader";

type RiskEvidenceProps = {
  result: PredictionResult | null;
};

export default function RiskEvidence({
  result,
}: RiskEvidenceProps) {
  const risk = result?.risk_level || "LOW";

  const signals = [
    {
      name: "RISK LEVEL",
      position: "top",
      value: result ? risk : "UNASSESSED",
    },
    {
      name: "PREDICTION",
      position: "right",
      value: result
        ? result.prediction === 1
          ? "FRAUD"
          : "LEGITIMATE"
        : "UNASSESSED",
    },
    {
      name: "FEATURE SPACE",
      position: "bottom",
      value: result
        ? `${result.features} DIMENSIONS`
        : "UNASSESSED",
    },
    {
      name: "MODEL",
      position: "left",
      value: result
        ? "XGBOOST"
        : "UNASSESSED",
    },
  ];

  return (
    <section className="dashboard-panel evidence-panel">

      <PanelHeader
        number="04"
        title="MODEL SIGNALS"
        meta="DERIVED OUTPUTS"
      />

      <div className="evidence-content">

        <div className="evidence-radar">

          <div className="radar-ring ring-one" />
          <div className="radar-ring ring-two" />
          <div className="radar-ring ring-three" />

          <div className="radar-cross horizontal" />
          <div className="radar-cross vertical" />

          {signals.map((signal) => (
            <div
              key={signal.name}
              className={`evidence-node ${signal.position}`}
            >

              <div className="node-line" />

              <div className="node-circle">
                <span />
              </div>

              <div className="node-label">

                <strong>
                  {signal.name}
                </strong>

                <small>
                  {signal.value}
                </small>

              </div>

            </div>
          ))}

          <div className="evidence-core">

            <span>
              FRAUD PROBABILITY
            </span>

            <strong>
              {result
                ? `${(result.fraud_probability * 100).toFixed(2)}%`
                : "—"}
            </strong>

            <small>
              {result
                ? risk
                : "UNASSESSED"}
            </small>

          </div>

        </div>

        <div className="risk-legend">

          <span className="legend-high">
            ● HIGH RISK
          </span>

          <span className="legend-medium">
            ● MEDIUM RISK
          </span>

          <span className="legend-low">
            ● LOW RISK
          </span>

          <span className="legend-none">
            ● UNASSESSED
          </span>

        </div>

      </div>

    </section>
  );
}