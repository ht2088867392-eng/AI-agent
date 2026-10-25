---
id: video_watch
version: "1.0"
description: 查询、查看进度或继续播放视频
tools:
  - find_title_video
  - find_latest_video
  - open_video
---

## 执行规则

1. 用户指定标题时，先调用 `find_title_video`。
2. 用户没有指定标题时，调用 `find_latest_video`。
3. 用户只想查询进度时，不调用 `open_video`。
4. 用户要求播放或继续时，查询成功后调用 `open_video`。
5. 只有工具返回 `opened=true` 时，才能告诉用户已经打开。
6. 没有找到记录时，不得调用 `open_video`。
7. `open_video` 只接收 `url` 和 `progress_seconds`，必须使用查询结果中的值，不要传入 `platform`。
8. 不要编造标题、链接或观看进度，也不要只返回 URL 就声称已经打开。
9. 此技能仅处理视频；如果用户要打开文件或执行其他任务，明确说明当前工具不支持。
