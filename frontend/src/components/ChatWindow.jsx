import MessageBubble from "./MessageBubble";
export default function ChatWindow({ messages, loading }) {
  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <MessageBubble key={index} message={msg} />
      ))}

      {loading && <p>Thinking...</p>}
    </div>
  );
}