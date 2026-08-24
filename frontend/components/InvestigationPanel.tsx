type InvestigationPanelProps = {
  transactionId: string;
  loading: boolean;
  error: string;
  onTransactionIdChange: (
    value: string
  ) => void;
  onInvestigate: () => void;
};

export default function InvestigationPanel({
  transactionId,
  loading,
  error,
  onTransactionIdChange,
  onInvestigate,
}: InvestigationPanelProps) {
  return (
    <section className="investigation-panel">

      <div className="section-header">

        <div>

          <span className="section-number">
            01
          </span>

          <span className="section-name">
            TRANSACTION INVESTIGATION
          </span>

        </div>

        <span className="section-source">
          IEEE-CIS / TRAIN TRANSACTION
        </span>

      </div>

      <div className="investigation-row">

        <div className="transaction-input">

          <span className="tx-label">
            TX
          </span>

          <span className="input-divider" />

          <input
            value={transactionId}
            onChange={(e) =>
              onTransactionIdChange(e.target.value)
            }
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onInvestigate();
              }
            }}
            placeholder="TransactionID"
            type="number"
          />

          <span className="input-type">
            INTEGER
          </span>

        </div>

        <button
          className="analyze-button"
          onClick={onInvestigate}
          disabled={loading}
        >
          {loading
            ? "ANALYZING..."
            : "ANALYZE TRANSACTION"}

          <span>→</span>
        </button>

      </div>

      <div className="query-footer">

        <span>
          {loading
            ? "Running XGBoost inference..."
            : error
            ? "Analysis failed"
            : transactionId
            ? "Analysis complete"
            : "Ready to analyze transaction"}
        </span>

        <span>
          POST /predict
        </span>

      </div>

      {error && (
        <div className="api-error">

          <span>!</span>

          {error}

        </div>
      )}

    </section>
  );
}