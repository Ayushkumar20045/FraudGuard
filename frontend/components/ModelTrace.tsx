import PanelHeader from "./ui/PanelHeader";
import TraceStep from "./ui/TraceStep";
import type { PredictionResult } from "../lib/api";

type ModelTraceProps = {
  result: PredictionResult | null;
};

function TraceConnector() {
  return (
    <div className="trace-connector">
      <span />
      <span />
    </div>
  );
}

export default function ModelTrace({
  result,
}: ModelTraceProps) {
  return (
    <section className="dashboard-panel trace-panel">

      <PanelHeader
        number="05"
        title="MODEL TRACE"
        meta="INFERENCE PIPELINE"
      />

      <div className="trace">

        <TraceStep
          number="01"
          title="RAW INPUT"
          value="RECEIVED"
        />

        <TraceConnector />

        <TraceStep
          number="02"
          title="FEATURE ENGINEERING"
          value="891 FEATURES"
        />

        <TraceConnector />

        <TraceStep
          number="03"
          title="FEATURE VECTOR"
          value="891 DIMENSIONS"
        />

        <TraceConnector />

        <TraceStep
          number="04"
          title="XGBOOST"
          value="DAY 7 CHAMPION"
        />

        <TraceConnector />

        <TraceStep
          number="05"
          title="RISK SCORE"
          value={
            result
              ? result.fraud_probability.toFixed(6)
              : "—"
          }
        />

        <TraceConnector />

        <TraceStep
          number="06"
          title="VERDICT"
          value={
            result
              ? result.risk_level === "HIGH"
                ? "FRAUD"
                : "CLEARED"
              : "PENDING"
          }
          final
        />

      </div>

    </section>
  );
}