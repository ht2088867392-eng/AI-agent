const REPORT_INTERVAL_MS = 15_000;
const MIN_PROGRESS_CHANGE_SECONDS = 5;

let lastReportKey = null;
let lastReportedProgress = -1;
let reportTimer = null;

let reportInFlight = false;
let reportPending = false;
let pendingForceReport = false;

const observedVideos = new WeakSet();


function isVisibleVideo(video) {
  const rect = video.getBoundingClientRect();

  return (
    rect.width > 0
    && rect.height > 0
    && video.offsetParent !== null
  );
}


function getVideoArea(video) {
  const rect = video.getBoundingClientRect();

  return rect.width * rect.height;
}


function findVideoElement() {
  const videos = Array.from(
    document.querySelectorAll("video")
  );

  if (videos.length === 0) {
    return null;
  }

  const playingVideo = videos.find(
    (video) =>
      !video.paused
      && !video.ended
      && video.readyState >=
        HTMLMediaElement.HAVE_CURRENT_DATA
      && isVisibleVideo(video)
  );

  if (playingVideo) {
    return playingVideo;
  }

  const visibleVideos = videos
    .filter(isVisibleVideo)
    .sort(
      (left, right) =>
        getVideoArea(right) - getVideoArea(left)
    );

  const visibleVideoWithMetadata =
    visibleVideos.find(
      (video) =>
        video.readyState >=
          HTMLMediaElement.HAVE_METADATA
        && Number.isFinite(video.duration)
        && video.duration > 0
    );

  if (visibleVideoWithMetadata) {
    return visibleVideoWithMetadata;
  }

  return (
    visibleVideos[0]
    ?? videos.find(
      (video) =>
        Number.isFinite(video.duration)
        && video.duration > 0
    )
    ?? videos[0]
  );
}

function formatLocalDateTime(date = new Date()) {
  const pad = (value) =>
    String(value).padStart(2, "0");

  return (
    `${date.getFullYear()}-`
    + `${pad(date.getMonth() + 1)}-`
    + `${pad(date.getDate())}T`
    + `${pad(date.getHours())}:`
    + `${pad(date.getMinutes())}:`
    + `${pad(date.getSeconds())}`
  );
}

function buildReport() {
  const page = detectVideoPage();
  const video = findVideoElement();

  if (!page || !video) {
    return null;
  }

  if (
    !Number.isFinite(video.currentTime)
    || video.currentTime < 0
  ) {
    return null;
  }

  const progressSeconds = Math.max(
    0,
    Math.floor(video.currentTime)
  );

  const durationSeconds =
    Number.isFinite(video.duration)
    && video.duration >= 0
      ? Math.floor(video.duration)
      : null;

  return {
    type: "VIDEO_PROGRESS",
    payload: {
      title: page.title,
      platform: page.platform,
      platform_video_id:
        page.platformVideoId,
      url: page.canonicalUrl,
      progress_seconds: progressSeconds,
      duration_seconds: durationSeconds,
      reported_at: formatLocalDateTime()
    }
  };
}


function getReportKey(message) {
  const payload = message.payload;

  return [
    payload.platform,
    payload.platform_video_id
  ].join(":");
}


function shouldReport(
  message,
  force = false
) {
  const reportKey = getReportKey(message);

  const currentProgress =
    message.payload.progress_seconds;

  if (reportKey !== lastReportKey) {
    return true;
  }

  const changedBy = Math.abs(
    currentProgress - lastReportedProgress
  );

  if (force) {
    return changedBy > 0;
  }

  return (
    changedBy >= MIN_PROGRESS_CHANGE_SECONDS
  );
}


function markReportSuccessful(message) {
  lastReportKey = getReportKey(message);

  lastReportedProgress =
    message.payload.progress_seconds;
}


async function reportProgress(
  { force = false } = {}
) {
  if (reportInFlight) {
    reportPending = true;
    pendingForceReport =
      pendingForceReport || force;

    return;
  }

  const message = buildReport();

  if (
    !message
    || !shouldReport(message, force)
  ) {
    return;
  }

  reportInFlight = true;

  try {
    const response =
      await chrome.runtime.sendMessage(message);

    if (!response?.ok) {
      console.warn(
        "Video progress report failed:",
        response?.error
          ?? "Unknown background error"
      );

      return;
    }

    markReportSuccessful(message);
  } catch (error) {
    console.warn(
      "Unable to send progress report:",
      error
    );
  } finally {
    reportInFlight = false;

    if (reportPending) {
      const shouldForce =
        pendingForceReport;

      reportPending = false;
      pendingForceReport = false;

      queueMicrotask(() => {
        void reportProgress({
          force: shouldForce
        });
      });
    }
  }
}


function attachVideoListeners(video) {
  if (
    !video
    || observedVideos.has(video)
  ) {
    return;
  }

  observedVideos.add(video);

  video.addEventListener(
    "loadedmetadata",
    () => {
      void reportProgress();
    }
  );

  video.addEventListener(
    "play",
    () => {
      void reportProgress();
    }
  );

  video.addEventListener(
    "pause",
    () => {
      void reportProgress({
        force: true
      });
    }
  );

  video.addEventListener(
    "seeked",
    () => {
      void reportProgress({
        force: true
      });
    }
  );

  video.addEventListener(
    "ended",
    () => {
      void reportProgress({
        force: true
      });
    }
  );
}


function scanAndAttachVideoListeners() {
  const videos =
    document.querySelectorAll("video");

  for (const video of videos) {
    attachVideoListeners(video);
  }
}


function startVideoObserver() {
  scanAndAttachVideoListeners();

  const observer = new MutationObserver(
    () => {
      scanAndAttachVideoListeners();
    }
  );

  observer.observe(
    document.documentElement,
    {
      childList: true,
      subtree: true
    }
  );
}


function startTracking() {
  if (reportTimer !== null) {
    clearInterval(reportTimer);
  }

  startVideoObserver();

  void reportProgress();

  reportTimer = setInterval(
    () => {
      void reportProgress();
    },
    REPORT_INTERVAL_MS
  );
}


document.addEventListener(
  "visibilitychange",
  () => {
    if (
      document.visibilityState === "hidden"
    ) {
      void reportProgress({
        force: true
      });
    }
  }
);


window.addEventListener(
  "pagehide",
  () => {
    void reportProgress({
      force: true
    });
  }
);


startTracking();
