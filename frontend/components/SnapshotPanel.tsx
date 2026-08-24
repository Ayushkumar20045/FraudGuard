import PanelHeader from "./ui/PanelHeader";
import SnapshotRow from "./ui/SnapshotRow";
import type { PredictionResult } from "../lib/api";

type SnapshotPanelProps = {
  result: PredictionResult | null;
};

export default function SnapshotPanel({
  result,
}: SnapshotPanelProps) {
  return (
    <section className="dashboard-panel snapshot-panel">

      <PanelHeader
        number="02"
        title="TRANSACTION SNAPSHOT"
        meta={
          result
            ? "ANALYSIS COMPLETE"
            : "AWAITING INPUT"
        }
      />

      <div className="snapshot-content">

        <div className="transaction-id-block">

          <span className="data-label">
            TRANSACTION ID
          </span>

          <div className="large-id">
            {result
              ? result.transaction_id
              : "—"}
          </div>

        </div>

        <SnapshotRow
          label="DATA SOURCE"
          value="IEEE-CIS"
        />

        <SnapshotRow
          label="FEATURE SPACE"
          value="891 DIMENSIONS"
        />

        <SnapshotRow
          label="MODEL"
          value="XGBOOST DAY 7 CHAMPION"
        />

        <SnapshotRow
          label="INFERENCE"
          value={
            result
              ? "● COMPLETE"
              : "● STANDBY"
          }
          status
        />

      </div>

    </section>
  );
}