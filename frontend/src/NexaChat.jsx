
import { useEffect, useRef, useState } from "react";
import MarkdownIt from "markdown-it";
import "./Chat.css";

// Initialize markdown-it with table support
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
}).enable(['table']);

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

  // Use explicit environment override or same-origin by default.
  // In Vite dev this works with proxy config; in Cloud Run it hits the same service.
  const apiBase = import.meta.env.VITE_API_BASE_URL || "";

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
      console.log(`[DEBUG] Sending prompt to ${apiBase}/prompt:`, text);
      const res = await fetch(`${apiBase}/prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text }),
      });

      console.log(`[DEBUG] Response status: ${res.status}`);
      if (!res.ok) {
        const t = await res.text().catch(() => "");
        console.error(`[DEBUG] Error response: ${t}`);
        throw new Error(t || `HTTP ${res.status}`);
      }
      const data = await res.json();
      console.log(`[DEBUG] Response data:`, data);
      const reply = data.response || "Hmm, I didn't get a response.";
      console.log(`[DEBUG] Reply content length: ${reply.length}`);
      setMessages((prev) => [...prev, { role: "bot", content: reply }]);
    } catch (err) {
      console.error("[DEBUG] Fetch error:", err);
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
      const text = await r.text();
      alert(text.trim().toUpperCase() === "OK" ? "✅ Backend reachable." : `⚠️ Health check response: ${text}`);
    } catch {
      alert("❌ Can’t reach backend. Verify OPENAI_API_KEY in .env.");
    }
  }

  return (
    <div className="nexa-chat-card">
      <div className="nexa-chat-window">
        {/* Updated rendering logic for messages */}
        {messages.map((m, i) => (
          <div key={i} className={`msg-row ${m.role === 'user' ? 'msg-row-user' : 'msg-row-bot'}`}>
            <div className={`nexa-msg ${m.role === 'user' ? 'user' : 'bot'}`}>
              {m.role === 'bot' ? (
                <div className="markdown-content" dangerouslySetInnerHTML={{ __html: md.render(m.content) }} />
              ) : (
                <div>{m.content}</div>
              )}
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
