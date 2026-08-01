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


[0.3.0]
SQLModel数据库ORM模型增加字段  platform_video_id：平台原生视频 ID，duration_seconds：总时长  
数据库增加唯一约束platform, platform_video_id，添加普通索引last_watched_at
