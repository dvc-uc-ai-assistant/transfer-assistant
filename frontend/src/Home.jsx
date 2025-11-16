export default function Home() {
  return (
    <div className="page">
      <div style={{ display: "flex", gap: 24, alignItems: "center", flexWrap: "nowrap", minHeight: '60vh' }}>
  <div style={{ flex: "1 1 50%", maxWidth: "50%", minWidth: 0, padding: '0 40px', boxSizing: "border-box" }}>
          <h1 className="nexa-glow" style={{ fontSize: "50px", color: "var(--text-light)", marginTop: 0, textAlign: "center" }}>Find the NEXT transfer courses with NEXA</h1>
          
          <p style={{ marginTop: 8, textAlign: "center" }}>
            Your DVC → UC transfer assistant for <strong style={{ color: "var(--dark-accent)" }}>Computer Science</strong> majors.
          </p>
          <p style={{ textAlign: "center" }}>
            Use the <strong style={{ color: "var(--dark-accent)" }}>Chat</strong> page to ask
            questions, explore requirements, and get tailored guidance for your transfer path.
            We currently support <strong style={{ color: "var(--dark-accent)" }}>UCB, UCD, and UCSD</strong>.
          </p>
        </div>

  <div style={{ flex: "1 1 50%", maxWidth: "50%", minWidth: 0, marginTop: 0, padding: '0 40px', boxSizing: "border-box" }}>
          <div
            style={{
              marginTop: 0,
              padding: 32,
              boxSizing: "border-box",
              borderRadius: 12,
              background: "var(--bg-color)",
              color: "var(--primary-dark)",
              boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            }}
          >
            <h3 style={{ marginTop: 0, textAlign: "center", color: "var(--dark-accent)", fontSize: "35px" }}>Quick Start</h3>

            <div className="button-row" style={{ marginTop: 12 }}>
              <button className="btn round">
                <p>Get usage tips on the <strong>How To Use</strong> tab.</p>
              </button>
              <button className="btn round">
                <p>Real-time assistant on the <strong>Chat</strong> tab.</p>
              </button>
              <button className="btn round">
                <p>Use <strong>Contact</strong> to send us feedback.</p>
              </button>
            </div>
            {/* metrics row (matches screenshot: large colored number + small label) */}
            <div className="metrics-row" style={{ marginTop: 18 }}>
              <div className="metric">
                <div className="metric-value metric-green">40+</div>
                <div className="metric-label">Course Mappings</div>
              </div>
              <div className="metric">
                <div className="metric-value metric-blue">24/7</div>
                <div className="metric-label">Responses</div>
              </div>
              <div className="metric">
                <div className="metric-value metric-pink">3</div>
                <div className="metric-label">UC Campuses</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
