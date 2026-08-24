import type { PredictionResult } from "../lib/api";
import PanelHeader from "./ui/PanelHeader";

type RiskEvidenceProps = {
  result: PredictionResult | null;
};

export default function RiskEvidence({
  result,
}: RiskEvidenceProps) {
  const risk = result?.risk_level || "LOW";

  const labels = [
    {
      name: "IDENTITY",
      position: "top",
    },
    {
      name: "CARD",
      position: "right",
    },
    {
      name: "BEHAVIOR",
      position: "bottom",
    },
    {
      name: "ADDRESS",
      position: "left",
    },
  ];

  return (
    <section className="dashboard-panel evidence-panel">

      <PanelHeader
        number="04"
        title="RISK EVIDENCE"
        meta="SIGNAL GROUPS"
      />

      <div className="evidence-content">

        <div className="evidence-radar">

          <div className="radar-ring ring-one" />
          <div className="radar-ring ring-two" />
          <div className="radar-ring ring-three" />

          <div className="radar-cross horizontal" />
          <div className="radar-cross vertical" />

          {labels.map((signal) => (
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
                  {result
                    ? `${risk} RISK`
                    : "UNASSESSED"}
                </small>

              </div>

            </div>
          ))}

          <div className="evidence-core">

            <span>
              TX
            </span>

            <strong>
              {result
                ? result.transaction_id
                : "—"}
            </strong>

            <small>
              {result
                ? `${risk} RISK`
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