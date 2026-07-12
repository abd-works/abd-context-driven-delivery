# generated-using: @open/open/open.py
"""open — mark this surface's actions open for extension."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SURFACE_PY = _REPO_ROOT / "surface" / "surface.py"
_CORE_PY = _REPO_ROOT / "extend" / "_core.py"
_ALIGN_PY = Path(__file__).resolve().parent / "check_alignment.py"

_surface_spec = importlib.util.spec_from_file_location("_surface", _SURFACE_PY)
_surface = importlib.util.module_from_spec(_surface_spec)
sys.modules.setdefault("_surface", _surface)
_surface_spec.loader.exec_module(_surface)

_core_spec = importlib.util.spec_from_file_location("_extend_core", _CORE_PY)
_core = importlib.util.module_from_spec(_core_spec)
sys.modules.setdefault("_extend_core", _core)
_core_spec.loader.exec_module(_core)

_align_spec = importlib.util.spec_from_file_location("_open_align", _ALIGN_PY)
_align = importlib.util.module_from_spec(_align_spec)
sys.modules.setdefault("_open_align", _align)
_align_spec.loader.exec_module(_align)

Surface = _surface.Surface
alignment_errors = _align.alignment_errors
child_alignment_errors = _core.child_alignment_errors

def _read_frontmatter(surface: Surface) -> dict:
    if not surface.agentic_surface.is_file():
        return {}
    text = surface.agentic_surface.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        import yaml

        data = yaml.safe_load(parts[1]) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}

def _parse_open(value: object) -> tuple[list[str], list[str]]:
    if value is None:
        return [], []
    if isinstance(value, dict):
        actions = value.get("actions") or []
        must_override = value.get("mustBeOveridden") or []
        return (
            [_slug(str(item)) for item in actions] if isinstance(actions, list) else [],
            [_slug(str(item)) for item in must_override]
            if isinstance(must_override, list)
            else [],
        )
    if isinstance(value, list):
        return [_slug(str(item)) for item in value], []
    return [_slug(str(value))], []

def _slug(title: str) -> str:
    return "-".join(
        part
        for part in "".join(ch.lower() if ch.isalnum() else " " for ch in title).split()
    )

def _as_slug_list(actions: list[str]) -> list[str]:
    return [_slug(action) for action in actions]

def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        import yaml

        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        fm = {}
    body = parts[2].lstrip("\n")
    return fm if isinstance(fm, dict) else {}, body

def _write_frontmatter(path: Path, frontmatter: dict, body: str) -> None:
    import yaml

    payload = yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False).rstrip()
    path.write_text(f"---\n{payload}\n---\n\n{body.lstrip()}", encoding="utf-8")

class Open:
    def __init__(self, surface: Surface) -> None:
        self._surface = surface

    def satisfy(self) -> list[str]:
        errors = alignment_errors(self._surface.path)
        errors.extend(self._parent_satisfy_errors())
        errors.extend(self._open_frontmatter_errors())
        errors.extend(child_alignment_errors(self._surface))
        return errors

    def _parent_satisfy_errors(self) -> list[str]:
        fm = _read_frontmatter(self._surface)
        extends = fm.get("extends")
        parent_name: str | None = None
        if isinstance(extends, dict):
            parent_name = extends.get("surface")
        elif isinstance(extends, str):
            parent_name = extends
        if not parent_name:
            return []

        parent_dir = (_REPO_ROOT / str(parent_name)).resolve()
        if not parent_dir.is_dir():
            return [f"extends parent not found: {parent_name}"]

        for path in (
            _REPO_ROOT / "surface" / "check_alignment.py",
            _REPO_ROOT / ".cdd" / "surface" / "check_alignment.py",
        ):
            if not path.is_file():
                continue
            spec = importlib.util.spec_from_file_location("_surface_satisfy", path)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.alignment_errors(parent_dir)
        return []

    def open(self, actions: list[str]) -> None:
        self._surface.assert_valid()
        fm, body = _split_frontmatter(self._surface.agentic_surface.read_text(encoding="utf-8"))
        slugs = _as_slug_list(actions)
        _, must_be = _parse_open(fm.get("open"))
        fm["open"] = {"actions": slugs, "mustBeOveridden": must_be}
        _write_frontmatter(self._surface.agentic_surface, fm, body)

    def deploy(self, target: Surface.DeployTarget) -> None:
        self._surface.deploy(target)

    def clean(self, target: Surface.DeployTarget) -> None:
        self._surface.clean(target)

    def _local_action_slugs(self) -> set[str]:
        if not self._surface.agentic_surface.is_file():
            return set()
        text = self._surface.agentic_surface.read_text(encoding="utf-8")
        if text.startswith("---"):
            parts = text.split("---", 2)
            body = parts[2] if len(parts) > 2 else text
        else:
            body = text
        return {
            _slug(line[3:].strip())
            for line in body.splitlines()
            if line.startswith("## ")
        }

    def _open_frontmatter_errors(self) -> list[str]:
        errors: list[str] = []
        fm = _read_frontmatter(self._surface)
        open_value = fm.get("open")
        if open_value is None:
            return errors
        if not isinstance(open_value, dict):
            errors.append("open frontmatter must be a map with actions and mustBeOveridden")
            return errors

        local_slugs = self._local_action_slugs()
        open_actions, must_override = _parse_open(open_value)
        for key, _ in (("actions", open_actions), ("mustBeOveridden", must_override)):
            raw = open_value.get(key)
            if raw is not None and not isinstance(raw, list):
                errors.append(f"open.{key} must be a list")

        for action in open_actions:
            if action not in local_slugs:
                errors.append(f"open.actions orphan '{action}' — not a ## action on this surface")
        for action in must_override:
            if action not in local_slugs:
                errors.append(
                    f"open.mustBeOveridden orphan '{action}' — not a ## action on this surface"
                )
        return errors

class OpenCli(Surface.Cli):
    def __init__(self, api: Open) -> None:
        super().__init__(api._surface)
        self._api = api

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]
        sub.add_parser("satisfy", help="Verify open frontmatter aligns with this surface")
        open_p = sub.add_parser("open", help="Mark this surface's actions open for extension")
        open_p.add_argument("actions", nargs="*", help="Actions to mark open; omit for all")
        return parser

    def _cmd_satisfy(self) -> int:
        errors = self._api.satisfy()
        if errors:
            for err in errors:
                print(f"satisfy FAIL: {err}")
            return 1
        print(f"satisfy OK: {self._api._surface.path}")
        return 0

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == "satisfy":
            return self._cmd_satisfy()
        if args.command == "open":
            self._api.open(args.actions)
            slugs = _as_slug_list(args.actions)
            print(f"open: {slugs or 'all'} → {self._api._surface.agentic_surface}")
            return 0
        return super()._dispatch(args, parser)

def main(argv: list[str] | None = None) -> int:
    surface = Surface(Path(__file__).resolve().parent)
    cli = OpenCli(Open(surface))
    return cli.execute(argv if argv is not None else sys.argv[1:])
