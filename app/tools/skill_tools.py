"""
负责把已加载的技能包装成 Agent 可调用的 load_skill 工具，让 Agent 按技能 ID 获取完整说明。
"""
from collections.abc import Iterable
from langchain.tools import tool
from app.agent.skill_loader import Skill


def build_load_skill_tool(skills: Iterable[Skill]):
    skills_by_id = {skill.id: skill for skill in skills}

    @tool("load_skill")
    def load_skill(skill_id: str) -> str:
        """Load the full instructions for a skill from the available skill catalog."""
        skill = skills_by_id.get(skill_id)
        if skill is None:
            available = ", ".join(sorted(skills_by_id)) or "none"
            return f"Unknown skill ID. Available skills: {available}."

        allowed_tools = ", ".join(skill.tools) or "none"
        return (
            f"Skill: {skill.id} (version {skill.version})\n"
            f"Description: {skill.description}\n"
            f"Tools intended for this skill: {allowed_tools}\n\n"
            f"{skill.instructions}"
        )

    return load_skill
