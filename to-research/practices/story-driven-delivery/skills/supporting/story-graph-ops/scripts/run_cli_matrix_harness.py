"""Policy-aware CLI conversion matrix harness.

This harness validates two things:
1) Structural parity for every allowed conversion path.
2) Source-of-truth policy enforcement for blocked model->code paths.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.formats.code.java.java_story_map import JavaStoryMap
from src.formats.code.python.python_story_map import PythonStoryMap
from src.formats.code.typescript.typescript_story_map import TypeScriptStoryMap
from src.formats.diagram.drawio.drawio_story_map import DrawIOStoryMap
from src.formats.diagram.miro.miro_story_map import MiroStoryMap
from src.formats.document.json.json_story_map import JsonStoryMap
from src.formats.document.markdown.markdown_story_map import MarkdownStoryMap

PROTOCOLS = ["json", "markdown", "drawio", "miro", "typescript", "python", "java"]
CODE_PROTOCOLS = {"typescript", "python", "java"}
TEXT_EXT = {"json": ".json", "markdown": ".md", "drawio": ".drawio.xml", "miro": ".miro.json"}


def ext_for(protocol: str) -> str:
    return TEXT_EXT[protocol] if protocol in TEXT_EXT else ".tree.json"


def adapter_for(protocol: str):
    return {
        "json": JsonStoryMap(),
        "markdown": MarkdownStoryMap(),
        "drawio": DrawIOStoryMap(),
        "miro": MiroStoryMap(),
        "typescript": TypeScriptStoryMap(),
        "python": PythonStoryMap(),
        "java": JavaStoryMap(),
    }[protocol]


def read_external(path: Path, protocol: str):
    text = path.read_text(encoding="utf-8")
    return text if protocol in TEXT_EXT else json.loads(text)


def counts(story_map) -> Dict[str, int]:
    epic_count = len(story_map.epics)
    sub_epic_count = 0
    story_count = 0
    ac_count = 0

    def walk_sub_epics(sub_epics):
        nonlocal sub_epic_count, story_count, ac_count
        for sub_epic in sub_epics:
            sub_epic_count += 1
            story_count += len(sub_epic.stories)
            for story in sub_epic.stories:
                ac_count += len(story.acceptance_criteria)
            walk_sub_epics(sub_epic.sub_epics)

    for epic in story_map.epics:
        walk_sub_epics(epic.sub_epics)

    return {
        "epics": epic_count,
        "sub_epics": sub_epic_count,
        "stories": story_count,
        "acceptance_criteria": ac_count,
    }


def is_blocked_by_policy(from_protocol: str, to_protocol: str) -> bool:
    return to_protocol in CODE_PROTOCOLS and from_protocol not in CODE_PROTOCOLS


def main() -> int:
    source_root = Path(r"c:\dev\paradise-mobile\pml-my\docs\stories")
    out_root = Path(r"c:\dev\paradise-mobile\pml-domain\docs\sand-box")
    cli = PROJECT_ROOT / "src" / "cli" / "story_graph_cli.py"

    sources: List[tuple[str, Path]] = []
    sources.extend([("markdown", p) for p in sorted(source_root.rglob("*.md"))])
    sources.extend([("json", p) for p in sorted(source_root.rglob("*.json"))])

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = out_root / f"story-graph-cli-policy-matrix-{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, Any]] = []

    for src_protocol, src_path in sources:
        canonical = adapter_for(src_protocol).parse(read_external(src_path, src_protocol))
        source_counts = counts(canonical)

        for to_protocol in PROTOCOLS:
            out_file = run_dir / f"{src_path.stem}__{src_protocol}_to_{to_protocol}{ext_for(to_protocol)}"
            command = [
                "python",
                str(cli),
                "convert",
                "--from-protocol",
                src_protocol,
                "--to-protocol",
                to_protocol,
                "--input",
                str(src_path),
                "--output",
                str(out_file),
            ]
            proc = subprocess.run(command, capture_output=True, text=True)
            blocked = is_blocked_by_policy(src_protocol, to_protocol)
            ok = proc.returncode == 0

            target_counts = None
            counts_match = None
            if ok:
                parsed = adapter_for(to_protocol).parse(read_external(out_file, to_protocol))
                target_counts = counts(parsed)
                counts_match = target_counts == source_counts

            results.append(
                {
                    "source": str(src_path),
                    "from": src_protocol,
                    "to": to_protocol,
                    "blocked_by_policy": blocked,
                    "ok": ok,
                    "stderr": proc.stderr.strip(),
                    "source_counts": source_counts,
                    "target_counts": target_counts,
                    "counts_match": counts_match,
                }
            )

    report_path = run_dir / "policy-matrix-results.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    blocked_expected = [r for r in results if r["blocked_by_policy"]]
    blocked_pass = [r for r in blocked_expected if not r["ok"]]
    allowed = [r for r in results if not r["blocked_by_policy"]]
    allowed_fail = [r for r in allowed if not r["ok"]]
    allowed_mismatch = [r for r in allowed if r["ok"] and not r["counts_match"]]

    print(f"RUN_DIR={run_dir}")
    print(f"BLOCKED_EXPECTED={len(blocked_expected)} BLOCKED_PASS={len(blocked_pass)}")
    print(f"ALLOWED_TOTAL={len(allowed)} ALLOWED_FAIL={len(allowed_fail)}")
    print(f"ALLOWED_COUNT_MISMATCH={len(allowed_mismatch)}")

    if len(blocked_expected) != len(blocked_pass):
        return 2
    if allowed_fail or allowed_mismatch:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

