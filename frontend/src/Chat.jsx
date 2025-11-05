import SkyrelisChat from "./SkyrelisChat";

export default function Chat() {
  return (
    <div className="page" style={{ background: "transparent", boxShadow: "none", paddingTop: 0 }}>
      <h1 style={{ color: "var(--primary-dark)", marginTop: 0 }}>NEXA Chat</h1>
      <SkyrelisChat />
    </div>
  );
}
