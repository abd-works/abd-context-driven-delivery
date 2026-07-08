# generated-using: @extend/extend/extend.py
"""extend — extend and override another surface from this one."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CORE_PY = Path(__file__).resolve().parent / "_core.py"
_OPEN_PY = _REPO_ROOT / "open" / "open.py"

_spec = importlib.util.spec_from_file_location("_extend_core", _CORE_PY)
_core = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("_extend_core", _core)
_spec.loader.exec_module(_core)

_open_spec = importlib.util.spec_from_file_location("_open", _OPEN_PY)
_open = importlib.util.module_from_spec(_open_spec)
sys.modules.setdefault("_open", _open)
_open_spec.loader.exec_module(_open)

Surface = _core.Surface
SurfaceCli = _core.SurfaceCli
DeployTarget = _core.DeployTarget
ExtendCommand = _core.ExtendCommand
_as_slug_list = _core._as_slug_list
parse_extends = _core.parse_extends
parse_open = _core.parse_open
parse_local_sections = _core.parse_local_sections
read_frontmatter = _core.read_frontmatter
resolve_surface = _core.resolve_surface
search_roots_for = _core.search_roots_for
implements_extend = _core.implements_extend
effective_commands = _core.effective_commands
child_alignment_errors = _core.child_alignment_errors
_default_extend_actions = _core._default_extend_actions
integrate_override_sections = _core.integrate_override_sections
split_frontmatter = _core.split_frontmatter
merge_frontmatter = _core.merge_frontmatter
write_frontmatter = _core.write_frontmatter
_EXTENSION_FIELDS = _core._EXTENSION_FIELDS


class Extend:
    def __init__(self, surface: Surface) -> None:
        self._surface = surface

    def satisfy(self) -> list[str]:
        errors = self._surface_file_errors()
        fm = read_frontmatter(self._surface)
        has_extension = any(key in fm for key in _EXTENSION_FIELDS)

        if has_extension and not implements_extend(
            self._surface, search_roots_for(self._surface)
        ):
            errors.append(
                "extension frontmatter present but surface does not implement extend"
            )

        parent_name, _, child_overrides = parse_extends(fm.get("extends"))
        if parent_name is None:
            errors.append("extends.surface is required")
        elif implements_extend(self._surface, search_roots_for(self._surface)):
            parent = resolve_surface(str(parent_name), search_roots_for(self._surface))
            if parent is None:
                errors.append(f"extends parent not found: {parent_name}")
            else:
                parent_fm = read_frontmatter(parent)
                _, must_be_overridden = parse_open(parent_fm.get("open"))
                must_override = set(must_be_overridden) or set(
                    _as_slug_list(parent_fm.get("mustOverride"))
                )
                overrides = set(child_overrides) or set(_as_slug_list(fm.get("overrides")))
                missing = must_override - overrides
                if missing:
                    errors.append(
                        "missing required overrides: " + ", ".join(sorted(missing))
                    )

        open_surface = resolve_surface("open", search_roots_for(self._surface))
        if open_surface is not None and self._surface.name != "open":
            errors.extend(child_alignment_errors(open_surface))

        return errors

    def extend(self, surface_ref: str, actions: list[str]) -> str:
        target = resolve_surface(surface_ref, search_roots_for(self._surface))
        if target is None and Path(surface_ref).is_dir():
            target = Surface(Path(surface_ref).resolve())
        if target is None or not target.is_valid:
            raise RuntimeError(f"surface not found: {surface_ref}")
        if not implements_extend(target, search_roots_for(target)):
            raise RuntimeError(f"'{target.name}' does not implement extend")

        self._surface.assert_valid()
        action_slugs = _as_slug_list(actions) if actions else _default_extend_actions(self._surface)
        if not action_slugs:
            raise RuntimeError("no actions to extend")

        open_slugs, _ = parse_open(read_frontmatter(self._surface).get("open"))
        open_slugs_set = set(open_slugs)
        if open_slugs_set:
            closed = [s for s in action_slugs if s not in open_slugs_set]
            if closed:
                print(
                    "WARN: extending actions not marked open on "
                    f"{self._surface.name}: {', '.join(closed)}"
                )
        elif actions:
            local_slugs = {
                section.slug for section in parse_local_sections(self._surface.agentic_surface)
            }
            unknown = [s for s in action_slugs if s not in local_slugs]
            if unknown:
                print(
                    "WARN: extending actions not on "
                    f"{self._surface.name}: {', '.join(unknown)}"
                )

        fm, body = split_frontmatter(target.agentic_surface.read_text(encoding="utf-8"))
        _, _, existing_overrides = parse_extends(fm.get("extends"))
        extends_value = fm.get("extends")
        if isinstance(extends_value, dict):
            extends_value = {
                **extends_value,
                "surface": self._surface.name,
                "actions": action_slugs,
                "overrides": existing_overrides,
            }
        else:
            extends_value = {
                "surface": self._surface.name,
                "actions": action_slugs,
                "overrides": existing_overrides,
            }
        updated = merge_frontmatter(fm, {"extends": extends_value})
        write_frontmatter(target.agentic_surface, updated, body)
        return f"extended {self._surface.name} → {target.name}: {action_slugs}"

    def override(self, surface_ref: str, actions: list[str]) -> str:
        target = resolve_surface(surface_ref, search_roots_for(self._surface))
        if target is None and Path(surface_ref).is_dir():
            target = Surface(Path(surface_ref).resolve())
        if target is None or not target.is_valid:
            raise RuntimeError(f"surface not found: {surface_ref}")

        self._surface.assert_valid()
        action_slugs = _as_slug_list(actions)
        fm, body = split_frontmatter(target.agentic_surface.read_text(encoding="utf-8"))
        extended_surface, _, existing_overrides = parse_extends(fm.get("extends"))
        if extended_surface != self._surface.name:
            raise RuntimeError(
                f"'{target.name}' extends '{extended_surface}', not '{self._surface.name}'"
            )

        override_slugs = list(dict.fromkeys(existing_overrides + action_slugs))
        body = integrate_override_sections(self._surface, target, body, action_slugs)
        extends_value = fm.get("extends")
        if isinstance(extends_value, dict):
            extends_value = {**extends_value, "overrides": override_slugs}
        else:
            extends_value = {
                "surface": self._surface.name,
                "actions": [],
                "overrides": override_slugs,
            }
        updated = merge_frontmatter(fm, {"extends": extends_value})
        write_frontmatter(target.agentic_surface, updated, body)
        return f"override {self._surface.name} → {target.name}: {action_slugs}"

    def deploy(self, target: DeployTarget) -> None:
        self._surface.deploy(target)

    def clean(self, target: DeployTarget) -> None:
        self._surface.clean(target)

    def _surface_file_errors(self) -> list[str]:
        errors: list[str] = []
        if not self._surface.agentic_surface.is_file():
            errors.append(f"missing agentic surface: {self._surface.agentic_surface.name}")
        if not self._surface.api_surface.is_file():
            errors.append(f"missing API surface: {self._surface.api_surface.name}")
        if self._surface.name != self._surface.path.name:
            errors.append("surface identity mismatch between folder and files")
        return errors


class ExtendCli(_open.OpenCli):
    def __init__(self, api: Extend) -> None:
        super().__init__(_open.Open(api._surface))
        self._extend = api

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]

        extend_p = sub.add_parser(
            "extend",
            help="Extend another surface from this surface",
        )
        extend_p.add_argument("surface", help="Surface name to extend onto")
        extend_p.add_argument(
            "actions",
            nargs="*",
            help="Actions to extend; omit when this surface is fully open",
        )

        override_p = sub.add_parser(
            "override",
            help="Override actions from this surface onto another",
        )
        override_p.add_argument("surface", help="Surface name")
        override_p.add_argument("actions", nargs="+", help="Actions to override")

        return parser

    def _cmd_satisfy(self) -> int:
        errors = self._extend.satisfy()
        if errors:
            for err in errors:
                print(f"satisfy FAIL: {err}")
            return 1
        print(f"satisfy OK: {self._extend._surface.path}")
        return 0

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == "satisfy":
            return self._cmd_satisfy()

        if args.command == "extend":
            try:
                print(self._extend.extend(args.surface, args.actions))
            except RuntimeError as exc:
                print(f"satisfy FAIL: {exc}")
                return 1
            return 0

        if args.command == "override":
            try:
                print(self._extend.override(args.surface, args.actions))
            except RuntimeError as exc:
                print(f"satisfy FAIL: {exc}")
                return 1
            return 0

        return super()._dispatch(args, parser)


def main(argv: list[str] | None = None) -> int:
    surface = Surface(Path(__file__).resolve().parent)
    cli = ExtendCli(Extend(surface))
    return cli.execute(argv if argv is not None else sys.argv[1:])
