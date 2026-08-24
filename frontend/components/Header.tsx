export default function Header() {
  return (
    <header className="topbar">

      <div className="brand">

        <div className="brand-shield">
          <span>FG</span>
        </div>

        <div>
          <div className="brand-name">
            FRAUDGUARD
          </div>

          <div className="brand-subtitle">
            RISK INTELLIGENCE SYSTEM
          </div>
        </div>

      </div>

      <nav className="navigation">

        <span className="nav-active">
          / INVESTIGATE
        </span>

        <span>/</span>

        <span>
          TRANSACTION ANALYSIS
        </span>

        <span>/</span>

        <span>
          AUDIT TRAIL
        </span>

      </nav>

      <div className="system-info">

        <span className="online-dot" />

        <span>
          SYSTEM ONLINE
        </span>

        <span className="header-divider" />

        <div className="model-display">

          <small>
            MODEL
          </small>

          <strong>
            XGBOOST DAY 7 CHAMPION
          </strong>

        </div>

      </div>

    </header>
  );
}