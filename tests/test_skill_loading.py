from pathlib import Path

import pytest

from app.agent.skill_loader import SkillLoadError, load_skills, render_skill_catalog
from app.tools.skill_tools import build_load_skill_tool


TOOLS = {"find_title_video", "find_latest_video", "open_video"}


def test_catalog_contains_only_skill_summaries():
    skills = load_skills(available_tools=TOOLS)

    catalog = render_skill_catalog(skills)

    assert "video_watch" in catalog
    assert "查询、查看进度或继续播放视频" in catalog
    assert "执行规则" not in catalog


def test_load_skill_returns_body_and_rejects_unknown_id():
    skills = load_skills(available_tools=TOOLS)
    load_skill = build_load_skill_tool(skills)

    result = load_skill.invoke({"skill_id": "video_watch"})
    unknown = load_skill.invoke({"skill_id": "../../.env"})

    assert "执行规则" in result
    assert "find_latest_video" in result
    assert "Unknown skill" in unknown
    assert ".env" not in unknown


def test_loader_rejects_skill_referencing_unregistered_tool(tmp_path: Path):
    (tmp_path / "invalid.md").write_text(
        "---\nid: invalid\nversion: '1'\ndescription: invalid\n"
        "tools: [delete_everything]\n---\nInstructions",
        encoding="utf-8",
    )

    with pytest.raises(SkillLoadError, match="未注册的工具"):
        load_skills(tmp_path, available_tools=TOOLS)


def test_loader_rejects_removed_triggers_field(tmp_path: Path):
    (tmp_path / "legacy.md").write_text(
        "---\nid: legacy\nversion: '1'\ndescription: legacy\n"
        "triggers: [test]\ntools: []\n---\nInstructions",
        encoding="utf-8",
    )

    with pytest.raises(SkillLoadError, match="不支持的字段"):
        load_skills(tmp_path, available_tools=TOOLS)
