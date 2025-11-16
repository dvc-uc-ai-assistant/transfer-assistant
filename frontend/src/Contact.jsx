export default function Contact() {
  return (
    <div className="page">
      <h1 style={{ 
        fontSize: "2.2rem", 
        background: "linear-gradient(90deg, var(--accent-pink), var(--dark-accent))", 
        WebkitBackgroundClip: "text", 
        WebkitTextFillColor: "transparent", 
        backgroundClip: "text", 
        marginTop: 0, 
        marginBottom: 8 
      }}>Get in Touch</h1>
      <p style={{ fontSize: "1rem", color: "#666", marginTop: 0, opacity: 0.9 }}>Have feature requests, feedback, or found an issue? We'd love to hear from you!</p>

      {/* Contact Cards Grid */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", 
        gap: "1.5rem", 
        marginTop: "2.5rem",
        marginBottom: "2.5rem"
      }}>
        {/* Email Card */}
        <div style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "1.75rem",
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
          border: "1px solid #e0e0e0",
          transition: "all 0.3s ease",
          cursor: "default"
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-4px)";
          e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.12)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
        }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>✉️</div>
          <h3 style={{ color: "var(--primary-dark)", margin: "0 0 0.75rem 0", fontSize: "1.1rem" }}>Email Us</h3>
          <p style={{ color: "#666", margin: "0 0 1rem 0", fontSize: "0.95rem" }}>Have questions or feedback?</p>
          <a href="mailto:team@nexa.example" style={{ 
            color: "white", 
            backgroundColor: "var(--accent-pink)",
            padding: "0.5rem 1rem",
            borderRadius: "6px",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "0.9rem",
            display: "inline-block",
            transition: "all 0.2s ease"
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#d4509f"}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "var(--accent-pink)"}
          >
            team@nexa.example
          </a>
        </div>

        {/* Feature Request Card */}
        <div style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "1.75rem",
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
          border: "1px solid #e0e0e0",
          transition: "all 0.3s ease",
          cursor: "default"
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-4px)";
          e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.12)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
        }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>💡</div>
          <h3 style={{ color: "var(--primary-dark)", margin: "0 0 0.75rem 0", fontSize: "1.1rem" }}>Feature Ideas</h3>
          <p style={{ color: "#666", margin: "0 0 1rem 0", fontSize: "0.95rem" }}>Have a suggestion for NEXA?</p>
          <a href="mailto:team@nexa.example?subject=Feature Request" style={{ 
            color: "white", 
            backgroundColor: "var(--primary-green)",
            padding: "0.5rem 1rem",
            borderRadius: "6px",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "0.9rem",
            display: "inline-block",
            transition: "all 0.2s ease"
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--green-shadow)"}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "var(--primary-green)"}
          >
            Send Request
          </a>
        </div>

        {/* Report Issue Card */}
        <div style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "1.75rem",
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
          border: "1px solid #e0e0e0",
          transition: "all 0.3s ease",
          cursor: "default"
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-4px)";
          e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.12)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
        }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>🐛</div>
          <h3 style={{ color: "var(--primary-dark)", margin: "0 0 0.75rem 0", fontSize: "1.1rem" }}>Report a Bug</h3>
          <p style={{ color: "#666", margin: "0 0 1rem 0", fontSize: "0.95rem" }}>Found something broken?</p>
          <a href="mailto:team@nexa.example?subject=Bug Report" style={{ 
            color: "white", 
            backgroundColor: "var(--light-accent)",
            padding: "0.5rem 1rem",
            borderRadius: "6px",
            textDecoration: "none",
            fontWeight: "600",
            fontSize: "0.9rem",
            display: "inline-block",
            transition: "all 0.2s ease"
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#5a78b5"}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "var(--light-accent)"}
          >
            Report Bug
          </a>
        </div>
      </div>

      {/* Bottom Message */}
      <div style={{
        background: "var(--light-accent)",
        borderRadius: "12px",
        padding: "1.5rem",
        textAlign: "center",
        border: "1px solid rgba(0,0,0,0.05)"
      }}>
        <p style={{ 
          margin: 0, 
          fontSize: "0.95rem", 
          color: "var(--text-light)",
          lineHeight: "1.6"
        }}>
          We appreciate your feedback and continuously work to improve NEXA. Your input helps us serve students better! 🎓
        </p>
      </div>
    </div>
  );
}
