"""Probe installed guidance instructions and actions."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run guidance diagnostics; writes diagnostics.json → guidance.",
    )
    parser.add_argument(
        "--guidance",
        action="append",
        default=None,
        help="Practice and fidelity slugs to filter probes.",
    )
    args = parser.parse_args()
    from harness.guidance.guidance import probe_guidance_actions, probe_guidance_instructions
    from harness.installation.installer import Installer

    installer = Installer(repo=_REPO)
    instructions = probe_guidance_instructions(args.guidance, installer)
    actions = probe_guidance_actions(args.guidance, installer)
    report = "\n\n".join((instructions, actions))
    print(report)
    if any(line.lstrip("!").startswith("red") for line in report.splitlines()[:4]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
