
import { useEffect, useRef, useState } from "react";

// Suggested prompts list
const suggestedPrompts = [
  "What CS courses should I take at DVC for UC Berkeley?",
  "What Science courses are required for Computer Science at UC Davis?",
  "Show me the required courses for UCSD and UCB.",
  "I've completed Math 192, what does that cover at UCB?",
];

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

  const apiBase = import.meta.env.VITE_API_BASE || "";

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
      alert("❌ Can’t reach backend. Verify VITE_API_BASE in .env.");
    }
  }

  return (
    <div className="chat-card">
      <div className="chat-header" style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <strong>NEXA Chatbot</strong>
        <span
          style={{
            marginLeft: 8,
            padding: "2px 8px",
            fontSize: 12,
            borderRadius: 999,
            background: "rgba(255,255,255,.18)",
            border: "1px solid rgba(255,255,255,.35)"
          }}
          title="Currently supports UC Berkeley, UC Davis, and UC San Diego."
        >
          UCB · UCD · UCSD only
        </span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button className="btn" onClick={checkHealth}>Health</button>
        </div>
      </div>

      <div className="chat-window">
        {/* Updated rendering logic for messages */}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role === "user" ? "user" : "bot"}`}>
            {m.content}
            {/* Render buttons if the message has prompts */}
            {m.prompts && (
              <div className="suggested-prompts-in-message" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                {m.prompts.map((prompt, j) => (
                  <button
                    key={j}
                    className="btn secondary" // Use the theme's .btn.secondary (orange)
                    onClick={() => sendMessage(prompt)}
                    disabled={loading}
                    // Add "round" style and override padding for a better look
                    style={{
                      borderRadius: '999px', // Makes the button pill-shaped
                      padding: '6px 14px',
                      fontSize: '13px'
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <form
        className="input-row"
        onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
      >
        <input
          className="text-input"
          type="text"
          placeholder="Type your question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="btn" type="submit" disabled={loading}>
          {loading ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
