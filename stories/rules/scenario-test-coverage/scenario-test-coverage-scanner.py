"""scenario-test-coverage — every scenario in a stories file has a describe block.

For each *-stories.ts (or *_stories.py) file found under tests/, extracts each
scenario's name string and checks that at least one sibling *.test.(ts|tsx|js)
(or test_*_*.py) file in the same directory contains a describe() / test class
that references that scenario name.

This closes the spec-to-test loop: the stories file is the contract; the test
file must honour every scenario defined in that contract.

Failure smells:
- Agent scaffolded the tier class but only wrote describe blocks for mainFlow.
- Agent added a new scenario to the stories file but forgot to add the test.
- Agent copy-pasted a describe block and left the old scenario name.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402

# --- stories file patterns ---

# Matches TS/JS/TSX stories files
_TS_STORIES_NAME = re.compile(r"[/\\]([a-z0-9-]+)-stories\.(?:ts|tsx|js)$")
_PY_STORIES_NAME = re.compile(r"[/\\]([a-z0-9_]+)_stories\.py$")

# Extract scenario keys (top-level keys that are not metadata)
_META_KEYS = frozenset({"story", "actor", "domainTerms", "evidence"})

# TS: `  scenarioKey: {` at indentation level 2
_TS_SCENARIO_KEY = re.compile(r"^  (\w+):\s*\{", re.MULTILINE)
# TS: `name: 'some scenario name'` (single or double quotes, or backtick)
_TS_SCENARIO_NAME = re.compile(r"name:\s*['\"`]([^'\"`\n]+)['\"`]")

# Python: SCENARIO_KEY = { 'name': '...' }
_PY_SCENARIO_KEY = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=\s*\{", re.MULTILINE)
_PY_SCENARIO_NAME = re.compile(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]")

# --- test file patterns ---

# TS describe call containing a scenario name string literal or property ref
_TS_DESCRIBE = re.compile(r"describe\s*\(")

# Python test class
_PY_TEST_CLASS = re.compile(r"^class\s+Test(\w+)\s*:", re.MULTILINE)


def _extract_ts_scenarios(text: str) -> List[Tuple[str, str]]:
    """Return [(key, name), ...] for each non-metadata scenario in a TS stories file."""
    results = []
    # Find positions of each top-level scenario key
    key_positions = list(_TS_SCENARIO_KEY.finditer(text))
    for i, km in enumerate(key_positions):
        key = km.group(1)
        if key in _META_KEYS:
            continue
        # Block: from this key to the next top-level key (or end)
        end = key_positions[i + 1].start() if i + 1 < len(key_positions) else len(text)
        block = text[km.start():end]
        name_m = _TS_SCENARIO_NAME.search(block)
        if name_m:
            results.append((key, name_m.group(1)))
    return results


def _extract_py_scenarios(text: str) -> List[Tuple[str, str]]:
    """Return [(key, name), ...] for each scenario constant in a Python stories file."""
    results = []
    key_positions = list(_PY_SCENARIO_KEY.finditer(text))
    for i, km in enumerate(key_positions):
        key = km.group(1)
        end = key_positions[i + 1].start() if i + 1 < len(key_positions) else len(text)
        block = text[km.start():end]
        name_m = _PY_SCENARIO_NAME.search(block)
        if name_m:
            results.append((key, name_m.group(1)))
    return results


def _test_files_in_dir(directory: Path, stories_suffix: str) -> List[Path]:
    """Return sibling test files for a stories file."""
    if stories_suffix in {".ts", ".tsx", ".js"}:
        return list(directory.glob("*.test.ts")) + list(directory.glob("*.test.tsx")) + list(directory.glob("*.test.js"))
    elif stories_suffix == ".py":
        return list(directory.glob("test_*.py"))
    return []


def _scenario_covered_ts(name: str, key: str, test_files: List[Path]) -> bool:
    """True if the scenario is referenced in a describe() call in any test file.

    Accepts two forms:
    1. Literal: describe('order accepted for a valid cart', ...)
    2. Property ref: describe(SubmitOrder.orderAccepted.name, ...)
    """
    key_ref = re.compile(re.escape(key) + r"\s*\.\s*name")
    for tf in test_files:
        text = tf.read_text(encoding="utf-8", errors="replace")
        for m in _TS_DESCRIBE.finditer(text):
            window = text[m.start(): m.start() + 300]
            if name in window:
                return True
            if key_ref.search(window):
                return True
    return False


def _scenario_covered_py(name: str, test_files: List[Path]) -> bool:
    """True if the scenario name appears in a test class or test method name."""
    slug = re.sub(r"[^a-z0-9]", "_", name.lower()).strip("_")
    for tf in test_files:
        text = tf.read_text(encoding="utf-8", errors="replace")
        if name in text:
            return True
        # Fuzzy: check slug fragment in class/method names
        if slug[:20] in text.lower():
            return True
    return False


class ScenarioTestCoverageScanner(ArtifactScanner):
    """Every scenario declared in a stories file has a describe block in the test file."""

    rule = "scenario-test-coverage"
    kind = "quality"
    reads = ("test_suites",)

    def scan(self) -> Iterator[Violation]:
        root = Path(self.workspace.root)

        # Walk workspace root for all stories files — they live alongside test files
        # but are not test suites themselves, so we scan the filesystem directly.
        for full in root.rglob("*"):
            if not full.is_file():
                continue
            rel = str(full.relative_to(root)).replace("\\", "/")

            ts_m = _TS_STORIES_NAME.search(rel)
            py_m = _PY_STORIES_NAME.search(rel)
            if not ts_m and not py_m:
                continue

            text = full.read_text(encoding="utf-8", errors="replace")
            directory = full.parent
            suffix = full.suffix

            if ts_m:
                scenarios = _extract_ts_scenarios(text)
                test_files = _test_files_in_dir(directory, suffix)
                if not test_files:
                    continue  # no test files yet — coverage scanner handles that
                for key, name in scenarios:
                    if not _scenario_covered_ts(name, key, test_files):
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario {key!r} ({name!r}) declared in "
                                f"{rel} has no describe() block in any sibling "
                                f"test file"
                            ),
                            location=rel,
                            severity="error",
                            hint=(
                                f"Add `describe(<Const>.{key}.name, () => {{ ... }})` "
                                f"to the sibling .test.ts file and wire all Given / "
                                f"When / Then steps explicitly."
                            ),
                        )

            elif py_m:
                scenarios = _extract_py_scenarios(text)
                test_files = _test_files_in_dir(directory, suffix)
                if not test_files:
                    continue
                for key, name in scenarios:
                    if not _scenario_covered_py(name, test_files):
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario {key!r} ({name!r}) declared in "
                                f"{rel} has no test method in any sibling "
                                f"test file"
                            ),
                            location=rel,
                            severity="error",
                            hint=(
                                f"Add a `class Test{key}` or `def test_{key.lower()}` "
                                f"method to the sibling test_*.py file with explicit "
                                f"Given / When / Then step calls."
                            ),
                        )


if __name__ == "__main__":
    sys.exit(run(ScenarioTestCoverageScanner))
