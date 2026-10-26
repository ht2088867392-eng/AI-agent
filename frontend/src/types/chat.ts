export type MessageRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
};

export type ChatResponse = {
  conversation_id: string;
  reply: string;
};
