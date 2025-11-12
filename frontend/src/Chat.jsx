import SkyrelisChat from "./SkyrelisChat";

export default function Chat() {
  return (
    <div
      className="page"
      style={{
        background: "linear-gradient(135deg, var(--accent-mint), var(--accent-lav))",
        boxShadow: "var(--shadow-sm)",
        border: "1px solid var(--border)",
        borderRadius: "var(--r-xl)",
        padding: "1.5rem 1.75rem",
        maxWidth: "1000px",
        margin: "0 auto",
      }}
    >
      <h1
        style={{
          color: "var(--accent-pink)",
          marginTop: 0,
          textAlign: "center",
          fontFamily: "'Poppins', system-ui, sans-serif",
          fontWeight: 700,
        }}
      >
        💬 NEXA Chat
      </h1>

      <p
        style={{
          textAlign: "center",
          marginBottom: "1.25rem",
          opacity: 0.85,
          fontSize: ".95rem",
        }}
      >
        Ask questions about <strong>DVC → UC transfers</strong>  
        (currently supports <strong>UCB, UCD, and UCSD</strong>).
      </p>

      <div
        style={{
          background: "var(--container-bg)",
          borderRadius: "var(--r-xl)",
          padding: "1rem",
          boxShadow: "var(--shadow-md)",
        }}
      >
        <SkyrelisChat />
      </div>
    </div>
  );
}
