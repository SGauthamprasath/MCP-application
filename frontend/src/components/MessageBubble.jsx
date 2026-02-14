export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        textAlign: isUser ? "right" : "left",
        margin: "10px",
      }}
    >
      <span
        style={{
          background: isUser ? "#4CAF50" : "#e0e0e0",
          color: isUser ? "white" : "black",
          padding: "10px",
          borderRadius: "10px",
          display: "inline-block",
        }}
      >
        {message.content}
      </span>
    </div>
  );
}