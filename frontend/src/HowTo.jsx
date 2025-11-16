export default function HowTo() {
  return (
    <div className="page">
      <h1 style={{ fontSize: "2.2rem", background: "linear-gradient(90deg, var(--accent-pink), var(--dark-accent))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", marginTop: 0, marginBottom: 8 }}>How to Use NEXA</h1>
      <p style={{ color: "var(--dark-accent)", fontSize: "1rem", marginTop: 0, opacity: 0.9 }}>Master the art of asking for transfer course guidance</p>

      {/* Campus Badge Cards */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2.5rem", flexWrap: "wrap", justifyContent: "center", marginTop: "1.5rem" }}>
        {[
          { name: "UC Berkeley", color: "var(--accent-pink)", code: "UCB" },
          { name: "UC Davis", color: "var(--dark-accent)", code: "UCD" },
          { name: "UC San Diego", color: "var(--light-accent)", code: "UCSD" }
        ].map((campus, idx) => (
          <div key={idx} style={{ 
            backgroundColor: campus.color, 
            color: "white", 
            padding: "0.75rem 1.5rem", 
            borderRadius: "20px", 
            fontSize: "0.95rem",
            fontWeight: "600",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            transition: "transform 0.2s ease",
            cursor: "default"
          }}>
            {campus.code} — {campus.name}
          </div>
        ))}
      </div>

      {/* Step Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", marginBottom: "2.5rem" }}>
        {[
          { num: 1, title: "Select Your Campuses", desc: "Choose your origin and destination universities. You can transfer between UC Berkeley, UC Davis, UC San Diego, and more." },
          { num: 2, title: "Ask Questions", desc: "Request specific information about equivalencies. NEXA's AI will help guide you through the transfer process." },
          { num: 3, title: "Specify Categories", desc: "Tell NEXA the specific category that you would like to target. Ex: \"Show me the UCD Mathematics Requirements\""},
          { num: 4, title: "Review Results", desc: "NEXA will show you equivalent courses at your destination campus with detailed information." },
          { num: 5, title: "Verify Details", desc: "If in doubt, review units, prerequisites, course descriptions, and other important information on ASSIST.org." },
          { num: 6, title: "Plan Ahead", desc: "Use the transfer information to plan your academic path and ensure a smooth transition." }
        ].map((step, idx) => (
          <div key={idx} style={{
            backgroundColor: "white",
            border: "1px solid #e0e0e0",
            borderRadius: "12px",
            padding: "1.5rem",
            transition: "all 0.3s ease",
            cursor: "default",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-4px)";
            e.currentTarget.style.boxShadow = "0 8px 16px rgba(0,0,0,0.12)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.08)";
          }}>
            <div style={{ display: "flex", alignItems: "center", marginBottom: "1rem" }}>
              <div style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--accent-pink), var(--dark-accent))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontWeight: "bold",
                fontSize: "1.1rem",
                marginRight: "1rem"
              }}>
                {step.num}
              </div>
              <h3 style={{ margin: 0, color: "var(--primary-dark)", fontSize: "1rem" }}>{step.title}</h3>
            </div>
            <p style={{ margin: 0, color: "#666", fontSize: "0.95rem", lineHeight: "1.6" }}>{step.desc}</p>
          </div>
        ))}
      </div>

      {/* Example Prompts */}
      <div style={{ 
        background: "linear-gradient(135deg, rgba(176, 226, 152, 0.25) 0%, rgba(176, 226, 152, 0.1) 100%)", 
        border: "3px solid var(--accent-pink)", 
        borderRadius: "12px", 
        padding: "1.5rem", 
        marginBottom: "2rem",
        boxShadow: "inset 0 2px 8px rgba(176, 226, 152, 0.1), 0 4px 12px rgba(0,0,0,0.05)"
      }}>
        <h3 style={{ color: "var(--primary-dark)", marginTop: 0, marginBottom: "1rem" }}>📝 Example Prompts</h3>
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {[
            "What are the equivalent courses at UCSD for Computer Science 61B from UC Berkeley?",
            "How many units does a 4-unit course transfer as between UC Davis and UC San Diego?",
            "What are the prerequisites for the equivalent course at my destination campus?"
          ].map((prompt, idx) => (
            <div key={idx} style={{
              background: "linear-gradient(90deg, rgba(255,255,255, 0.8) 0%, rgba(255,255,255, 0.95) 100%)",
              borderLeft: "4px solid var(--accent-pink)",
              padding: "0.75rem 1rem",
              borderRadius: "4px",
              color: "var(--primary-dark)",
              fontSize: "0.95rem",
              fontStyle: "italic",
              boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
              transition: "all 0.2s ease"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)";
              e.currentTarget.style.transform = "translateX(4px)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = "0 2px 4px rgba(0,0,0,0.05)";
              e.currentTarget.style.transform = "translateX(0)";
            }}>
              "{prompt}"
            </div>
          ))}
        </div>
      </div>

      <div style={{
        background: "var(--light-accent)",
        borderRadius: "12px",
        padding: "1.5rem",
        marginTop: "2rem",
        boxShadow: "0 8px 24px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.2)",
        border: "1px solid rgba(255,255,255,0.2)",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{
          position: "absolute",
          top: "-40px",
          right: "-40px",
          width: "120px",
          height: "120px",
          background: "radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)",
          borderRadius: "50%"
        }} />
        <p style={{
          margin: 0,
          fontSize: "1rem",
          lineHeight: "1.7",
          color: "white",
          fontWeight: "500",
          position: "relative",
          zIndex: 1
        }}>
          <span style={{ fontSize: "1.3rem", marginRight: "0.5rem" }}>💡</span>
          <strong>Pro Tip:</strong> Keep each question focused and specific with campus names and course codes. If you need a different angle, ask a fresh question!
        </p>
      </div>
    </div>
  );
}
