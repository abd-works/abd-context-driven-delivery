"""CLI adapter — parses argv, invokes the loader and Skill.assemble, prints JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ..assembly.fidelity import Fidelity, UnknownFidelityError
from ..assembly.phase import Phase, UnknownPhaseError
from .loader import load_skill


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assemble_components",
        description=(
            "Filter a skill package by fidelity + format + phase and emit a manifest "
            "of files for the AI to read. Anomalies (unknown fidelity, missing front "
            "matter, invalid YAML) are reported on stderr but never abort the run."
        ),
    )
    parser.add_argument("--skill-root", required=True,
                        help="Root of the skill package (contains concepts/, rules/, templates/, …).")
    parser.add_argument("--fidelity", required=True,
                        help="Comma-separated fidelity set, e.g. 'exploration,specification'.")
    parser.add_argument("--format", required=True,
                        help="Output format, e.g. md, ts, py.")
    parser.add_argument("--phase", required=True,
                        choices=[phase.value for phase in Phase],
                        help="Workflow phase: interview | generate | validate.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        fidelities = frozenset(
            Fidelity.parse(entry.strip())
            for entry in args.fidelity.split(",")
            if entry.strip()
        )
    except UnknownFidelityError as exc:
        _emit_error("unknown_fidelity_argument", {"value": exc.value})
        return 2

    if not fidelities:
        _emit_error("empty_fidelity_argument", {})
        return 2

    try:
        phase = Phase.parse(args.phase)
    except UnknownPhaseError as exc:
        _emit_error("unknown_phase_argument", {"value": exc.value})
        return 2

    skill_root = Path(args.skill_root)
    if not skill_root.is_dir():
        _emit_error("skill_root_not_found", {"path": str(skill_root)})
        return 2

    skill = load_skill(skill_root)
    manifest = skill.assemble(
        fidelities=fidelities,
        format=args.format,
        phase=phase,
    )

    manifest_dict = manifest.to_dict()
    json.dump(manifest_dict, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")

    anomalies_payload = None
    if manifest.anomalies:
        anomalies_payload = [anomaly.to_dict() for anomaly in manifest.anomalies]
        payload = {"anomalies": anomalies_payload}
        sys.stderr.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if not os.environ.get("STORIES_SKILL_TRACE"):
        try:
            from ..skill_trace import log_assemble

            log_assemble(manifest_dict, anomalies=anomalies_payload)
        except ImportError:
            pass

    return 0


def _emit_error(kind: str, details: dict) -> None:
    payload = {"error": {"kind": kind, "details": details}}
    sys.stderr.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
