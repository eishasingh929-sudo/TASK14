import { FormEvent, useState } from "react";
import { useChat } from "../hooks/useChat";
import { useVoice } from "../hooks/useVoice";
import { voiceQuery } from "../services/uniguru-api";
import { MessageBubble } from "./MessageBubble";
import { VoiceInput } from "./VoiceInput";

export function ChatWidget() {
  const [input, setInput] = useState("");
  const { messages, isLoading, sendMessage, setMessages } = useChat();
  const { isRecording, startRecording, stopRecording } = useVoice();

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text) {
      return;
    }
    setInput("");
    await sendMessage(text);
  }

  async function onVoiceToggle() {
    if (!isRecording) {
      await startRecording();
      return;
    }
    const blob = await stopRecording();
    try {
      const response = await voiceQuery(blob);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer || "", payload: response }
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Voice request failed. Please retry." }
      ]);
    }
  }

  return (
    <section className="chat-card">
      <div className="messages">
        {messages.map((message, idx) => (
          <MessageBubble
            key={`${message.role}-${idx}`}
            role={message.role}
            content={message.content}
            payload={message.payload}
          />
        ))}
        {isLoading && <div className="bubble assistant">Loading...</div>}
      </div>

      <form className="row" onSubmit={onSubmit}>
        <input
          placeholder="Ask UniGuru..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
        />
        <button type="submit">Send</button>
        <VoiceInput isRecording={isRecording} onToggle={onVoiceToggle} />
      </form>
    </section>
  );
}
