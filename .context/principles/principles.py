"""principles - manage guiding principles and their examples."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import CapabilityCli and Capability from capability
# ---------------------------------------------------------------------------
_CDD_CAP = Path(__file__).resolve().parents[1] / "capability" / "capability.py"
_spec = importlib.util.spec_from_file_location("capability", _CDD_CAP)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("capability", _mod)
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
_BaseCli = _mod.CapabilityCli

_PRINCIPLES_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class CapabilityCli(_BaseCli):
    """principles capability CLI."""

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == "add-principle":
            return self._add_principle(args)
        if args.command == "add-example":
            return self._add_example(args)
        return super()._dispatch(args, parser)

    def _add_principle(self, args: argparse.Namespace) -> int:
        name = args.name.lower().replace(" ", "-")
        description = args.description
        path = _PRINCIPLES_DIR / f"{name}.md"
        if path.exists():
            print(f"principle already exists: {path.name}", file=sys.stderr)
            return 1
        path.write_text(
            f"{description}\n",
            encoding="utf-8",
        )
        print(f"created: {path.relative_to(_PRINCIPLES_DIR.parent)}")
        return 0

    def _add_example(self, args: argparse.Namespace) -> int:
        name = args.principle.lower().replace(" ", "-")
        path = _PRINCIPLES_DIR / f"{name}.md"
        if not path.exists():
            print(f"principle not found: {name}.md", file=sys.stderr)
            return 1
        current = path.read_text(encoding="utf-8")
        example_block = f"\n**Example:** {args.example}\n"
        if "## Examples" not in current:
            current = current.rstrip("\n") + "\n\n## Examples\n" + example_block
        else:
            current = current.rstrip("\n") + "\n" + example_block
        path.write_text(current, encoding="utf-8")
        print(f"added example to: {path.name}")
        return 0

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]

        ap = sub.add_parser("add-principle", help="Create a new principle file")
        ap.add_argument("name", help="Principle name (kebab-case)")
        ap.add_argument("description", help="One-line description")

        ae = sub.add_parser("add-example", help="Append an example to a principle")
        ae.add_argument("principle", help="Principle name")
        ae.add_argument("example", help="Example text")

        return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    cap = Capability(_PRINCIPLES_DIR)
    return CapabilityCli(cap).execute(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
