const API_URL =
  "http://127.0.0.1:8000"
  + "/api/v1/video-records/progress";


// MVP 阶段暂时写在这里。
// 必须与后端 .env 中配置的 Token 一致。
const EXTENSION_TOKEN =
  "xkkZg9r_08X8amE8LvHWoQGzZPa54ylVrWUS4esDWds";


const REQUEST_TIMEOUT_MS = 10_000;


function isAllowedSender(sender) {
  if (sender.id !== chrome.runtime.id) {
    return false;
  }

  if (!sender.url) {
    return false;
  }

  try {
    const url = new URL(sender.url);

    return (
      url.protocol === "https:"
      && url.hostname ===
        "www.bilibili.com"
      && url.pathname.startsWith(
        "/video/"
      )
    );
  } catch {
    return false;
  }
}


function isNonEmptyString(
  value,
  maxLength
) {
  return (
    typeof value === "string"
    && value.trim().length > 0
    && value.length <= maxLength
  );
}


function isValidBilibiliUrl(value) {
  if (typeof value !== "string") {
    return false;
  }

  try {
    const url = new URL(value);

    return (
      url.protocol === "https:"
      && url.hostname ===
        "www.bilibili.com"
      && url.pathname.startsWith(
        "/video/"
      )
    );
  } catch {
    return false;
  }
}


function isValidReportedAt(value) {
  if (value === null || value === undefined) {
    return true;
  }

  if (typeof value !== "string") {
    return false;
  }

  return !Number.isNaN(
    Date.parse(value)
  );
}


function isValidProgressPayload(payload) {
  if (
    payload === null
    || typeof payload !== "object"
    || Array.isArray(payload)
  ) {
    return false;
  }

  return (
    isNonEmptyString(
      payload.title,
      255
    )
    && payload.platform ===
      "bilibili"
    && isNonEmptyString(
      payload.platform_video_id,
      255
    )
    && isValidBilibiliUrl(
      payload.url
    )
    && Number.isInteger(
      payload.progress_seconds
    )
    && payload.progress_seconds >= 0
    && (
      payload.duration_seconds === null
      || (
        Number.isInteger(
          payload.duration_seconds
        )
        && payload.duration_seconds >= 0
      )
    )
    && isValidReportedAt(
      payload.reported_at
    )
  );
}


async function readResponseBody(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}


function formatResponseBody(body) {
  if (body === null) {
    return "";
  }

  if (typeof body === "string") {
    return body;
  }

  try {
    return JSON.stringify(body);
  } catch {
    return String(body);
  }
}


async function sendProgress(payload) {
  if (
    !EXTENSION_TOKEN
    || EXTENSION_TOKEN ===
      "替换为与你.env一致的Token"
  ) {
    throw new Error(
      "Extension token is not configured"
    );
  }

  const controller =
    new AbortController();

  const timeoutId = setTimeout(
    () => {
      controller.abort();
    },
    REQUEST_TIMEOUT_MS
  );

  try {
    const response = await fetch(
      API_URL,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
          "X-Extension-Token":
            EXTENSION_TOKEN
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      }
    );

    const responseBody =
      await readResponseBody(response);

    if (!response.ok) {
      const detail =
        formatResponseBody(
          responseBody
        );

      throw new Error(
        detail
          ? `HTTP ${response.status}: ${detail}`
          : `HTTP ${response.status}`
      );
    }

    return responseBody;
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(
        `Request timed out after ${
          REQUEST_TIMEOUT_MS / 1000
        } seconds`
      );
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}


chrome.runtime.onMessage.addListener(
  (message, sender, sendResponse) => {
    if (
      message?.type !==
        "VIDEO_PROGRESS"
    ) {
      return false;
    }

    if (!isAllowedSender(sender)) {
      sendResponse({
        ok: false,
        error:
          "Message sender is not allowed"
      });

      return false;
    }

    if (
      !isValidProgressPayload(
        message.payload
      )
    ) {
      sendResponse({
        ok: false,
        error:
          "Invalid video progress payload"
      });

      return false;
    }

    sendProgress(message.payload)
      .then((data) => {
        sendResponse({
          ok: true,
          data
        });
      })
      .catch((error) => {
        console.error(
          "Progress upload failed:",
          error
        );

        sendResponse({
          ok: false,
          error:
            error instanceof Error
              ? error.message
              : String(error)
        });
      });

    // 保持消息通道开启，等待异步请求完成。
    return true;
  }
);
