
"""
    4. 结构切分（Structure-aware Chunking）

按文档自身的标题层级切块。每个块不仅包含当前层级的正文，还会把从根到当前标题的
**所有父级标题**连带着放在块的最前面，这样单独看任意一个块，也能知道
它出自文档的哪一章哪一节。

通过 `split_level` 参数控制「从第几级标题开始切」：

    split_level=None（默认）  → 按最细层级切：每个「叶子标题节点」成一个块
    split_level=2             → 从二级标题(##)起切：每个 ## 一节一个块，###/#### 归入块内
    split_level=3             → 从三级标题(###)起切
    split_level=4             → 从四级标题(####)起切
"""

import re
from typing import List, Dict, Optional

# 标题行：# 后面必须跟空格，1~6 级（# 到 ######）
heading_pat = re.compile(r'^(#{1,6})\s+(.*)$')
fence_pat = re.compile(r'^```')


def _new_node(level: int, title: str) -> Dict:
    """标题树节点：{"level", "title", "body"(直接正文), "children"(子标题)}"""
    return {"level": level, "title": title, "body": [], "children": []}


def _build_tree(md_text: str) -> Dict:
    """把 md 解析成一棵标题树。"""
    root = _new_node(0, "")
    stack = [root]
    in_code = False

    for line in md_text.splitlines():
        if fence_pat.match(line.strip()):
            in_code = not in_code
            stack[-1]["body"].append(line)
            continue
        m = heading_pat.match(line) if not in_code else None
        if m:
            level = len(m.group(1))
            node = _new_node(level, m.group(2).strip())
            while stack[-1]["level"] >= level:
                stack.pop()
            stack[-1]["children"].append(node)
            stack.append(node)
        elif line.strip():
            stack[-1]["body"].append(line)

    return root


def _collect_roots(root: Dict, split_level: Optional[int]) -> List:
    """收集「块起点」节点及其父级链。

    标题级别 >= split_level 的节点成为块起点，更粗层级继续下钻；
    没有子标题的叶子节点（有正文）自己成块，避免正文漏掉。
    split_level=None 表示一路下钻到最细（叶子），即按最细层级切。
    """
    roots = []

    def rec(node, path):
        if not node["children"]:
            if node["level"] > 0 and node["body"]:
                roots.append((node, path))
            return
        for c in node["children"]:
            p = path + [(c["level"], c["title"])]
            if split_level is not None and c["level"] >= split_level:
                roots.append((c, p))
            else:
                rec(c, p)

    rec(root, [])
    return roots


def _render_body(node: Dict) -> str:
    """输出块起点的正文：直接正文 + 子标题（含子标题文本与子正文）。"""
    lines = list(node["body"])
    for c in node["children"]:
        lines.append("#" * c["level"] + " " + c["title"])
        lines.append(_render_body(c))
    return "\n".join(lines)


def _make_chunk(header_lines: List[str], body: str) -> Dict:
    """把父级标题链 + 正文拼成一个块。"""
    return {
        "text": "\n".join(header_lines) + "\n\n" + body,
        "meta": {"breadcrumbs": [ln.lstrip("#").strip() for ln in header_lines]},
    }


# 结构切分
def structure_chunk(
    md_text: str,
    split_level: Optional[int] = None,
    max_len: int = 200,
    min_len: int = 20,
) -> List[Dict]:
    """结构切分。

    Args:
        md_text:     原始 Markdown 文本。
        split_level: 从第几级标题开始切。None 表示按最细层级切（每个叶子标题成块）。
        max_len:     块正文长度上限，超长块按段落二次切分（子块同样前置父级标题）。
        min_len:     块长度下限，过短块并入前一块（同一父级链下）。

    Returns:
        list[dict]，每项 {"text": 父级标题链 + 正文, "meta": {"breadcrumbs": [...]}}
        其中父级标题链（含当前标题）全部排在正文前面。
    """
    chunks = []
    for node, path in _collect_roots(_build_tree(md_text), split_level):
        header_lines = ["#" * lv + " " + t for lv, t in path]
        body = _render_body(node).strip()
        if not body:
            continue

        # 超长正文：按段落二次切分，每个子块同样前置父级标题链
        if len(body) > max_len:
            paras = [p.strip() for p in body.split("\n\n") if p.strip()]
            buf = ""
            for p in paras:
                if len(buf) + len(p) + 2 <= max_len:
                    buf += ("\n\n" + p) if buf else p
                else:
                    if buf:
                        chunks.append(_make_chunk(header_lines, buf))
                    buf = p
            if buf:
                chunks.append(_make_chunk(header_lines, buf))
        else:
            chunks.append(_make_chunk(header_lines, body))

    # 过短的块并入前一块（同一父级链下）
    merged = []
    for ch in chunks:
        if (merged and len(ch["text"]) < min_len
                and merged[-1]["meta"]["breadcrumbs"] == ch["meta"]["breadcrumbs"]):
            merged[-1]["text"] += "\n\n" + ch["text"]
        else:
            merged.append(ch)

    return merged

# 演示入口
if __name__ == '__main__':
    fp = open('../docs/结构切分-原始文本.txt', "r", encoding="utf-8")
    text = fp.read()

    for lv in [None, 2, 3, 4]:
        chunks = structure_chunk(text, split_level=lv)
        label = "最细层级(默认)" if lv is None else f"第 {lv} 级"
        print(f"\n{'=' * 70}\n切分层级：{label}  →  共 {len(chunks)} 个块\n{'=' * 70}")
        for i, ch in enumerate(chunks):
            print(f"---------- 块 {i + 1} ----------")
            print(ch["text"])
            print()
