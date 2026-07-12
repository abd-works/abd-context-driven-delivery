# generated-using: @capability/{capability}/{capability}.py
"""capability — discover, parse, deploy, and clean CDD capabilities."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXTEND_PY = _REPO_ROOT / "extend" / "extend.py"
_spec = importlib.util.spec_from_file_location("_extend", _EXTEND_PY)
_extend_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("_extend", _extend_mod)
_spec.loader.exec_module(_extend_mod)

Surface = _extend_mod.Surface
Extend = _extend_mod.Extend
ExtendCli = _extend_mod.ExtendCli
ExtendCommand = _extend_mod.ExtendCommand
parse_local_sections = _extend_mod.parse_local_sections
search_roots_for = _extend_mod.search_roots_for
implements_extend = _extend_mod.implements_extend
effective_commands = _extend_mod.effective_commands

Capability = Surface
CapabilityCommand = ExtendCommand


class CapabilityCli(ExtendCli):
    def __init__(self, capability: Capability) -> None:
        super().__init__(Extend(capability))
        self._capability = capability

    @property
    def commands(self) -> list[CapabilityCommand]:
        if implements_extend(self._capability, search_roots_for(self._capability)):
            return effective_commands(
                self._capability, search_roots_for(self._capability)
            )
        return [
            CapabilityCommand(section.title, section.description)
            for section in parse_local_sections(self._capability.agentic_surface)
        ]

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]

        identify_p = sub.add_parser(
            "identify", help="Check whether a path is a valid capability"
        )
        identify_p.add_argument("path", help="Path to check")

        discover_p = sub.add_parser(
            "discover", help="Find all CDD capabilities under a root directory"
        )
        discover_p.add_argument("root", help="Root directory to search")
        discover_p.add_argument(
            "--recursive", action="store_true", help="Search recursively (any depth)"
        )

        sub.add_parser("list", help="List effective commands from the capability .md")

        return parser

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        cmd = args.command

        if cmd == "identify":
            path = Path(args.path).resolve()
            cap = Capability(path)
            if cap.is_valid:
                print(f"valid capability: {path}")
                return 0
            print(f"not a capability (missing .cdd-config.json): {path}")
            return 1

        if cmd == "discover":
            root = Path(args.root).resolve()
            caps = list_capabilities(root, recursive=getattr(args, "recursive", False))
            if not caps:
                print(f"no capabilities found under {root}")
            for p in caps:
                print(p)
            return 0

        if cmd == "list":
            for c in self.commands:
                suffix = f" (from @{c.inherited_from})" if c.is_inherited else ""
                print(f"{c.slug}: {c.title}{suffix}")
            return 0

        return super()._dispatch(args, parser)


def is_capability(path: Path) -> bool:
    return Capability(path).is_valid


def list_capabilities(root: Path, *, recursive: bool = False) -> list[Path]:
    pattern = "**/.cdd-config.json" if recursive else "*/.cdd-config.json"
    return sorted(p.parent for p in root.glob(pattern))


def main(argv: list[str] | None = None) -> int:
    capability = Capability(Path(__file__).resolve().parent)
    cli = CapabilityCli(capability)
    return cli.execute(argv if argv is not None else sys.argv[1:])
