"""Probe installed guidance instructions and actions."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

REPORT_HEADER_LINES = 4
"""The probe's summary lines, which carry its red, yellow, or green status."""


def main() -> int:
    args = _arguments()
    from harness.diagnostics.guidance_probe import GuidanceProbe
    from harness.installation.installer import Installer

    probe = GuidanceProbe.from_filter(Installer(repo=_REPO), args.guidance)
    report = "\n\n".join((probe.instructions(), probe.actions()))
    print(report)
    return 1 if _is_red(report) else 0


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run guidance diagnostics; writes diagnostics.json → guidance.",
    )
    parser.add_argument(
        "--guidance",
        action="append",
        default=None,
        help="Practice and fidelity slugs to filter probes.",
    )
    return parser.parse_args()


def _is_red(report: str) -> bool:
    return any(line.lstrip("!").startswith("red") for line in report.splitlines()[:REPORT_HEADER_LINES])


if __name__ == "__main__":
    raise SystemExit(main())
