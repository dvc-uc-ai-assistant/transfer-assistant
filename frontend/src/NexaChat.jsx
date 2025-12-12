
import { useEffect, useRef, useState } from "react";
import "./Chat.css";

// Suggested prompts list
const suggestedPrompts = [
  "What CS courses should I take at DVC for UC Berkeley?",
  "What Science courses are required for Computer Science at UC Davis?",
  "Show me the required courses for UCSD and UCB.",
  "I've completed Math 192, what does that cover at UCB?",
];

// Typing indicator component with animated dots
function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <div className="dot dot-1" />
      <div className="dot dot-2" />
      <div className="dot dot-3" />
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
    <div className="nexa-chat-card">
      <div className="nexa-chat-header">
        <strong>💬 NEXA Chat</strong>
        <span className="badge" title="Currently supports UC Berkeley, UC Davis, and UC San Diego.">UCB · UCD · UCSD</span>
        <div className="actions">
          <button className="btn health-btn" onClick={checkHealth}>Health</button>
        </div>
      </div>

      <div className="nexa-chat-window">
        {/* Updated rendering logic for messages */}
        {messages.map((m, i) => (
          <div key={i} className={`msg-row ${m.role === 'user' ? 'msg-row-user' : 'msg-row-bot'}`}>
            <div className={`nexa-msg ${m.role === 'user' ? 'user' : 'bot'}`}>
              {m.content}
              {m.prompts && (
                <div className="suggested-prompts-in-message">
                  {m.prompts.map((prompt, j) => (
                    <button
                      key={j}
                      className="prompt-btn"
                      onClick={() => sendMessage(prompt)}
                      disabled={loading}
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
          <div className="msg-row msg-row-bot" style={{ marginBottom: '0.5rem' }}>
            <div className="nexa-msg bot">
              <TypingIndicator />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <form className="nexa-input-row" onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
        <input
          className="nexa-text-input"
          type="text"
          placeholder="Ask me anything about transfers…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onFocus={(e) => e.currentTarget.classList.add('focus')}
          onBlur={(e) => e.currentTarget.classList.remove('focus')}
        />
        <button
          className="nexa-send-button"
          type="submit"
          disabled={loading}
        >
          {loading ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
