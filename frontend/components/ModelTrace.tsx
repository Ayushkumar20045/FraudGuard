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
  const hasResult = Boolean(result);

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
          value={
            hasResult
              ? "RECEIVED"
              : "WAITING"
          }
        />

        <TraceConnector />

        <TraceStep
          number="02"
          title="PREPROCESSING"
          value={
            hasResult
              ? "COMPLETE"
              : "PENDING"
          }
        />

        <TraceConnector />

        <TraceStep
          number="03"
          title="FEATURE VECTOR"
          value={
            result
              ? `${result.features} DIMENSIONS`
              : "—"
          }
        />

        <TraceConnector />

        <TraceStep
          number="04"
          title="MODEL"
          value={
            result
              ? result.model
              : "READY"
          }
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
              ? result.prediction === 1
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