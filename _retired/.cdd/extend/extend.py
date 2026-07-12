# generated-using: @extend/extend/extend.py
"""extend — frontmatter, inheritance at deploy, open/extend CLI."""
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
SurfaceCli = _surface_mod.SurfaceCli
DeployTarget = _surface_mod.DeployTarget
DeployRecord = _surface_mod.DeployRecord
_CONFIG_FILE = _surface_mod._CONFIG_FILE

_EXTENSION_FIELDS = frozenset({"extends", "overrides", "open", "mustOverride"})
_INFRASTRUCTURE_ACTIONS = frozenset(
    {"generate", "satisfy", "deploy", "clean", "open", "extend"}
)


def _commands_dir(target: DeployTarget) -> Path:
    if target.ide == _surface_mod.IDE.CURSOR:
        return target.root / ".cursor" / "commands"
    return target.root / ".github" / "prompts"


def _command_suffix(target: DeployTarget) -> str:
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
    if not surface.md_surface.is_file():
        return {}
    fm, _ = split_frontmatter(surface.md_surface.read_text(encoding="utf-8"))
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
    deploy = DeployRecord.load(surface)
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


def _parent_exposes(parent: Surface, cmd: ExtendCommand) -> bool:
    if cmd.slug in _INFRASTRUCTURE_ACTIONS:
        return True
    open_slugs = set(_as_slug_list(read_frontmatter(parent).get("open")))
    local_slugs = {section.slug for section in parse_local_sections(parent.md_surface)}
    return cmd.slug in local_slugs and cmd.slug in open_slugs


def implements_extend(surface: Surface, search_roots: list[Path] | None = None) -> bool:
    if surface.name == "extend":
        return True
    roots = search_roots or search_roots_for(surface)
    parent_name = read_frontmatter(surface).get("extends")
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
        for section in parse_local_sections(surface.md_surface)
    ]
    fm = read_frontmatter(surface)
    parent_name = fm.get("extends")

    if not parent_name or not implements_extend(surface, roots):
        return local

    parent = resolve_surface(str(parent_name), roots)
    if parent is None:
        raise RuntimeError(f"extends parent not found: {parent_name}")

    overrides = set(_as_slug_list(fm.get("overrides")))
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


def commands_for_deploy(surface: Surface) -> list[ExtendCommand]:
    if not implements_extend(surface, search_roots_for(surface)):
        return [
            ExtendCommand(section.title, section.description)
            for section in parse_local_sections(surface.md_surface)
        ]
    return effective_commands(surface, search_roots_for(surface))


def deploy(surface: Surface, target: DeployTarget) -> None:
    surface.assert_valid()
    surface._copy_to_cdd(target)
    _write_skill_wrapper(surface, target)
    _write_command_wrappers(surface, target)
    DeployRecord(ide=target.ide, target_root=target.root).save(surface)


def clean(surface: Surface, target: DeployTarget) -> None:
    surface._clean_minimal(target)
    for cmd in commands_for_deploy(surface):
        cmd_file = (
            _commands_dir(target)
            / f"{surface.name}-{cmd.slug}{_command_suffix(target)}"
        )
        if cmd_file.exists():
            cmd_file.unlink()


def _write_skill_wrapper(surface: Surface, target: DeployTarget) -> None:
    skill_dir = target.skills_dir / surface.name
    skill_dir.mkdir(parents=True, exist_ok=True)
    cdd_rel = f".cdd/{surface.name}/{surface.name}.md"
    body = read_md_body(surface.md_surface.read_text(encoding="utf-8"))
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


def _write_command_wrappers(surface: Surface, target: DeployTarget) -> None:
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


class ExtendCli(SurfaceCli):
    def __init__(self, surface: Surface) -> None:
        super().__init__(surface)
        self._surface = surface

    def _surface_file_errors(self) -> list[str]:
        errors: list[str] = []
        if not self._surface.md_surface.is_file():
            errors.append(f"missing agentic surface: {self._surface.md_surface.name}")
        if not self._surface.api_surface.is_file():
            errors.append(f"missing API surface: {self._surface.api_surface.name}")
        if self._surface.name != self._surface.path.name:
            errors.append("surface identity mismatch between folder and files")
        return errors

    def _cmd_satisfy(self) -> int:
        errors = self._surface_file_errors()
        fm = read_frontmatter(self._surface)
        has_extension = any(key in fm for key in _EXTENSION_FIELDS)

        if has_extension and not implements_extend(
            self._surface, search_roots_for(self._surface)
        ):
            errors.append(
                "extension frontmatter present but surface does not implement extend"
            )

        if fm.get("extends") and implements_extend(
            self._surface, search_roots_for(self._surface)
        ):
            parent_name = fm.get("extends")
            parent = resolve_surface(
                str(parent_name), search_roots_for(self._surface)
            )
            if parent is None:
                errors.append(f"extends parent not found: {parent_name}")
            else:
                must_override = set(
                    _as_slug_list(read_frontmatter(parent).get("mustOverride"))
                )
                overrides = set(_as_slug_list(fm.get("overrides")))
                missing = must_override - overrides
                if missing:
                    errors.append(
                        "missing required overrides: "
                        + ", ".join(sorted(missing))
                    )

        if errors:
            for err in errors:
                print(f"satisfy FAIL: {err}")
            return 1
        print(f"satisfy OK: {self._surface.path}")
        return 0

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]
        sub.add_parser("satisfy", help="Validate surface files and extension frontmatter")

        open_p = sub.add_parser("open", help="Mark actions open on a source surface")
        open_p.add_argument("target", help="Path to source surface folder")
        open_p.add_argument("actions", nargs="+", help="Action names to mark open")

        extend_p = sub.add_parser(
            "extend",
            help="Scaffold extension from source to target",
        )
        extend_p.add_argument("source", help="Source surface name or path")
        extend_p.add_argument("target", help="Target surface folder")
        extend_p.add_argument("actions", nargs="+", help="Explicit action list to extend")

        return parser

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        cmd = args.command

        if cmd == "satisfy":
            return self._cmd_satisfy()

        if cmd == "open":
            return self._cmd_open(Path(args.target), args.actions)

        if cmd == "extend":
            return self._cmd_extend(args.source, Path(args.target), args.actions)

        return super()._dispatch(args, parser)

    def _cmd_open(self, target: Path, actions: list[str]) -> int:
        surface = Surface(target.resolve())
        surface.assert_valid()
        if not implements_extend(surface, search_roots_for(surface)):
            print(
                f"WARN: '{surface.name}' does not implement extend — "
                "open metadata may not participate in inheritance."
            )
        fm, body = split_frontmatter(surface.md_surface.read_text(encoding="utf-8"))
        slugs = _as_slug_list(actions)
        updated = merge_frontmatter(fm, {"open": slugs})
        write_frontmatter(surface.md_surface, updated, body)
        print(f"open: {slugs} → {surface.md_surface}")
        return 0

    def _cmd_extend(
        self,
        source_ref: str,
        target_path: Path,
        actions: list[str],
    ) -> int:
        target = Surface(target_path.resolve())
        target.assert_valid()
        if not implements_extend(target, search_roots_for(target)):
            print(f"satisfy FAIL: target '{target.name}' does not implement extend")
            return 1

        source = resolve_surface(source_ref, search_roots_for(target))
        if source is None and Path(source_ref).is_dir():
            source = Surface(Path(source_ref).resolve())
        if source is None or not source.is_valid:
            print(f"satisfy FAIL: source not found: {source_ref}")
            return 1

        action_slugs = _as_slug_list(actions)
        open_slugs = set(_as_slug_list(read_frontmatter(source).get("open")))
        closed = [s for s in action_slugs if s not in open_slugs]
        if closed:
            print(
                "WARN: extending actions not marked open on source "
                f"{source.name}: {', '.join(closed)}"
            )

        fm, body = split_frontmatter(target.md_surface.read_text(encoding="utf-8"))
        updated = merge_frontmatter(
            fm,
            {"extends": source.name, "overrides": action_slugs},
        )

        for action_slug in action_slugs:
            title = action_slug.replace("-", " ").title()
            if f"## {title}" not in body:
                body = body.rstrip() + f"\n## {title}\n\nTODO: complete {title} override.\n"

        write_frontmatter(target.md_surface, updated, body)
        print(f"extended {source.name} → {target.name}: {action_slugs}")
        return 0


def main(argv: list[str] | None = None) -> int:
    surface = Surface(Path(__file__).resolve().parent)
    cli = ExtendCli(surface)
    return cli.execute(argv if argv is not None else sys.argv[1:])
