import {
  type FormEvent,
  type KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { ChatApiError, checkApiHealth, sendChatMessage } from "./api/chat";
import type { ChatMessage } from "./types/chat";

const CONVERSATION_KEY = "ai-agent:conversation-id";
const MESSAGES_KEY = "ai-agent:messages";

const suggestions = [
  "继续上次的视频",
  "帮我查找最近观看的内容",
  "搜索知识库中的相关资料",
];

function createMessageId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function readStoredMessages(): ChatMessage[] {
  try {
    const stored = localStorage.getItem(MESSAGES_KEY);
    if (!stored) {
      return [];
    }

    const parsed: unknown = JSON.parse(stored);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter(
      (message): message is ChatMessage =>
        typeof message === "object" &&
        message !== null &&
        "id" in message &&
        typeof message.id === "string" &&
        "role" in message &&
        (message.role === "user" || message.role === "assistant") &&
        "content" in message &&
        typeof message.content === "string",
    );
  } catch {
    return [];
  }
}

function App() {
  const [conversationId, setConversationId] = useState<string | null>(() =>
    localStorage.getItem(CONVERSATION_KEY),
  );
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    localStorage.getItem(CONVERSATION_KEY) ? readStoredMessages() : [],
  );
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    void checkApiHealth().then(setApiOnline);
  }, []);

  useEffect(() => {
    if (conversationId) {
      localStorage.setItem(CONVERSATION_KEY, conversationId);
    } else {
      localStorage.removeItem(CONVERSATION_KEY);
    }
  }, [conversationId]);

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
    } else {
      localStorage.removeItem(MESSAGES_KEY);
    }
  }, [messages]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  function startNewChat() {
    setConversationId(null);
    setMessages([]);
    setError(null);
    setInput("");
    inputRef.current?.focus();
  }

  async function submitMessage(message: string) {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isSending) {
      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: trimmedMessage,
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setError(null);
    setIsSending(true);

    try {
      const result = await sendChatMessage(conversationId, trimmedMessage);
      setConversationId(result.conversation_id);
      setApiOnline(true);
      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          content: result.reply,
        },
      ]);
    } catch (requestError) {
      if (requestError instanceof ChatApiError && requestError.status === 0) {
        setApiOnline(false);
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : "无法完成请求，请稍后重试。",
      );
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitMessage(input);
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submitMessage(input);
    }
  }

  const statusLabel = apiOnline === null ? "检查连接中" : apiOnline ? "服务在线" : "服务离线";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-topline">
          <div className="brand-block">
            <div className="brand-mark" aria-hidden="true">AI</div>
            <div>
              <p className="eyebrow">PERSONAL WORKSPACE</p>
              <h1>视频助手</h1>
            </div>
          </div>
          <span className="version-label">0.1</span>
        </div>

        <button
          className="new-chat-button"
          type="button"
          onClick={startNewChat}
          disabled={isSending}
        >
          <span className="plus-icon" aria-hidden="true">+</span>
          新建对话
        </button>

        <section className="sidebar-section current-session">
          <p className="section-label">当前会话</p>
          <div className="session-row">
            <span className="session-glyph" aria-hidden="true">↗</span>
            <div className="session-copy">
              <strong>{conversationId ? "继续中的对话" : "新对话"}</strong>
              <span>{messages.length ? `${messages.length} 条消息` : "等待你的第一个问题"}</span>
            </div>
            <span className="session-dot" aria-label="当前会话" />
          </div>
        </section>

        <section className="sidebar-section prompt-section">
          <p className="section-label">可以这样问</p>
          <ul className="prompt-list">
            <li>找回最近观看的视频</li>
            <li>从知识库整理一个主题</li>
            <li>继续未完成的学习内容</li>
          </ul>
        </section>

        <div className="sidebar-footer">
          <span className={`status-dot ${apiOnline === false ? "offline" : ""}`} />
          <span>{statusLabel}</span>
          <span className="footer-separator" aria-hidden="true">/</span>
          <span>本地工作区</span>
        </div>
      </aside>

      <main className="chat-panel">
        <header className="chat-header">
          <div>
            <p className="eyebrow dark-eyebrow">AI CONVERSATION</p>
            <h2>和你的助手聊聊</h2>
          </div>
          <div className="header-status">
            <span className={`status-dot ${apiOnline === false ? "offline" : ""}`} />
            {statusLabel}
          </div>
        </header>

        <div className="conversation-area" aria-live="polite">
          {messages.length === 0 ? (
            <section className="welcome-state">
              <div className="welcome-mark" aria-hidden="true">AI</div>
              <p className="eyebrow dark-eyebrow">YOUR ASSISTANT IS READY</p>
              <h3>从一个问题开始</h3>
              <p className="welcome-copy">
                我可以帮你查找观看记录、继续视频，也可以检索知识库中的内容。
              </p>
              <div className="suggestion-grid">
                {suggestions.map((suggestion) => (
                  <button
                    className="suggestion-button"
                    key={suggestion}
                    type="button"
                    onClick={() => void submitMessage(suggestion)}
                  >
                    <span>{suggestion}</span>
                    <span aria-hidden="true">→</span>
                  </button>
                ))}
              </div>
            </section>
          ) : (
            <div className="message-list">
              {messages.map((message) => (
                <article className={`message-row ${message.role}`} key={message.id}>
                  <div className="message-avatar" aria-hidden="true">
                    {message.role === "assistant" ? "AI" : "你"}
                  </div>
                  <div className="message-body">
                    <div className="message-meta">
                      <span>{message.role === "assistant" ? "AI 助手" : "你"}</span>
                    </div>
                    <div className="message-content">{message.content}</div>
                  </div>
                </article>
              ))}
              {isSending && (
                <article className="message-row assistant">
                  <div className="message-avatar" aria-hidden="true">AI</div>
                  <div className="message-body">
                    <div className="message-meta"><span>AI 助手</span></div>
                    <div className="typing-indicator" aria-label="AI 正在回复">
                      <span /><span /><span />
                    </div>
                  </div>
                </article>
              )}
              <div ref={endOfMessagesRef} />
            </div>
          )}
        </div>

        {error && (
          <div className="error-banner" role="alert">
            <span className="error-mark" aria-hidden="true">!</span>
            <span>{error}</span>
            <button type="button" onClick={() => setError(null)} aria-label="关闭错误提示">×</button>
          </div>
        )}

        <div className="composer-wrap">
          <form className="composer" onSubmit={handleSubmit}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleInputKeyDown}
              placeholder="输入你的问题..."
              maxLength={10_000}
              rows={1}
              disabled={isSending}
              aria-label="输入消息"
            />
            <button
              className="send-button"
              type="submit"
              disabled={!input.trim() || isSending}
            >
              <span>{isSending ? "处理中" : "发送"}</span>
              <span className="send-arrow" aria-hidden="true">→</span>
            </button>
          </form>
          <div className="composer-footer">
            <span>内容会保存在当前浏览器</span>
            <span>{input.length.toLocaleString()}/10,000</span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
