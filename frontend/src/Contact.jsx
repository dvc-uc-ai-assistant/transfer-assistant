export default function Contact() {
  return (
    <div className="page">
      <h1 style={{ color: "var(--primary-dark)", marginTop: 0 }}>Contact NEXA</h1>

      <p>Have feature requests, feedback, or found an issue? Reach out and we’ll take a look.</p>

      <div
        style={{
          marginTop: 16,
          padding: 16,
          border: "1px solid #d9d7cf",
          borderRadius: 12,
          background: "#fff",
        }}
      >
        <p style={{ margin: 0 }}>
          Email:{" "}
          <a href="mailto:team@nexa.example" style={{ color: "var(--primary-green)" }}>
            team@nexa.example
          </a>
        </p>
      </div>
    </div>
  );
}
