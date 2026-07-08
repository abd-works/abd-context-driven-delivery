"""{capability} — {one sentence description}."""
from __future__ import annotations

import argparse
from pathlib import Path


class CapabilityCli:
    """CLI template for capability API surfaces."""

    def __init__(self, capability_root: Path) -> None:
        self.capability_root = capability_root.resolve()

    def execute(self, argv: list[str]) -> int:
        parser = _build_parser()
        args = parser.parse_args(argv)

        if args.command == "{action-one}":
            self._action_one()
            return 0

        if args.command == "{action-two}":
            self._action_two()
            return 0

        parser.error(f"unknown command: {args.command}")
        return 2

    def _action_one(self) -> None:
        raise NotImplementedError

    def _action_two(self) -> None:
        raise NotImplementedError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="{capability} capability CLI")
    parser.add_argument("command", choices=("{action-one}", "{action-two}"))
    return parser


def main(argv: list[str] | None = None) -> int:
    cli = CapabilityCli(Path(__file__).resolve().parent)
    return cli.execute(argv or [])


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
