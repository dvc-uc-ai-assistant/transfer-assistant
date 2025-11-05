export default function Home() {
  return (
    <div className="page">
      <h1 style={{ color: "var(--primary-dark)", marginTop: 0 }}>Welcome to NEXA</h1>

      <p>
        This is your DVC → UC transfer assistant. Use the <strong>Chat</strong> page to ask
        questions, explore requirements, and get tailored guidance for your transfer path.
        We currently support <strong>UCB, UCD, and UCSD</strong>.
      </p>

      <div
        style={{
          marginTop: 16,
          padding: 16,
          border: "1px solid #d9d7cf",
          borderRadius: 12,
          background: "#fff",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Quick Start</h3>
        <ul>
          <li>Go to the <strong>Chat</strong> tab and ask about articulation, ASSIST, or campus requirements.</li>
          <li>We’ll soon add a <strong>Campus Explorer</strong> tab with filters and data visualizations.</li>
          <li>Use <strong>Contact</strong> to send us feedback.</li>
        </ul>
      </div>
    </div>
  );
}
