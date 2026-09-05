"""Deploy Cursor rules from context-tool markdown Shared rules and fidelity ### Rules."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from primitives.assets.markdown_extractor import _FIDELITY_H2_NAMES, _h2_slug, _iter_h2_blocks

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONTEXT_TOOLS = _REPO_ROOT / "context_tools"
_SKIP_SLUGS = frozenset({"base", "create_context_tool", "agent_bdd", "car"})

# Glob patterns for Auto Attached rules (alwaysApply: false). Comma-separated per Cursor docs.
CONTEXT_TOOL_RULE_GLOBS: dict[str, dict[str, str]] = {
    "stories": {
        "shared": "**/sandbox/**/*.{py,md,js,ts,java},**/tests/**/*.{py,js,ts,java},**/*story-map*.md",
        "story_map": "**/*story-map*.md,**/sandbox/**/.context/**/*.{md,drawio}",
        "scenarios": "**/sandbox/**/*.{py,js,ts,java}",
        "acceptance_tests": "**/tests/**/*.{py,js,ts,java}",
    },
    "ux": {
        "shared": "**/sandbox/**/*.{html,drawio,json,md},**/.context/**/*ux*.{md,drawio}",
        "ia": "**/sandbox/**/.context/**/*.{drawio,md},**/*information-architecture*",
        "mockup": "**/sandbox/**/*.html,**/sandbox/**/.context/**",
        "front_end_code": "**/sandbox/**/*.html,**/src/**/*.{html,tsx,jsx,vue}",
    },
    "bdd": {
        "shared": "**/tests/**/*.{py,js,ts,java},**/primitives/**/*.py,**/context_tools/**/*.py",
        "modules": "**/*modules*.md,**/.context/**/*",
        "behavior": "**/tests/**/*.{py,js,ts,java}",
        "development": "**/tests/**/*.{py,js,ts,java},**/*.{py,js,ts,java}",
    },
    "ddd": {
        "shared": "**/domain/**/*.{md,py},**/*bounded-context*.md",
        "bounded_context": "**/*bounded-context*.md,**/domain/**/*.md",
        "building_blocks": "**/*bounded-context*.md,**/domain/**/*.md",
        "tactics": "**/domain/**/*.py,**/src/**/*.py",
    },
    "clean_engineering": {
        "shared": "**/domain/**/*,**/sandbox/**/modules/**",
        "modules": "**/sandbox/**/modules/**/*.{md,py},**/domain/**/modules/**",
        "model": "**/domain/**/*.md,**/sandbox/**/*.md",
        "code": "**/domain/**/*.py,**/src/**/*.py",
        "specification": "**/domain/**/*.md",
    },
    "cdd": {
        "shared": "**/.context/**/cdd-sketch.md,**/.context/sessions/**",
        "discovery": "**/.context/**/cdd-sketch.md,**/sandbox/**",
        "explore": "**/.context/**/cdd-sketch.md,**/sandbox/**",
        "spec": "**/.context/**/cdd-sketch.md,**/sandbox/**,**/tests/**",
        "engineer": "**/sandbox/**,**/tests/**,**/domain/**",
    },
}

_RULES_HEADING = re.compile(r"^(?:###\s+Rules|\*\*Rules:\*\*)\s*$", re.MULTILINE)
_SHARED_HEADING = re.compile(
    r"^(?:##\s+Shared\s+rules|\*\*Shared\s+Rules:\*\*)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_CDD_STAGE_RULES = re.compile(
    r"^##\s+Stages\s+\(CDD\s+fidelity\)\s*$", re.MULTILINE | re.IGNORECASE
)


@dataclass(frozen=True)
class ContextToolRuleSpec:
    tool_slug: str
    name: str
    description: str
    globs: str
    body: str
    folder: str = "context_tools"


def _escape_description(text: str) -> str:
    return text.replace('"', "'").splitlines()[0].strip()


def _skill_ref(tool_slug: str, fidelity: str) -> str:
    return f"{tool_slug}-{fidelity}"


def _rules_section_body(block: str) -> str:
    match = _RULES_HEADING.search(block)
    if not match:
        return ""
    lines: list[str] = []
    for line in block[match.end() :].splitlines():
        if re.match(r"^#{1,3}\s+\S", line) and not line.startswith("####"):
            break
        if line.strip().startswith("- **`"):
            lines.append(line)
    return "\n".join(lines).strip()


def _shared_rules_body(text: str) -> str:
    match = _SHARED_HEADING.search(text)
    if match:
        rest = text[match.end() :]
        end = re.search(r"^##\s+\S", rest, re.MULTILINE)
        section = rest[: end.start()] if end else rest
        lines = [line for line in section.splitlines() if line.strip().startswith("- **`")]
        if lines:
            return "\n".join(lines).strip()
    return ""


def _cdd_orchestration_rules(text: str) -> str:
    match = _CDD_STAGE_RULES.search(text)
    if not match:
        return ""
    rest = text[match.end() :]
    end = re.search(r"^##\s+\S|^#\s+\S", rest, re.MULTILINE)
    block = (match.group(0) + rest[: end.start()] if end else match.group(0) + rest).strip()
    return _rules_section_body(block)


def _fidelity_names_from_py(py_path: Path, class_name: str) -> frozenset[str]:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return frozenset()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or (class_name and node.name != class_name):
            continue
        for item in node.body:
            if not isinstance(item, ast.Assign):
                continue
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "fidelities":
                    if isinstance(item.value, ast.Dict):
                        names: set[str] = set()
                        for value in item.value.values:
                            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                                names.add(value.value)
                        return frozenset(names)
    return frozenset()


def _kit_markdown(tool_dir: Path, slug: str) -> Path | None:
    for candidate in (tool_dir / f"{slug}.md", tool_dir / f"{slug.replace('_', '-')}.md"):
        if candidate.is_file():
            return candidate
    for path in sorted(tool_dir.glob("*.md")):
        if path.name.startswith("."):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "# Contexts" in text or text.lstrip().startswith("# Instructions"):
            return path
    return None


def _shared_globs(tool_slug: str) -> str:
    cfg = CONTEXT_TOOL_RULE_GLOBS.get(tool_slug, {})
    explicit = cfg.get("shared", "").strip()
    if explicit:
        return explicit
    parts = [value for key, value in cfg.items() if key != "shared" and value.strip()]
    if not parts:
        return ""
    merged: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for pattern in part.split(","):
            cleaned = pattern.strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                merged.append(cleaned)
    return ",".join(merged)


def _glob_for(tool_slug: str, fidelity: str) -> str:
    cfg = CONTEXT_TOOL_RULE_GLOBS.get(tool_slug, {})
    return cfg.get(fidelity, cfg.get("shared", _shared_globs(tool_slug)))


def _oxford_or(items: list[str]) -> str:
    if len(items) <= 1:
        return items[0] if items else ""
    if len(items) == 2:
        return f"{items[0]} or {items[1]}"
    return ", ".join(items[:-1]) + f", or {items[-1]}"


def _rule_opener(
    tool_slug: str,
    *,
    shared: bool,
    fidelity: str = "",
    skill_refs: list[str],
    fidelity_names: frozenset[str] = frozenset(),
) -> str:
    refs = ", ".join(f"@{ref}" for ref in skill_refs)
    if shared:
        activities = _oxford_or([name.replace("_", " ") for name in sorted(fidelity_names)])
        return (
            f"When {activities}, also follow these rules on top of the fidelity-specific ones. "
            f"See {refs} for full generate guidance.\n\n"
        )
    activity = fidelity.replace("_", " ")
    return (
        f"When {activity}, follow these rules. "
        f"See @{_skill_ref(tool_slug, fidelity)} for the full skill.\n\n"
    )


def _fidelity_skill_refs(tool_slug: str, fidelity_names: frozenset[str]) -> list[str]:
    return [_skill_ref(tool_slug, name) for name in sorted(fidelity_names)]


def rules_for_context_tool(
    tool_dir: Path,
    *,
    slug: str,
    class_name: str = "",
) -> list[ContextToolRuleSpec]:
    md_path = _kit_markdown(tool_dir, slug)
    if md_path is None:
        return []
    text = md_path.read_text(encoding="utf-8", errors="replace")
    py_path = tool_dir / f"{slug}.py"
    if not py_path.is_file():
        py_files = list(tool_dir.glob("*.py"))
        py_path = py_files[0] if len(py_files) == 1 else py_path
    fidelity_names = _fidelity_names_from_py(py_path, class_name) if py_path.is_file() else frozenset()
    skill_refs = _fidelity_skill_refs(slug, fidelity_names)

    specs: list[ContextToolRuleSpec] = []

    shared_body = _shared_rules_body(text)
    if not shared_body and slug == "cdd":
        shared_body = _cdd_orchestration_rules(text)
    if shared_body:
        globs = _shared_globs(slug)
        specs.append(
            ContextToolRuleSpec(
                tool_slug=slug,
                name=slug,
                description=f"{slug} shared rules — apply across all fidelities",
                globs=globs,
                body=_rule_opener(
                    slug,
                    shared=True,
                    skill_refs=skill_refs,
                    fidelity_names=fidelity_names,
                )
                + "\n"
                + shared_body,
            )
        )

    for heading, block in _iter_h2_blocks(text):
        fidelity = _h2_slug(heading)
        if fidelity not in _FIDELITY_H2_NAMES and fidelity not in fidelity_names:
            continue
        rules_body = _rules_section_body(block)
        if not rules_body:
            continue
        specs.append(
            ContextToolRuleSpec(
                tool_slug=slug,
                name=fidelity,
                description=f"{slug} {fidelity.replace('_', ' ')} rules",
                globs=_glob_for(slug, fidelity),
                body=_rule_opener(
                    slug,
                    shared=False,
                    fidelity=fidelity,
                    skill_refs=skill_refs,
                )
                + "\n"
                + rules_body,
            )
        )

    return specs


def iter_context_tool_dirs(repo_root: Path | None = None) -> list[tuple[str, Path, str]]:
    """Return (slug, tool_dir, class_name) for deployable context tools."""
    root = repo_root or _REPO_ROOT
    tools_root = root / "context_tools"
    if not tools_root.is_dir():
        return []
    rows: list[tuple[str, Path, str]] = []
    for child in sorted(tools_root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in _SKIP_SLUGS:
            continue
        py_files = [
            p
            for p in child.glob("*.py")
            if p.name != "__init__.py" and "spec" not in p.name
        ]
        if not py_files:
            continue
        py_path = child / f"{child.name}.py"
        if not py_path.is_file():
            py_path = py_files[0]
        class_name = ""
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    break
        except (OSError, SyntaxError):
            class_name = ""
        rows.append((child.name, child, class_name))
    return rows


def all_context_tool_rule_specs(repo_root: Path | None = None) -> list[ContextToolRuleSpec]:
    specs: list[ContextToolRuleSpec] = []
    for slug, tool_dir, class_name in iter_context_tool_dirs(repo_root):
        specs.extend(rules_for_context_tool(tool_dir, slug=slug, class_name=class_name))
    return specs
