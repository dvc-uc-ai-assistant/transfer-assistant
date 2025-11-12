export default function HowTo() {
  return (
    <div className="page">
      <h1>How to Use NEXA</h1>

      <div className="kawaii-card" style={{ marginTop: "1rem" }}>
        <strong>Supported campuses:</strong> UC Berkeley (UCB), UC Davis (UCD), and UC San Diego (UCSD).
      </div>

      <ol
        style={{
          lineHeight: 1.8, marginTop: "1rem", background: "var(--surface)",
          border: "1px solid var(--border)", borderRadius: "var(--r-xl)",
          padding: "1rem 1.25rem", boxShadow: "var(--sh-sm)", listStylePosition: "inside"
        }}
      >
        <li>Go to the <strong>Chat</strong> tab.</li>
        <li>Ask questions about transfer prep, articulation, ASSIST, or campus requirements.</li>
        <li>Mention a campus for focused guidance. Example: <em>“What math do I need for CS at UCSD?”</em></li>
        <li>Include any <em>completed courses</em> (e.g., “I finished Calc I and English Comp”).</li>
        <li>Refine with <em>“required only”</em>, <em>“major prep only”</em>, or <em>“show remaining courses.”</em></li>
      </ol>

      <h2 style={{ marginTop: "1rem" }}>Good Examples:</h2>
      <ul className="kawaii-card" style={{ lineHeight: 1.8, marginTop: ".6rem" }}>
        <li>“For <strong>UCB EECS</strong>, what lower-division courses remain if I’ve done Calc I &amp; II?”</li>
        <li>“Compare <strong>UCD vs UCSD</strong> for ME — focus on <em>required major prep only</em>.”</li>
        <li>“I’ve completed English Comp and Physics 1. What’s next for <strong>UCSD CSE</strong>?”</li>
      </ul>

      <p style={{ marginTop: "1rem", color: "var(--ink-700)" }}>
        Tip: Keep each question focused. If you need another angle (another campus, GE vs. major prep),
        ask a fresh question.
      </p>
    </div>
  );
}
