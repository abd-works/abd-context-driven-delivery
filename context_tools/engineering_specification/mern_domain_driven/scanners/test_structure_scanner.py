"""Scanner: verify story-driven test structure.

Checks that each lowest-level sub-epic folder under tests/ contains:
- All 3 tier test files: *_server.test.ts, *_client.test.tsx, *_e2e.spec.ts
- A helpers/ directory with base, server, client, and e2e helper files
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from mern_scanner_base import MERNScanner
from utilities.scanners.violation import Violation


class TestStructureScanner(MERNScanner):
    """Checks that test folders follow the story-driven 3-tier pattern."""

    RULE = "test-story-driven"

    REQUIRED_TIER_SUFFIXES = {
        "server test": "_server.test.ts",
        "client test": "_client.test.tsx",
        "e2e test": "_e2e.spec.ts",
    }

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        sub_epic_folders = self._find_test_folders(root)

        for folder in sub_epic_folders:
            sub_epic_name = folder.name

            for tier_name, suffix in self.REQUIRED_TIER_SUFFIXES.items():
                matching = [f for f in folder.iterdir() if f.is_file() and f.name.endswith(suffix)]
                if not matching:
                    violations.append(
                        self.v(
                            f"Sub-epic '{sub_epic_name}/' is missing a "
                            f"{tier_name} file (expected: *{suffix}).",
                            str(folder),
                        )
                    )

            helpers_dir = folder / "helpers"
            if not helpers_dir.exists():
                violations.append(
                    self.v(
                        f"Sub-epic '{sub_epic_name}/' is missing the "
                        "'helpers/' directory for shared test helpers.",
                        str(folder),
                    )
                )
            else:
                violations.extend(self._check_helper_files(helpers_dir, sub_epic_name))

        return violations

    def _check_helper_files(self, helpers_dir: Path, sub_epic_name: str) -> List[Violation]:
        """Check that helper directory contains required helper files."""
        violations: List[Violation] = []
        required_suffixes = {
            "base helper": [".base.ts"],
            "server helper": [".server.ts"],
            "client helper": [".client.ts", ".client.tsx"],
            "e2e helper": [".e2e.ts"],
        }

        for helper_name, suffixes in required_suffixes.items():
            matching = [
                f for f in helpers_dir.iterdir() if f.is_file() and any(f.name.endswith(s) for s in suffixes)
            ]
            if not matching:
                violations.append(
                    self.v(
                        f"Sub-epic '{sub_epic_name}/helpers/' is missing "
                        f"a {helper_name} file (expected: *{suffixes[0]}).",
                        str(helpers_dir),
                    )
                )

        return violations
