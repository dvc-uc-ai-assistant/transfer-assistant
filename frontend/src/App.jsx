import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import Home from "./Home";
import Chat from "./Chat";
import Contact from "./Contact";
import HowTo from "./HowTo";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        {/* 🌈 Navbar */}
        <nav className="navbar">
          <div className="navbar-inner">
            <h1 className="nav-title" style={{ position: "relative" }}>
              NEXA
              <span
                style={{
                  position: "absolute",
                  right: "-12px",
                  top: "-8px",
                  fontSize: "0.85rem",
                  animation: "sparkle 1.8s infinite ease-in-out",
                }}
              >
                ✨
              </span>
            </h1>

            <div className="nav-spacer" />

            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                "nav-link" + (isActive ? " active" : "")
              }
            >
              Home
            </NavLink>

            <NavLink
              to="/how-to"
              className={({ isActive }) =>
                "nav-link" + (isActive ? " active" : "")
              }
            >
              How&nbsp;to&nbsp;Use
            </NavLink>

            <NavLink
              to="/chat"
              className={({ isActive }) =>
                "nav-link" + (isActive ? " active" : "")
              }
            >
              Chat
            </NavLink>

            <NavLink
              to="/contact"
              className={({ isActive }) =>
                "nav-link" + (isActive ? " active" : "")
              }
            >
              Contact
            </NavLink>
          </div>
        </nav>

        {/* 🪄 Routes */}
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/how-to" element={<HowTo />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </main>

        {/* 🍰 Footer */}
        <footer
          style={{
            textAlign: "center",
            padding: "1.2rem",
            fontWeight: 600,
            color: "var(--ink-500)",
            background: "linear-gradient(180deg, #ffffffb8, #fff5fd)",
            borderTop: "1px solid var(--border)",
            backdropFilter: "blur(6px)",
          }}
        >
          © {new Date().getFullYear()} NEXA · crafted with ☁️ &amp; 💖
        </footer>
      </div>
    </BrowserRouter>
  );
}

/* Add this little animation either here or in theme.css */
const sparkleKeyframes = `
@keyframes sparkle {
  0%, 100% { opacity: 0; transform: scale(0.8) rotate(0deg); }
  50% { opacity: 1; transform: scale(1.1) rotate(20deg); }
}
`;

// inject sparkle animation dynamically (optional but neat)
if (typeof document !== "undefined" && !document.getElementById("sparkle-style")) {
  const style = document.createElement("style");
  style.id = "sparkle-style";
  style.innerHTML = sparkleKeyframes;
  document.head.appendChild(style);
}
