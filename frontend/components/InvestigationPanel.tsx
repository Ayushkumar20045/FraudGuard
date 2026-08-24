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

      {/* =====================================================
          HEADER
      ===================================================== */}

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
          LIVE TRANSACTION ANALYSIS
        </span>

      </div>


      {/* =====================================================
          MAIN INVESTIGATION AREA
      ===================================================== */}

      <div className="investigation-main">

        <div className="investigation-input-area">

          <span className="data-label">
            TRANSACTION ID
          </span>

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
              placeholder="Enter transaction ID"
              type="number"
              aria-label="Transaction ID"
            />

            <span className="input-type">
              INTEGER
            </span>

          </div>

          <span className="transaction-helper">
            IEEE-CIS transaction identifier
          </span>

        </div>


        {/* =================================================
            STATUS STRIP
        ================================================= */}

        <div className="system-status-strip">

          <div className="status-block">

            <span className="status-indicator active" />

            <div>
              <small>
                MODEL STATUS
              </small>

              <strong>
                {loading
                  ? "PROCESSING"
                  : "READY"}
              </strong>
            </div>

          </div>


          <div className="status-divider" />


          <div className="status-block">

            <span className="status-indicator active" />

            <div>
              <small>
                FEATURE PIPELINE
              </small>

              <strong>
                891 FEATURES
              </strong>
            </div>

          </div>


          <div className="status-divider" />


          <div className="status-block">

            <span className="status-indicator active" />

            <div>
              <small>
                INFERENCE CHANNEL
              </small>

              <strong>
                SECURE / LIVE
              </strong>
            </div>

          </div>

        </div>


        {/* =================================================
            ACTION ROW
        ================================================= */}

        <div className="investigation-action">

          <div className="model-ready">

            <span className="ready-pulse" />

            <span>
              {loading
                ? "RUNNING XGBOOST INFERENCE"
                : "MODEL READY / XGBOOST DAY 7 CHAMPION"}
            </span>

          </div>


          <button
            className="analyze-button"
            onClick={onInvestigate}
            disabled={loading}
          >

            <span className="button-label">
              {loading
                ? "ANALYZING TRANSACTION"
                : "INVESTIGATE TRANSACTION"}
            </span>

            <span className="button-arrow">
              →
            </span>

          </button>

        </div>

      </div>


      {/* =====================================================
          QUERY FOOTER
      ===================================================== */}

      <div className="query-footer">

        <span>
          {loading
            ? "Running XGBoost inference..."
            : error
            ? "Analysis failed"
            : transactionId
            ? "Transaction ready for investigation"
            : "Ready to analyze transaction"}
        </span>

        <span>
          POST /predict
        </span>

      </div>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="api-error">

          <span>!</span>

          {error}

        </div>
      )}

    </section>
  );
}