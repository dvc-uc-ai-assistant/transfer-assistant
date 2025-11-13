import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import Home from "./Home";
import Chat from "./Chat";
import Contact from "./Contact";
import HowTo from "./HowTo";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <nav className="navbar">
          <div className="navbar-inner">
            <h1 className="nav-title">NEXA</h1>
            <NavLink to="/" end className={({isActive}) => "nav-link" + (isActive ? " active" : "")}>Home</NavLink>
            <NavLink to="/how-to" className={({isActive}) => "nav-link" + (isActive ? " active" : "")}>How&nbsp;to&nbsp;Use</NavLink>
            <NavLink to="/chat" className={({isActive}) => "nav-link" + (isActive ? " active" : "")}>Chat</NavLink>
            <NavLink to="/contact" className={({isActive}) => "nav-link" + (isActive ? " active" : "")}>Contact</NavLink>
            <div className="nav-spacer" />
          </div>
        </nav>

        <main>
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
    </BrowserRouter>
  );
}
