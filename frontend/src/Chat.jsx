import NexaChat from "./NexaChat";
import { useLocation } from "react-router-dom";

export default function Chat() {
  const location = useLocation();

  return (
    <div className="chat-page">
      <NexaChat key={location.key} />
    </div>
  );
}
