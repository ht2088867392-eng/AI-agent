import type { ChatResponse } from "../types/chat";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ChatApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ChatApiError";
    this.status = status;
  }
}

async function parseResponse(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

export async function sendChatMessage(
  conversationId: string | null,
  message: string,
): Promise<ChatResponse> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/api/v1/chat/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message,
      }),
    });
  } catch {
    throw new ChatApiError("无法连接到聊天服务，请确认后端已经启动。", 0);
  }

  const body = await parseResponse(response);
  if (!response.ok) {
    const detail =
      typeof body === "object" && body !== null && "detail" in body
        ? String(body.detail)
        : "聊天请求失败，请稍后重试。";
    throw new ChatApiError(detail, response.status);
  }

  if (
    typeof body !== "object" ||
    body === null ||
    !("conversation_id" in body) ||
    !("reply" in body)
  ) {
    throw new ChatApiError("聊天服务返回了无效数据。", response.status);
  }

  return body as ChatResponse;
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      method: "GET",
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  }
}
