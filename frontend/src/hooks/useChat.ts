import { useState } from "react";
import { ask } from "../services/uniguru-api";
import { UniGuruResponse } from "../types/uniguru";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  payload?: UniGuruResponse;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  async function sendMessage(text: string) {
    if (!text.trim()) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);
    try {
      const response = await ask(text);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer || "", payload: response }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Request failed. Please try again." }
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return { messages, isLoading, sendMessage, setMessages };
}
