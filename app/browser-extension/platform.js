function getBilibiliVideoId(url) {
  const match = url.pathname.match(
    /^\/video\/(BV[a-zA-Z0-9]+|av\d+)(?:\/|$)/i
  );

  if (!match) {
    return null;
  }

  const rawVideoId = match[1];

  if (/^bv/i.test(rawVideoId)) {
    return `BV${rawVideoId.slice(2)}`;
  }

  if (/^av/i.test(rawVideoId)) {
    return `av${rawVideoId.slice(2)}`;
  }

  return rawVideoId;
}


function normalizeTitle(title) {
  if (typeof title !== "string") {
    return "";
  }

  return title
    .replace(/_哔哩哔哩_bilibili$/i, "")
    .trim()
    .slice(0, 255);
}


function detectVideoPage() {
  let url;

  try {
    url = new URL(window.location.href);
  } catch {
    return null;
  }

  if (
    url.hostname !== "www.bilibili.com"
    || !url.pathname.startsWith("/video/")
  ) {
    return null;
  }

  const videoId = getBilibiliVideoId(url);

  if (!videoId) {
    return null;
  }

  const title = normalizeTitle(document.title);

  if (!title) {
    return null;
  }

  return {
    platform: "bilibili",
    platformVideoId: videoId,
    title,
    canonicalUrl:
      `https://www.bilibili.com/video/${videoId}`
  };
}
