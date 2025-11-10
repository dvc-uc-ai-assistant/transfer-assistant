import { useEffect, useRef, useState } from "react";

export default function NexaChat() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "👋 Hi! I’m NEXA — ask me anything about DVC → UC transfers." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const apiBase = import.meta.env.VITE_API_BASE || "";

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;

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
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role === "user" ? "user" : "bot"}`}>{m.content}</div>
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
          placeholder="Type your question… (UCB/UCD/UCSD supported)"
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
