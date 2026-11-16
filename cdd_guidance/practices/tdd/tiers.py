"""The test tiers a spec file's name puts it in, and what a unit spec may not reach."""
from __future__ import annotations

import re
from pathlib import PurePosixPath

# The suffixes that name each tier, longest first so a heavy or e2e spec is not read as unit.
TIER_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("e2e", "_e2e_spec.py"), ("e2e", "_agent_spec.py"), ("e2e", ".e2e.spec.ts"), ("e2e", ".agent.spec.ts"),
    ("heavy", "_heavy_spec.py"), ("heavy", ".heavy.spec.ts"),
    ("unit", "_story.test.py"), ("unit", "_story.test.ts"), ("unit", "_spec.py"), ("unit", ".spec.ts"),
    ("unit", ".spec.shared.ts"), ("unit", "Spec.java"),
)
# A story test's tier file, named `.story.<tier>.`: the server tier starts a real server and the Playwright tier drives
# a browser; the shared and domain tiers run in memory.
_STORY_TIERS = {"shared": "unit", "domain": "unit", "server": "heavy", "heavy": "heavy", "playwright": "e2e", "e2e": "e2e"}
# Code files a test lives in; a markdown or YAML file is no test file.
TEST_CODE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".java")
# Imports that reach a real resource: a process, the network, a browser. Python's import lines, then TypeScript's
# module names.
_REAL_RESOURCE = re.compile(
    r"^\s*(?:import|from)\s+(subprocess|socket|http\.client|urllib\.request|requests|playwright)\b"
    r"|^\s*import\b[^;\n]*?from\s+[\"'](?:node:)?(child_process|net|http|https|@playwright/test|playwright)[\"']",
    re.MULTILINE,
)


def tier_of(file: str) -> str | None:
    """The tier a spec file's name puts it in; none for a name no tier suffix ends."""
    name = PurePosixPath(file.replace("\\", "/")).name
    story_tier = re.search(r"\.story\.(\w+)\.", name)
    if story_tier:
        return _STORY_TIERS.get(story_tier.group(1), "unit")
    return next((tier for tier, suffix in TIER_SUFFIXES if name.endswith(suffix)), None)


def is_test_code(file: str) -> bool:
    """Whether file is code a test can live in."""
    return file.replace("\\", "/").endswith(TEST_CODE_SUFFIXES)


def real_resources_in(text: str) -> list[tuple[int, str]]:
    """Each line that imports a real resource, with the line's number and the module it imports."""
    return [
        (text.count("\n", 0, found.start()) + 1, found.group(1) or found.group(2)) for found in _REAL_RESOURCE.finditer(text)
    ]
