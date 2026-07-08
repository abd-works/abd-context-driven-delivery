# generated-using: @capability/{capability}/{capability}.py
"""{capability} — {one sentence description}."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_CDD_CAP = Path(__file__).resolve().parents[1] / "capability" / "capability.py"
_spec = importlib.util.spec_from_file_location("_capability_impl", _CDD_CAP)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["_capability_impl"] = _mod
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
_BaseCli = _mod.CapabilityCli


class {Capability}:
    """{capability} logic."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def {action_one}(self) -> None:
        raise NotImplementedError

    def {action_two}(self) -> None:
        raise NotImplementedError


class {Capability}Cli(_BaseCli):
    """{capability} CLI — thin shim over {Capability}."""

    def __init__(self, capability: Capability) -> None:
        super().__init__(capability)
        self._impl = {Capability}(capability.path)

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == "{action-one}":
            self._impl.{action_one}()
            return 0

        if args.command == "{action-two}":
            self._impl.{action_two}()
            return 0

        return super()._dispatch(args, parser)

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]
        sub.add_parser("{action-one}", help="{Describe action one}")
        sub.add_parser("{action-two}", help="{Describe action two}")
        return parser


def main(argv: list[str] | None = None) -> int:
    cap = Capability(Path(__file__).resolve().parent)
    return {Capability}Cli(cap).execute(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
