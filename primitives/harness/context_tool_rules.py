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
# Prefer extension-based patterns — code and artifacts can live outside fixed folder names.
_PY = "**/*.py"
_MD = "**/*.md"
_PY_MD = "**/*.py,**/*.md"
_CODE = "**/*.py,**/*.js,**/*.ts,**/*.java,**/*.c,**/*.cs"
_PY_JS_TS_JAVA = "**/*.{py,js,ts,java}"

# Later fidelity Cursor rules include earlier fidelity rule bullets (same kit).
_FIDELITY_RULE_STACK: dict[str, dict[str, str]] = {
    "clean_engineering": {"code": "model"},
}

CONTEXT_TOOL_RULE_GLOBS: dict[str, dict[str, str]] = {
    "stories": {
        "shared": f"{_PY_MD},{_PY_JS_TS_JAVA},**/*story-map*.md",
        "story_map": "**/*story-map*.md,**/.context/**/*.{md,drawio}",
        "scenarios": _PY_JS_TS_JAVA,
        "acceptance_tests": _PY_JS_TS_JAVA,
    },
    "ux": {
        "shared": "**/*.{html,drawio,json,md}",
        "ia": "**/*.{drawio,md},**/*information-architecture*",
        "mockup": "**/*.html,**/.context/**",
        "front_end_code": "**/*.{html,tsx,jsx,vue,js,ts}",
    },
    "bdd": {
        "shared": f"{_PY_JS_TS_JAVA},**/*modules*.md",
        "modules": "**/*modules*.md,**/.context/**/*",
        "behavior": _PY_JS_TS_JAVA,
        "development": _PY_JS_TS_JAVA,
    },
    "ddd": {
        "shared": f"{_PY_MD},**/*bounded-context*.md",
        "bounded_context": "**/*bounded-context*.md,**/*.md",
        "building_blocks": "**/*bounded-context*.md,**/*.md",
        "tactics": _CODE,
    },
    "clean_engineering": {
        "shared": _PY_MD,
        "modules": _PY_MD,
        "model": _PY_MD,
        "code": _CODE,
        "specification": _MD,
    },
    "cdd": {
        "shared": "**/.context/**/cdd-sketch.md,**/.context/sessions/**",
        "discovery": "**/.context/**/cdd-sketch.md,**/*.{md,py}",
        "explore": "**/.context/**/cdd-sketch.md,**/*.{md,py}",
        "spec": "**/.context/**/cdd-sketch.md,**/*.{md,py,js,ts,java}",
        "engineer": f"{_CODE},**/*.md",
    },
}

_RULES_HEADING = re.compile(
    r"^(?:###\s+(?:Module\s+rules|Class\s+[Rr]ules|Rules)|\*\*Rules:\*\*)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
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


def _rule_bullets(body: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith("- **`"):
            return "\n".join(lines[index:]).strip()
    return body.strip()


def _apply_fidelity_rule_stacks(
    tool_slug: str, specs: list[ContextToolRuleSpec]
) -> list[ContextToolRuleSpec]:
    stacks = _FIDELITY_RULE_STACK.get(tool_slug, {})
    if not stacks:
        return specs
    by_name = {spec.name: spec for spec in specs}
    merged: list[ContextToolRuleSpec] = []
    for spec in specs:
        base_name = stacks.get(spec.name)
        if not base_name or base_name not in by_name:
            merged.append(spec)
            continue
        base_label = base_name.replace("_", " ")
        fidelity_label = spec.name.replace("_", " ")
        merged.append(
            ContextToolRuleSpec(
                tool_slug=spec.tool_slug,
                name=spec.name,
                description=spec.description,
                globs=spec.globs,
                body=(
                    f"When {fidelity_label}, follow these rules on top of the "
                    f"{base_label} rules. "
                    f"See @{_skill_ref(tool_slug, spec.name)} for the full skill.\n\n"
                    + _rule_bullets(by_name[base_name].body)
                    + "\n\n"
                    + _rule_bullets(spec.body)
                ),
                folder=spec.folder,
            )
        )
    return merged


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

    return _apply_fidelity_rule_stacks(slug, specs)


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
