# generated-using: @extend/extend/_core.py
"""Shared extension frontmatter, inheritance at deploy, and helpers."""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SURFACE_PY = _REPO_ROOT / "surface" / "surface.py"
_spec = importlib.util.spec_from_file_location("_surface", _SURFACE_PY)
_surface_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("_surface", _surface_mod)
_spec.loader.exec_module(_surface_mod)

Surface = _surface_mod.Surface
_CONFIG_FILE = _surface_mod._CONFIG_FILE

_EXTENSION_FIELDS = frozenset({"extends", "overrides", "open", "mustOverride"})
_INFRASTRUCTURE_ACTIONS = frozenset(
    {"create", "satisfy", "deploy", "clean", "open", "extend"}
)


def _commands_dir(target: Surface.DeployTarget) -> Path:
    if target.ide == _surface_mod.IDE.CURSOR:
        return target.root / ".cursor" / "commands"
    return target.root / ".github" / "prompts"


def _command_suffix(target: Surface.DeployTarget) -> str:
    return ".md" if target.ide == _surface_mod.IDE.CURSOR else ".prompt.md"


def slug(title: str) -> str:
    return "-".join(
        part
        for part in "".join(ch.lower() if ch.isalnum() else " " for ch in title).split()
    )


def read_md_body(text: str) -> str:
    if not text.startswith("---"):
        return text
    match = re.match(r"^---\r?\n.*?\r?\n---\r?\n?", text, re.DOTALL)
    if not match:
        return text
    return text[match.end() :]


@dataclass
class _MdSection:
    title: str
    description: str

    @property
    def slug(self) -> str:
        return slug(self.title)


def parse_local_sections(md_path: Path) -> list[_MdSection]:
    if not md_path.is_file():
        return []
    body = read_md_body(md_path.read_text(encoding="utf-8"))
    sections: list[_MdSection] = []
    current: _MdSection | None = None

    for raw in body.splitlines():
        line = raw.strip()
        if line == "---":
            if current:
                sections.append(current)
            break
        if raw.startswith("## "):
            if current:
                sections.append(current)
            current = _MdSection(title=raw[3:].strip(), description="")
            continue
        if current and not current.description and line and not line.startswith("#"):
            current.description = line

    if current:
        sections.append(current)
    return sections


@dataclass(frozen=True)
class ExtendCommand:
    title: str
    description: str
    inherited_from: str | None = None

    @property
    def slug(self) -> str:
        return slug(self.title)

    @property
    def is_inherited(self) -> bool:
        return self.inherited_from is not None


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if not match:
        return {}, text
    raw = match.group(1)
    body = text[match.end() :]
    if yaml is None:
        return {}, body
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}, body
    if not isinstance(data, dict):
        return {}, body
    return data, body


def merge_frontmatter(existing: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    merged.update(updates)
    return merged


def write_frontmatter(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    if not frontmatter:
        path.write_text(body.lstrip("\n"), encoding="utf-8")
        return
    payload = yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False).rstrip()
    path.write_text(f"---\n{payload}\n---\n\n{body.lstrip()}", encoding="utf-8")


def read_frontmatter(surface: Surface) -> dict[str, Any]:
    if not surface.agentic_surface.is_file():
        return {}
    fm, _ = split_frontmatter(surface.agentic_surface.read_text(encoding="utf-8"))
    return fm


def resolve_surface(name: str, search_roots: list[Path]) -> Surface | None:
    for root in search_roots:
        candidate = (root / name).resolve()
        if candidate.is_dir() and (candidate / _CONFIG_FILE).is_file():
            return Surface(candidate)
        cdd = (root / ".cdd" / name).resolve()
        if cdd.is_dir() and (cdd / _CONFIG_FILE).is_file():
            return Surface(cdd)
    return None


def search_roots_for(surface: Surface) -> list[Path]:
    roots = [surface.path.parent, _REPO_ROOT]
    deploy = Surface.DeployRecord.load(surface)
    if deploy:
        roots.append(deploy.target_root.resolve())
        roots.append(deploy.target_root.resolve() / ".cdd")
    seen: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.append(resolved)
    return seen


def _as_slug_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [slug(value)]
    if isinstance(value, list):
        return [slug(str(item)) for item in value]
    return [slug(str(value))]


def parse_extends(value: Any) -> tuple[str | None, list[str], list[str]]:
    if value is None:
        return None, [], []
    if isinstance(value, str):
        return value, [], []
    if isinstance(value, dict):
        base = value.get("surface")
        if base is None:
            return None, [], []
        return (
            str(base),
            _as_slug_list(value.get("actions")),
            _as_slug_list(value.get("overrides")),
        )
    return str(value), [], []


def parse_open(value: Any) -> tuple[list[str], list[str]]:
    if value is None:
        return [], []
    if isinstance(value, dict):
        return (
            _as_slug_list(value.get("actions")),
            _as_slug_list(value.get("mustBeOveridden")),
        )
    return _as_slug_list(value), []


def local_action_slugs(surface: Surface) -> set[str]:
    return {section.slug for section in parse_local_sections(surface.agentic_surface)}


def discover_surfaces(root: Path) -> list[Surface]:
    surfaces: list[Surface] = []
    for config in sorted(root.glob("*/.cdd-config.json")):
        candidate = Surface(config.parent)
        if candidate._has_required_files():
            surfaces.append(candidate)
    return surfaces


def surfaces_extending(parent: Surface, root: Path) -> list[Surface]:
    return [
        surface
        for surface in discover_surfaces(root)
        if surface.name != parent.name
        and parse_extends(read_frontmatter(surface).get("extends"))[0] == parent.name
    ]


def available_action_slugs(surface: Surface) -> set[str]:
    deployed = {
        cmd.slug for cmd in effective_commands(surface, search_roots_for(surface))
    }
    _, extend_actions, _ = parse_extends(read_frontmatter(surface).get("extends"))
    return deployed | set(extend_actions)


def child_alignment_errors(parent: Surface) -> list[str]:
    errors: list[str] = []
    open_actions, must_override = parse_open(read_frontmatter(parent).get("open"))
    local_slugs = local_action_slugs(parent)
    available_slugs = available_action_slugs(parent)
    allowed_actions = set(open_actions) if open_actions else local_slugs
    required_overrides = set(must_override)

    for child in surfaces_extending(parent, parent.path.parent):
        _, child_actions, child_overrides = parse_extends(
            read_frontmatter(child).get("extends")
        )
        child_action_set = set(child_actions)
        child_override_set = set(child_overrides)

        for action in child_action_set:
            if action not in available_slugs:
                errors.append(
                    f"{child.name}: extends.actions orphan '{action}' "
                    f"— not an action on {parent.name}"
                )
            elif action not in allowed_actions:
                errors.append(
                    f"{child.name}: extends.actions '{action}' not open on {parent.name}"
                )

        missing = required_overrides - child_override_set
        if missing:
            errors.append(
                f"{child.name}: extends.overrides missing required "
                f"{', '.join(sorted(missing))} from open.mustBeOveridden"
            )

        for action in child_override_set:
            if action not in available_slugs:
                errors.append(
                    f"{child.name}: extends.overrides orphan '{action}' "
                    f"— not an action on {parent.name}"
                )

    return errors


def _parent_exposes(parent: Surface, cmd: ExtendCommand) -> bool:
    if cmd.slug in _INFRASTRUCTURE_ACTIONS:
        return True
    local_slugs = {section.slug for section in parse_local_sections(parent.agentic_surface)}
    if cmd.slug not in local_slugs:
        return False
    open_slugs, _ = parse_open(read_frontmatter(parent).get("open"))
    open_slugs_set = set(open_slugs)
    if not open_slugs_set:
        return True
    return cmd.slug in open_slugs_set


def _default_extend_actions(base: Surface) -> list[str]:
    open_slugs, _ = parse_open(read_frontmatter(base).get("open"))
    open_slugs_set = set(open_slugs)
    local_slugs = [section.slug for section in parse_local_sections(base.agentic_surface)]
    if not open_slugs_set:
        return local_slugs
    return [slug for slug in local_slugs if slug in open_slugs_set]


def implements_extend(surface: Surface, search_roots: list[Path] | None = None) -> bool:
    if surface.name in ("extend", "open"):
        return True
    roots = search_roots or search_roots_for(surface)
    parent_name, _ = parse_extends(read_frontmatter(surface).get("extends"))
    if not parent_name:
        return False
    parent = resolve_surface(str(parent_name), roots)
    if parent is None:
        return False
    return implements_extend(parent, roots)


def effective_commands(
    surface: Surface,
    search_roots: list[Path] | None = None,
    *,
    _visited: frozenset[str] | None = None,
) -> list[ExtendCommand]:
    roots = search_roots or search_roots_for(surface)
    visited = _visited or frozenset()
    if surface.name in visited:
        raise RuntimeError(f"extension cycle detected at '{surface.name}'")

    local = [
        ExtendCommand(section.title, section.description)
        for section in parse_local_sections(surface.agentic_surface)
    ]
    fm = read_frontmatter(surface)
    parent_name, extend_actions, extends_overrides = parse_extends(fm.get("extends"))

    if not parent_name or not implements_extend(surface, roots):
        return local

    parent = resolve_surface(str(parent_name), roots)
    if parent is None:
        raise RuntimeError(f"extends parent not found: {parent_name}")

    overrides = set(extends_overrides) or set(_as_slug_list(fm.get("overrides")))
    extend_action_slugs = set(extend_actions)
    parent_commands = effective_commands(
        parent, roots, _visited=visited | {surface.name}
    )
    local_slugs = {cmd.slug for cmd in local}
    merged: list[ExtendCommand] = list(local)

    for cmd in parent_commands:
        if cmd.slug in overrides:
            continue
        if cmd.slug in local_slugs:
            continue
        if extend_action_slugs and cmd.slug not in extend_action_slugs:
            if cmd.slug not in _INFRASTRUCTURE_ACTIONS:
                continue
        if not _parent_exposes(parent, cmd):
            continue
        merged.append(
            ExtendCommand(
                cmd.title,
                f"read @{parent.name} § {cmd.title}",
                inherited_from=parent.name,
            )
        )

    return merged


def parse_section_blocks(body: str) -> list[tuple[str, str, str]]:
    blocks: list[tuple[str, str, str]] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("## "):
            title = lines[i][3:].strip()
            start = i
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            block = "\n".join(lines[start:i]).strip() + "\n"
            blocks.append((slug(title), title, block))
        else:
            i += 1
    return blocks


def split_preamble(body: str) -> tuple[str, list[tuple[str, str, str]]]:
    lines = body.splitlines()
    preamble_end = 0
    while preamble_end < len(lines) and not lines[preamble_end].startswith("## "):
        preamble_end += 1
    preamble = "\n".join(lines[:preamble_end]).strip()
    sections = parse_section_blocks("\n".join(lines[preamble_end:]))
    return preamble, sections


def _adapt_section_block(block: str, base: Surface, sub: Surface) -> str:
    return (
        block.replace(f"@{base.name}", f"@{sub.name}")
        .replace(f"`{base.name}`", f"`{sub.name}`")
        .replace(f"python -m {base.name}", f"python -m {sub.name}")
    )


def integrate_override_sections(
    base: Surface,
    sub: Surface,
    sub_body: str,
    override_slugs: list[str],
) -> str:
    base_body = read_md_body(base.agentic_surface.read_text(encoding="utf-8"))
    base_sections = parse_section_blocks(base_body)
    base_by_slug = {s: (t, b) for s, t, b in base_sections}
    base_order = [s for s, _, _ in base_sections]

    preamble, sub_sections = split_preamble(sub_body)
    sub_by_slug = {s: (t, b) for s, t, b in sub_sections}

    merged_slugs = list(dict.fromkeys(s for s, _, _ in sub_sections))
    for action_slug in override_slugs:
        if action_slug in sub_by_slug or action_slug not in base_by_slug:
            continue
        insert_at = len(merged_slugs)
        if action_slug in base_order:
            target_idx = base_order.index(action_slug)
            for i, existing in enumerate(merged_slugs):
                if existing in base_order and base_order.index(existing) > target_idx:
                    insert_at = i
                    break
        merged_slugs.insert(insert_at, action_slug)

    blocks: list[str] = []
    if preamble:
        blocks.append(preamble)
        blocks.append("")
    for action_slug in merged_slugs:
        if action_slug in sub_by_slug:
            blocks.append(sub_by_slug[action_slug][1].rstrip())
        else:
            title, block = base_by_slug[action_slug]
            blocks.append(_adapt_section_block(block, base, sub).rstrip())
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def commands_for_deploy(surface: Surface) -> list[ExtendCommand]:
    if not implements_extend(surface, search_roots_for(surface)):
        return [
            ExtendCommand(section.title, section.description)
            for section in parse_local_sections(surface.agentic_surface)
        ]
    return effective_commands(surface, search_roots_for(surface))


def deploy(surface: Surface, target: Surface.DeployTarget) -> None:
    surface.assert_valid()
    surface._copy_to_cdd(target)
    _write_skill_wrapper(surface, target)
    _write_command_wrappers(surface, target)
    Surface.DeployRecord(ide=target.ide, target_root=target.root).save(surface)


def clean(surface: Surface, target: Surface.DeployTarget) -> None:
    surface._clean(target)
    for cmd in commands_for_deploy(surface):
        cmd_file = (
            _commands_dir(target)
            / f"{surface.name}-{cmd.slug}{_command_suffix(target)}"
        )
        if cmd_file.exists():
            cmd_file.unlink()


def _write_skill_wrapper(surface: Surface, target: Surface.DeployTarget) -> None:
    skill_dir = target.skills_dir / surface.name
    skill_dir.mkdir(parents=True, exist_ok=True)
    cdd_rel = f".cdd/{surface.name}/{surface.name}.md"
    body = read_md_body(surface.agentic_surface.read_text(encoding="utf-8"))
    blurb = ""
    for raw in body.splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith("#"):
            blurb = stripped
            break

    lines = [
        f"# {surface.name}",
        "",
        blurb,
        "",
        f"read in full → `{cdd_rel}`",
        "",
    ]
    for cmd in commands_for_deploy(surface):
        lines.append(f"## {cmd.title}")
        if cmd.inherited_from:
            lines.append(f"read @{cmd.inherited_from} § {cmd.title}")
        else:
            lines.append(f"read in full → `{cdd_rel}` §{cmd.title}")
        lines.append("")
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


def _write_command_wrappers(surface: Surface, target: Surface.DeployTarget) -> None:
    commands_dir = _commands_dir(target)
    commands_dir.mkdir(parents=True, exist_ok=True)
    cdd_rel = f".cdd/{surface.name}/{surface.name}.md"
    for cmd in commands_for_deploy(surface):
        path = commands_dir / (
            f"{surface.name}-{cmd.slug}{_command_suffix(target)}"
        )
        if cmd.inherited_from:
            body = f"read @{cmd.inherited_from} § {cmd.title}\n"
        else:
            body = (
                f"# {surface.name} — {cmd.title}\n\n"
                f"{cmd.description or ''}\n\n"
                f"read in full → `{cdd_rel}` §{cmd.title}\n"
            )
        path.write_text(body, encoding="utf-8")
