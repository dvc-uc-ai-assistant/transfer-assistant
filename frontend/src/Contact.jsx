export default function Contact() {
  return (
    <div className="page">
      <h1>Contact NEXA</h1>
      <p style={{ marginTop: ".25rem", color: "var(--ink-700)" }}>
        Have a feature request, feedback, or found an issue? We’d love to hear from you.
      </p>

      <div className="kawaii-card" style={{ marginTop: "1rem", maxWidth: 540, marginInline: "auto" }}>
        <p style={{ margin: 0, fontWeight: 600, color: "var(--ink-900)" }}>Email</p>
        <p style={{ margin: ".25rem 0 0" }}>
          <a
            href="mailto:team@nexa.example"
            style={{
              color: "var(--accent)",
              textDecorationThickness: "2px",
              textUnderlineOffset: "3px",
              fontWeight: 600,
            }}
          >
            team@nexa.example
          </a>
        </p>
        <p style={{ marginTop: "1rem", fontSize: "var(--fs-14)", color: "var(--ink-500)" }}>
          We typically reply within 2–3 business days.
        </p>
      </div>
    </div>
  );
}
