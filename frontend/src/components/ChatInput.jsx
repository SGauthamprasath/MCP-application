import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend(text);
    setText("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        placeholder="Ask something..."
        onChange={(e) => setText(e.target.value)}
        style={{ width: "80%", padding: "10px" }}
      />
      <button type="submit">Send</button>
    </form>
  );
}