export default function HowTo() {
  return (
    <div className="page">
      <h1 style={{ color: "var(--primary-dark)", marginTop: 0 }}>How to Use NEXA</h1>

      <div
        style={{
          marginTop: 12,
          padding: 12,
          border: "1px solid #d9d7cf",
          borderRadius: 10,
          background: "#fff8ef",
        }}
      >
        <strong>Supported campuses (for now):</strong> UC Berkeley (UCB), UC Davis (UCD), and UC San Diego (UCSD).
      </div>

      <ol style={{ lineHeight: 1.7, marginTop: 16 }}>
        <li>Go to the <strong>Chat</strong> tab.</li>
        <li>Ask questions about transfer prep, articulation, ASSIST, or campus requirements.</li>
        <li>
          Mention a campus to get focused guidance. Example:&nbsp;
          <em>“What math do I need for CS at UCSD?”</em>
        </li>
        <li>
          Include any <em>completed courses</em> or areas you’ve finished (e.g., “I finished Calc I and English Comp”).
        </li>
        <li>
          Refine your query with constraints like <em>“required only”</em>, <em>“focus on major prep”</em>,
          or <em>“show remaining courses.”</em>
        </li>
      </ol>

      <h3 style={{ marginTop: 20 }}>Good Prompt Examples</h3>
      <ul style={{ lineHeight: 1.7 }}>
        <li>
          “For <strong>UCB</strong> EECS, what lower-division courses do I still need if I’ve done Calc I &amp; II?”
        </li>
        <li>
          “Compare <strong>UCD vs UCSD</strong> for ME — focus on <em>required major prep only</em>.”
        </li>
        <li>
          “I’ve completed English Comp and Physics 1. What’s next for <strong>UCSD CSE</strong>?”
        </li>
      </ul>

      <p style={{ marginTop: 16, opacity: 0.85 }}>
        Tip: Keep each question focused. If you need a new angle (another campus, or GE vs. major prep),
        ask a fresh question.
      </p>
    </div>
  );
}
