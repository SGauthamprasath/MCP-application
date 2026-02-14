import { useState } from "react";
import { sendMessage } from "../api";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

export default function chatpage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (text) => {
    if (!text) return;

    const userMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);

    try {
      setLoading(true);
      const response = await sendMessage(text);

      const botMessage = {
        role: "assistant",
        content: response.reply,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Error connecting to server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>AI Data Console</h1>
      <chatwindow messages={messages} loading={loading} />
      <chatinput onSend={handleSend} />
    </div>
  );
}