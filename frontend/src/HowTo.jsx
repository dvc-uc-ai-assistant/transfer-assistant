export default function HowTo() {
  return (
    <div className="page">
      <h1 style={{ fontSize: "2.2rem", background: "linear-gradient(90deg, var(--primary-pink), var(--dark-accent))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text", marginTop: 0, marginBottom: 8 }}>How to Use NEXA</h1>
      <p style={{ color: "#666", fontSize: "1rem", marginTop: 0, opacity: 0.9 }}>Learn how to get the most out of your transfer assistant</p>

      {/* Campus Badge Cards */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2.5rem", flexWrap: "wrap", justifyContent: "center", marginTop: "1.5rem" }}>
        {[
          { name: "UC Berkeley", color: "var(--dark-accent)", code: "UCB" },
          { name: "UC Davis", color: "var(--teal-accent)", code: "UCD" },
          { name: "UC San Diego", color: "var(--primary-pink)", code: "UCSD" }
        ].map((campus, idx) => (
          <div key={idx} style={{ 
            backgroundColor: campus.color, 
            color: "white", 
            padding: "0.75rem 1.5rem", 
            borderRadius: "20px", 
            fontSize: "0.95rem",
            fontWeight: "600",
            boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
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
          { num: 1, title: "Ask Specific Questions", desc: "Be specific with campus names and course codes. Example: 'What's the equivalent of CS 61B from UCB at UCSD?'" },
          { num: 2, title: "Explore Requirements", desc: "Ask about major requirements, prerequisites, and transfer policies for your desired UC campus." },
          { num: 3, title: "Check Course Mappings", desc: "Get detailed information about equivalent courses, units, and course descriptions." },
          { num: 4, title: "Verify Information", desc: "Cross-check results on ASSIST.org for the most up-to-date official information." },
          { num: 5, title: "Plan Your Path", desc: "Use the information to create your personalized transfer academic plan." },
          { num: 6, title: "Get Feedback", desc: "Use the Contact page to share feedback or suggest improvements to NEXA." }
        ].map((step, idx) => (
          <div key={idx} style={{
            backgroundColor: "white",
            border: "1px solid #e8e8f0",
            borderRadius: "10px",
            padding: "1.5rem",
            transition: "all 0.3s ease",
            cursor: "default",
            boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
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
                background: idx % 2 === 0 ? "linear-gradient(135deg, var(--accent-pink), var(--dark-accent))" : "linear-gradient(135deg, var(--teal-accent), var(--primary-pink))",
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
        background: "linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%)", 
        border: "3px solid var(--teal-accent)", 
        borderRadius: "12px", 
        padding: "1.5rem", 
        marginBottom: "2rem",
        boxShadow: "inset 0 2px 8px rgba(6, 182, 212, 0.05), 0 4px 12px rgba(0,0,0,0.05)"
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
              borderLeft: "4px solid var(--teal-accent)",
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
        background: "linear-gradient(135deg, var(--teal-accent), var(--primary-pink))",
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
