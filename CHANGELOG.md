[0.1.0] - 2026-07-27

完成 AI 助手第一阶段开发。  
已实现：  
创建 Agent  
支持 Tool 工具调用，可以查询固定标题视频  
支持长期数据库记忆观看历史  
支持自然语言查询  


[0.2.0]  - 2026-7-30  
增加查询最近观看视频功能
优化数据库结构，长期观看历史数据库由sqlite3数据库改为MySQL，同时采用了SQLModel ORM + SQLAlchemy 异步引擎 + aiomysql 异步驱动。
添加Alembic数据库迁移  
优化项目架构，将工具业务逻辑拆分出来


[0.3.0] - 2026-8-1
SQLModel数据库ORM模型增加字段  platform_video_id：平台原生视频 ID，duration_seconds：总时长  
数据库增加唯一约束platform, platform_video_id，添加普通索引last_watched_at
添加fastapi路由和应用接口用来接受Chrome扩展传来的数据，自动创建或者更新视频记录
创建Chrome扩展，自动记录B站观看记录
工具更新，打开视频工具可以自动定位观看进度


[0.4.0] - 2026-08-27
新增记忆系统：  
* 新增基于LangGraph`AsyncPostgresSaver`的会话记忆，通过`thread_id`持久化对话消息和Agent执行状态，支持跨轮次恢复上下文。  
* 新增长期记忆能力，使用 `AsyncPostgresStore` 持久化用户记忆，接入Embedding，通过向量相似度检索与当前问题最相关的长期记忆。  
* 通过extractor.py文件，创建长期记忆提取器，使用结构化输出识别用户的个人资料、偏好、项目和长期指令等信息。  
* 创建service.py文件，使它成为处理长期记忆的业务层，使用`MemoryService`类封装增加记忆，删除记忆等操作。
