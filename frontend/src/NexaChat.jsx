
import { useEffect, useRef, useState } from "react";

// Suggested prompts list
const suggestedPrompts = [
  "What CS courses should I take at DVC for UC Berkeley?",
  "What Science courses are required for Computer Science at UC Davis?",
  "Show me the required courses for UCSD and UCB.",
  "I've completed Math 192, what does that cover at UCB?",
];

// Typing indicator component with animated dots
function TypingIndicator() {
  const dotStyle = {
    width: "0.5rem",
    height: "0.5rem",
    borderRadius: "50%",
    backgroundColor: "var(--accent-pink)",
    animation: "bounce 1.4s infinite",
    display: "inline-block"
  };

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: "0.25rem",
      padding: "0.5rem 0"
    }}>
      <style>{`
        @keyframes bounce {
          0%, 80%, 100% {
            transform: translateY(0);
            opacity: 0.6;
          }
          40% {
            transform: translateY(-0.5rem);
            opacity: 1;
          }
        }
        .dot-1 { animation-delay: 0s !important; }
        .dot-2 { animation-delay: 0.2s !important; }
        .dot-3 { animation-delay: 0.4s !important; }
      `}</style>
      <div className="dot-1" style={dotStyle} />
      <div className="dot-2" style={dotStyle} />
      <div className="dot-3" style={dotStyle} />
    </div>
  );
}


export default function NexaChat() {
  const [messages, setMessages] = useState([
    // The initial message now contains the prompts
    {
      role: "assistant",
      content: "👋 Hi! I’m NEXA — ask me anything about DVC → UC transfers. Here are some ideas to get started:",
      prompts: suggestedPrompts,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const apiBase = import.meta.env.OPENAI_API_KEY || "";

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Modified to accept an optional promptText
  async function sendMessage(promptText) {
    const text = (typeof promptText === 'string' ? promptText : input).trim();
    if (!text) return;

    // Add the new user message to the chat
    setMessages((prev) => [...prev, { role: "user", content: text }]);

    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${apiBase}/prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text }),
      });

      if (!res.ok) {
        const t = await res.text().catch(() => "");
        throw new Error(t || `HTTP ${res.status}`);
      }
      const data = await res.json();
      const reply = data.response || "Hmm, I didn’t get a response.";
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ I couldn’t reach the server. Check the base URL in .env and try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function checkHealth() {
    try {
      const r = await fetch(`${apiBase}/health`, { method: "GET" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      alert(j.ok ? "✅ Backend reachable." : `⚠️ Backend not ready: ${j.loaded_campuses?.length || 0} campuses loaded`);
    } catch {
      alert("❌ Can’t reach backend. Verify OPENAI_API_KEY in .env.");
    }
  }

  return (
    <div className="chat-card" style={{
      display: "flex",
      flexDirection: "column",
      height: "70vh",
      backgroundColor: "white",
      borderRadius: "16px",
      boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
      overflow: "hidden",
      border: "1px solid #e0e0e0"
    }}>
      <div className="chat-header" style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: 8, 
        flexWrap: "wrap",
        padding: "1.25rem 1.5rem",
        background: "linear-gradient(135deg, var(--accent-pink), var(--dark-accent))",
        color: "white"
      }}>
        <strong style={{ fontSize: "1.1rem" }}>💬 NEXA Chat</strong>
        <span
          style={{
            marginLeft: 8,
            padding: "4px 12px",
            fontSize: 12,
            borderRadius: 999,
            background: "rgba(255,255,255,.2)",
            border: "1px solid rgba(255,255,255,.4)",
            fontWeight: "500"
          }}
          title="Currently supports UC Berkeley, UC Davis, and UC San Diego."
        >
          UCB · UCD · UCSD
        </span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button className="btn" onClick={checkHealth} style={{
            backgroundColor: "rgba(255,255,255,0.2)",
            color: "white",
            border: "1px solid rgba(255,255,255,0.3)",
            borderRadius: "6px",
            padding: "6px 12px",
            fontSize: "12px",
            cursor: "pointer",
            transition: "all 0.2s ease"
          }}>Health</button>
        </div>
      </div>

      <div className="chat-window" style={{
        flex: 1,
        overflowY: "auto",
        padding: "1.5rem",
        backgroundColor: "#fafafa",
        display: "flex",
        flexDirection: "column",
        gap: "0.75rem"
      }}>
        {/* Updated rendering logic for messages */}
        {messages.map((m, i) => (
          <div key={i} style={{
            display: "flex",
            justifyContent: m.role === "user" ? "flex-end" : "flex-start",
            marginBottom: "0.5rem"
          }}>
            <div className={`msg ${m.role === "user" ? "user" : "bot"}`} style={{
              maxWidth: "75%",
              padding: "0.875rem 1rem",
              borderRadius: "12px",
              backgroundColor: m.role === "user" ? "var(--accent-pink)" : "white",
              color: m.role === "user" ? "white" : "var(--primary-dark)",
              boxShadow: m.role === "user" ? "0 2px 8px rgba(224, 114, 164, 0.2)" : "0 2px 8px rgba(0,0,0,0.08)",
              fontSize: "0.95rem",
              lineHeight: "1.5"
            }}>
              {m.content}
              {m.prompts && (
                <div className="suggested-prompts-in-message" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                  {m.prompts.map((prompt, j) => (
                    <button
                      key={j}
                      onClick={() => sendMessage(prompt)}
                      disabled={loading}
                      style={{
                        borderRadius: '8px',
                        padding: '8px 12px',
                        fontSize: '13px',
                        backgroundColor: "var(--primary-green)",
                        color: "var(--primary-dark)",
                        border: "none",
                        cursor: loading ? "not-allowed" : "pointer",
                        transition: "all 0.2s ease",
                        fontWeight: "500",
                        textAlign: "left",
                        opacity: loading ? 0.6 : 1
                      }}
                      onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = "var(--green-shadow)")}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "var(--primary-green)")}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{
            display: "flex",
            justifyContent: "flex-start",
            marginBottom: "0.5rem"
          }}>
            <div style={{
              padding: "0.875rem 1rem",
              borderRadius: "12px",
              backgroundColor: "white",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)"
            }}>
              <TypingIndicator />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <form
        className="input-row"
        onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
        style={{
          display: "flex",
          gap: "0.75rem",
          padding: "1.25rem 1.5rem",
          backgroundColor: "white",
          borderTop: "1px solid #e0e0e0"
        }}
      >
        <input
          className="text-input"
          type="text"
          placeholder="Ask me anything about transfers…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{
            flex: 1,
            padding: "0.75rem 1rem",
            borderRadius: "8px",
            border: "1px solid #d0d0d0",
            fontSize: "0.95rem",
            fontFamily: "inherit",
            transition: "border-color 0.2s ease"
          }}
          onFocus={(e) => e.currentTarget.style.borderColor = "var(--accent-pink)"}
          onBlur={(e) => e.currentTarget.style.borderColor = "#d0d0d0"}
        />
        <button 
          className="btn" 
          type="submit" 
          disabled={loading}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: loading ? "#ccc" : "var(--accent-pink)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: "600",
            transition: "all 0.2s ease",
            opacity: loading ? 0.7 : 1
          }}
          onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = "#d4509f")}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "var(--accent-pink)")}
        >
          {loading ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
