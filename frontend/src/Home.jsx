import { NavLink } from "react-router-dom";

export default function Home() {
  return (
    <div className="page">
      <h1>Welcome to NEXA</h1>
      <p style={{ marginTop: ".25rem", color: "var(--ink-700)" }}>
        Your DVC → UC transfer assistant. Use the <strong>Chat</strong> page to ask questions,
        explore requirements, and get tailored guidance. We currently support UCB, UCD, and UCSD.
      </p>

      <div className="kawaii-card" style={{ marginTop: "1rem" }}>
        <h2 style={{ marginTop: 0 }}>Quick Start</h2>
        <ul style={{ lineHeight: 1.8, margin: 0, paddingLeft: "1.1rem" }}>
          <li>Go to the <strong>Chat</strong> tab and ask about articulation, ASSIST, or campus requirements.</li>
          <li>We’ll soon add a <strong>Campus Explorer</strong> tab with filters and data visualizations.</li>
          <li>Use <strong>Contact</strong> to send us feedback.</li>
        </ul>

        <div style={{ marginTop: "1rem", display: "flex", gap: ".6rem", flexWrap: "wrap" }}>
          <NavLink to="/chat" className="btn">Start Chatting</NavLink>
          <NavLink to="/how-to" className="btn secondary">How to Use</NavLink>
        </div>
      </div>
    </div>
  );
}
