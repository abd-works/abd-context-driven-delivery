#!/usr/bin/env python3
"""Flag architecture-context.md files not linked from the central spec, or vice-versa.

The central architecture-specification.md is the index of every documented folder.
This scanner enforces a two-way match:

  1. Every architecture-context.md on disk MUST be linked from the central spec.
  2. Every link in the central spec that points at architecture-context.md MUST
     resolve to a file that actually exists.

Repo-root links (``/src/.../architecture-context.md``) resolve against the workspace
root; relative links resolve against the spec file's directory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Set

_ROOT = Path(__file__).resolve().parent.parent
_REPO = _ROOT.parent.parent.parent.parent
for _p in (
    _REPO / "common" / "scripts",
    _ROOT / "scanners",
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation  # noqa: E402
from scanner_bases.resources.scan_context import ScanFilesContext  # noqa: E402
from arch_spec_context import (  # noqa: E402
    build_arch_spec_context,
    CONTEXT_FILE_NAME,
    resolve_spec_link,
)

_LINK_RE = re.compile(r"\]\(([^)]+architecture-context\.md[^)]*)\)")


def _extract_linked_paths(text: str, spec_path: Path, workspace: Path) -> Dict[str, Path]:
    """Return {raw_link_target: resolved_absolute_path} for every context link in spec."""
    result: Dict[str, Path] = {}
    for m in _LINK_RE.finditer(text):
        raw = m.group(1).strip()
        if not raw.split("#")[0].strip():
            continue
        result[raw] = resolve_spec_link(raw, spec_path, workspace)
    return result


def _infer_workspace(central_spec: Path, context_files: List[Path]) -> Path:
    """Walk up from the central spec until all context files lie under the candidate."""
    candidate = central_spec.parent
    ctx_paths = [f for f in context_files if f.name == CONTEXT_FILE_NAME]
    while candidate != candidate.parent:
        if all(str(f.resolve()).startswith(str(candidate.resolve())) for f in ctx_paths):
            return candidate.resolve()
        candidate = candidate.parent
    return central_spec.parent.resolve()


class EveryDocumentedFolderReachableScanner(Scanner):

    def scan_with_context(self, context: ScanFilesContext) -> List[Dict]:
        violations: List[Dict] = []
        all_files = list(context.files.code_files)
        if not all_files:
            return violations

        central_spec: Path | None = None
        for f in all_files:
            if f.name == "architecture-specification.md":
                central_spec = f
                break

        if central_spec is None:
            violations.append(
                Violation(
                    rule=self.rule,
                    violation_message=(
                        "No architecture-specification.md found in the workspace. "
                        "Create the central spec and index every architecture-context.md under "
                        "the Package Context section."
                    ),
                    severity="warning",
                ).to_dict()
            )
            return violations

        workspace = getattr(context, "_workspace", None) or _infer_workspace(
            central_spec, all_files
        )
        spec_text = central_spec.read_text(encoding="utf-8")
        linked = _extract_linked_paths(spec_text, central_spec, workspace)
        linked_resolved: Set[Path] = set(linked.values())
        disk_files: Set[Path] = {
            f.resolve()
            for f in all_files
            if f.name == CONTEXT_FILE_NAME
        }

        for disk_path in sorted(disk_files):
            if disk_path not in linked_resolved:
                rel = _try_rel(disk_path, workspace)
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            f"architecture-context.md at '{rel}' exists on disk but is not "
                            f"linked from the central spec's Package Context section. "
                            f"Add an index entry so the folder is discoverable."
                        ),
                        location=str(disk_path),
                        severity="error",
                    ).to_dict()
                )

        for raw, resolved in sorted(linked.items(), key=lambda kv: str(kv[1])):
            if not resolved.is_file():
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            f"Central spec links to '{raw}' (resolves to '{resolved}') "
                            f"but that architecture-context.md does not exist on disk. "
                            f"Either create the file or remove the broken link."
                        ),
                        location=str(central_spec),
                        severity="error",
                    ).to_dict()
                )

        return violations


def _try_rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(
        execute_scan_with_workspace(
            EveryDocumentedFolderReachableScanner,
            "every-documented-folder-is-reachable-from-central-spec",
            build_arch_spec_context,
            skill_root=_ROOT,
        )
    )
