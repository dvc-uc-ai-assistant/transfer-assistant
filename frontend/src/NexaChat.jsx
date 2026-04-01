import { useEffect, useRef, useState } from "react";
import MarkdownIt from "markdown-it";
import "./Chat.css";

// initialize markdown-it with table support
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
}).enable(['table']);

// suggested prompts list
const suggestedPrompts = [
  "What CS courses should I take at DVC for UC Berkeley?",
  "What Science courses are required for Computer Science at UC Davis?",
  "Show me the required courses for UCSD and UCB.",
  "I've completed Math 192, what does that cover at UCB?",
];

// typing indicator component with animated dots
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
    {
      role: "assistant",
      content: "👋 Hi! I'm NEXA — ask me anything about DVC → UC transfers. Here are some ideas to get started:",
      prompts: suggestedPrompts,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const apiBase = import.meta.env.VITE_API_BASE_URL || "";

  const [sessionId, setSessionId] = useState(null);
  const focusTimeRef = useRef(null);
  const [captchaRequired, setCaptchaRequired] = useState(false);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(promptText) {
    const text = (typeof promptText === 'string' ? promptText : input).trim();
    if (!text) return;

    if (captchaRequired) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Too many requests detected. Please wait a moment before trying again." },
      ]);
      return;
    }

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    const timingMs = focusTimeRef.current ? Date.now() - focusTimeRef.current : 0;
    focusTimeRef.current = null;

    try {
      const res = await fetch(`${apiBase}/prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: text,
          session_id: sessionId || undefined,
          timing_ms: timingMs,
          _confirm: "",
        }),
      });

      if (res.status === 429) {
        const data = await res.json().catch(() => ({}));
        if (data.captcha_required) {
          setCaptchaRequired(true);
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "⚠️ Too many requests detected. Please wait a moment before continuing." },
          ]);
          setLoading(false);
          return;
        }
      }

      if (res.status === 403) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "⚠️ Your request was blocked. Please refresh the page and try again." },
        ]);
        setLoading(false);
        return;
      }

      if (!res.ok) {
        const t = await res.text().catch(() => "");
        throw new Error(t || `HTTP ${res.status}`);
      }

      const data = await res.json();

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      const reply = data.response || "Hmm, I didn't get a response.";
      setMessages((prev) => [...prev, { role: "bot", content: reply }]);
    } catch (err) {
      console.error("[DEBUG] Fetch error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ I couldn't reach the server. Check the base URL in .env and try again." },
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
      alert("❌ Can't reach backend. Verify OPENAI_API_KEY in .env.");
    }
  }

  // fetches /download-chat and triggers a full conversation PDF download
  async function downloadChat() {
    if (!sessionId) {
      alert("No conversation to download yet!");
      return;
    }
    try {
      const res = await fetch(`${apiBase}/download-chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "nexa-chat.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("[DEBUG] Download chat error:", err);
      alert("⚠️ Could not download chat. Please try again.");
    }
  }

  return (
    <div className="nexa-chat-card">
      <div className="nexa-chat-window">
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

      {/* download button - only visible once a conversation has started */}
      {sessionId && (
        <div className="nexa-download-row">
          <button
            className="nexa-download-button"
            onClick={downloadChat}
            disabled={loading}
          >
            ⬇ Download Chat
          </button>
        </div>
      )}

      <form className="nexa-input-row" onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
        {/* Honeypot hidden field - real users never see or fill this, bots often do */}
        <input
          type="text"
          name="_confirm"
          style={{ display: "none" }}
          tabIndex="-1"
          autoComplete="off"
          readOnly
          value=""
        />
        <input
          className="nexa-text-input"
          type="text"
          placeholder="Ask me anything about transfers…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onFocus={(e) => {
            e.currentTarget.classList.add('focus');
            focusTimeRef.current = Date.now();
          }}
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