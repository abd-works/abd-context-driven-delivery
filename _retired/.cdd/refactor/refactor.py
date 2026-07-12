"""refactor — extract or merge capabilities to keep each one focused and coherent."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_CDD_CAP = Path(__file__).resolve().parents[1] / "capability" / "capability.py"

import importlib.util
_spec = importlib.util.spec_from_file_location("capability", _CDD_CAP)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("capability", _mod)
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
_BaseCli = _mod.CapabilityCli


class CapabilityCli(_BaseCli):
    """refactor capability CLI."""

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == "extract":
            return self._extract(args)
        if args.command == "merge":
            return self._merge(args)
        return super()._dispatch(args, parser)

    def _extract(self, args: argparse.Namespace) -> int:
        print("Extract is a guided agentic action — follow refactor/references/extract.md")
        print(f"  source:  {args.source}")
        print(f"  target:  {args.target}")
        return 0

    def _merge(self, args: argparse.Namespace) -> int:
        print("Merge is a guided agentic action — follow refactor/references/merge.md")
        print(f"  capability-a: {args.capability_a}")
        print(f"  capability-b: {args.capability_b}")
        if args.master:
            print(f"  master:       {args.master}")
        return 0

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]

        ex = sub.add_parser("extract", help="Extract a portion of a capability into a new one")
        ex.add_argument("source", help="Source capability name")
        ex.add_argument("target", help="New capability name")

        mg = sub.add_parser("merge", help="Merge two capabilities into one")
        mg.add_argument("capability_a")
        mg.add_argument("capability_b")
        mg.add_argument("--master", "-m", help="Master capability (keeps name and folder)")

        return parser


def main(argv: list[str] | None = None) -> int:
    cap = Capability(Path(__file__).resolve().parent)
    return CapabilityCli(cap).execute(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
