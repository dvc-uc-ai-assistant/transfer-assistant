import { BrowserRouter, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import Home from "./Home";
import Chat from "./Chat";
import Contact from "./Contact";
import HowTo from "./HowTo";

const CHAT_STORAGE_KEY = "nexa_chat_state_v1";

function AppShell() {
  const [navOpen, setNavOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    if (location.pathname !== "/chat") {
      sessionStorage.removeItem(CHAT_STORAGE_KEY);
    }
  }, [location.pathname]);

  return (
    <div className="app-shell">
        <nav className={"navbar" + (navOpen ? " open" : "") } aria-hidden={!navOpen && window.innerWidth <= 900}>
          <div className="navbar-inner">
            <div className="nav-header">
              <img src="/nexa-logo.png" alt="NEXA" className="nav-logo" />
              <h1 className="nav-title">NEXA</h1>
            </div>
            <NavLink to="/" end className={({isActive}) => "nav-link" + (isActive ? " active" : "")} onClick={() => setNavOpen(false)}>Home</NavLink>
            <NavLink to="/how-to" className={({isActive}) => "nav-link" + (isActive ? " active" : "")} onClick={() => setNavOpen(false)}>How&nbsp;to&nbsp;Use</NavLink>
            <NavLink to="/chat" className={({isActive}) => "nav-link" + (isActive ? " active" : "")} onClick={() => setNavOpen(false)}>Chat</NavLink>
            <NavLink to="/contact" className={({isActive}) => "nav-link" + (isActive ? " active" : "")} onClick={() => setNavOpen(false)}>Contact</NavLink>
            <div className="nav-spacer" />
          </div>
        </nav>

        {/* Mobile nav toggle button */}
        <button
          className="mobile-nav-toggle"
          aria-label={navOpen ? "Close navigation" : "Open navigation"}
          aria-expanded={navOpen}
          onClick={() => setNavOpen((v) => !v)}
        >
          <span className="hamburger" aria-hidden="true" />
        </button>

        <main onClick={() => navOpen && setNavOpen(false)}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/how-to" element={<HowTo />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </main>

        <footer style={{ textAlign: "center", padding: "1rem", opacity: .7 }}>
          © {new Date().getFullYear()} NEXA
        </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
