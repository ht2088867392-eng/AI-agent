from __future__ import annotations

import re
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import yaml


# 匹配 Markdown 文件开头的 YAML 元数据区：
# ---
# id: example
# ---
# 正文从第二个 --- 之后开始。DOTALL 让元数据可以跨多行匹配。
FRONTMATTER_PATTERN = re.compile(
    r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)",
    re.DOTALL,
)

# 技能 ID 只允许小写字母、数字、下划线和连字符，且首字符必须是字母或数字。
SKILL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# 技能 front matter 当前支持的字段白名单；拼错或添加未支持字段时会报错。
ALLOWED_FIELDS = {
    "id",
    "version",
    "description",
    "triggers",
    "tools",
}


class SkillLoadError(ValueError):
    """技能文件格式错误或引用了无效工具。"""


@dataclass(frozen=True)
class Skill:
    """解析后的技能数据；frozen=True 可避免加载后意外修改技能配置。"""

    # 与 front matter 对应的技能元数据。
    id: str
    version: str
    description: str
    # triggers 目前只保存元数据，不负责在代码里匹配用户输入。
    triggers: tuple[str, ...]
    # 技能声明计划使用的工具名称；加载时会检查这些名称是否已注册。
    tools: tuple[str, ...]
    # Markdown 元数据区之后的完整技能说明。
    instructions: str
    # 技能文件来源，便于报错或追踪配置。
    source: Path


def load_skills(
    skills_dir: Path | None = None,
    *,
    available_tools: Collection[str] | None = None,
) -> tuple[Skill, ...]:
    """加载并校验技能目录下的 Markdown 文件，返回 Skill 元组。

    skills_dir 未传入时默认读取当前文件旁边的 skills/ 目录。
    available_tools 若提供，则会拒绝声明了不存在工具的技能。
    """
    if skills_dir is None:
        skills_dir = Path(__file__).parent / "skills"

    if not skills_dir.is_dir():
        raise SkillLoadError(f"技能目录不存在：{skills_dir}")

    # 同时用列表保留排序结果，用集合快速检查重复 ID。
    loaded: list[Skill] = []
    seen_ids: set[str] = set()

    # 排序可保证不同机器上技能加载和展示顺序一致。
    for path in sorted(skills_dir.glob("*.md")):
        skill = _load_one(path, available_tools=available_tools)

        if skill.id in seen_ids:
            raise SkillLoadError(f"重复的技能 id：{skill.id}")

        seen_ids.add(skill.id)
        loaded.append(skill)

    return tuple(loaded)


def render_skill_catalog(skills: Collection[Skill]) -> str:
    """只生成技能 ID 和简介，作为 Agent 提示词中的技能目录。

    不包含 instructions，完整规则由 load_skill 工具按需返回给模型。
    """
    return "\n".join(
        f"- {skill.id}: {skill.description}"
        for skill in skills
    )


def _load_one(
    path: Path,
    *,
    available_tools: Collection[str] | None,
) -> Skill:
    """读取并验证单个技能文件，然后转换为 Skill 对象。"""
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)

    if match is None:
        raise SkillLoadError(
            f"{path.name} 缺少 YAML front matter，"
            "文件开头应以 --- 开始"
        )

    try:
        # safe_load 只解析普通 YAML 数据，不会执行 YAML 中的任意 Python 对象。
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise SkillLoadError(f"{path.name} 的 YAML 格式错误") from exc

    if not isinstance(metadata, dict):
        raise SkillLoadError(f"{path.name} 的 front matter 必须是对象")

    # 同时检查未知字段和必填字段，尽早暴露 front matter 配置错误。
    unknown_fields = set(metadata) - ALLOWED_FIELDS
    if unknown_fields:
        raise SkillLoadError(
            f"{path.name} 包含不支持的字段：{sorted(unknown_fields)}"
        )

    required_fields = {"id", "version", "description", "triggers", "tools"}
    missing_fields = required_fields - set(metadata)
    if missing_fields:
        raise SkillLoadError(
            f"{path.name} 缺少字段：{sorted(missing_fields)}"
        )

    skill_id = metadata["id"]
    if not isinstance(skill_id, str) or not SKILL_ID_PATTERN.fullmatch(skill_id):
        raise SkillLoadError(f"{path.name} 的 id 格式无效：{skill_id!r}")

    description = metadata["description"]
    if not isinstance(description, str) or not description.strip():
        raise SkillLoadError(f"{path.name} 的 description 不能为空")

    triggers = _string_tuple(metadata["triggers"], "triggers", path)
    tools = _string_tuple(metadata["tools"], "tools", path)

    if not triggers:
        raise SkillLoadError(f"{path.name} 至少需要一个 trigger")

    if available_tools is not None:
        unknown_tools = set(tools) - set(available_tools)     # tools集合和available_tools集合的差集
        if unknown_tools:
            raise SkillLoadError(
                f"{path.name} 引用了未注册的工具：{sorted(unknown_tools)}"
            )

    # 正则匹配结束的位置正好是 YAML 区块之后，剩余文本就是技能正文。
    instructions = text[match.end():].strip()
    if not instructions:
        raise SkillLoadError(f"{path.name} 的技能正文不能为空")

    return Skill(
        id=skill_id,
        version=str(metadata["version"]),
        description=description.strip(),
        triggers=triggers,
        tools=tools,
        instructions=instructions,
        source=path,
    )


def _string_tuple(value: object, field: str, path: Path) -> tuple[str, ...]:
    """验证 YAML 列表中的元素均为非空字符串，并转换成元组。"""
    if not isinstance(value, list):
        raise SkillLoadError(f"{path.name} 的 {field} 必须是列表")

    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise SkillLoadError(f"{path.name} 的 {field} 只能包含非空字符串")

    return tuple(item.strip() for item in value)
