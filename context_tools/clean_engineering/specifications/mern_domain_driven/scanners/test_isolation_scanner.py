"""Scanner: verify test data isolation - no blanket resets.

Detects dangerous patterns that wipe all data instead of only
test-created data. Scans:
- Test files (tests/**) for blanket API reset calls or unfiltered deletes
- Server files (packages/**/*-server.ts, packages/**/app.ts) for blanket
  reset endpoints that accept no resource-specific filter

Violations include:
- deleteMany({}) with empty filter
- drop() / dropCollection() calls
- Endpoints named /test/reset or similar that wipe entire collections
- beforeAll/beforeEach/afterAll/afterEach hooks that call blanket reset APIs
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from mern_scanner_base import MERNScanner
from utilities.scanners.violation import Violation


class TestIsolationScanner(MERNScanner):
    """Checks that tests and server code never use blanket data resets."""

    RULE = "use-thorough-e2e-tests"

    # Patterns that indicate blanket deletion in TypeScript/JavaScript files
    BLANKET_DELETE_PATTERNS: List[Tuple[str, str]] = [
        (
            r"deleteMany\s*\(\s*\{\s*\}\s*\)",
            "deleteMany({}) with empty filter deletes ALL documents. "
            "Use a filter like { id: { $in: ids } } to delete only test-created data.",
        ),
        (
            r"\.drop\s*\(\s*\)",
            "Calling .drop() destroys the entire collection. "
            "Delete specific documents by ID instead.",
        ),
        (
            r"dropCollection\s*\(",
            "dropCollection() destroys the entire collection. "
            "Delete specific documents by ID instead.",
        ),
        (
            r"dropDatabase\s*\(",
            "dropDatabase() destroys the entire database. "
            "Delete specific documents by ID instead.",
        ),
    ]

    # Patterns in test files that indicate blanket reset API calls
    TEST_RESET_PATTERNS: List[Tuple[str, str]] = [
        (
            r"""(request|fetch|axios)\s*\.\s*(post|delete|get)\s*\(\s*['"`][^'"`]*\/test\/reset""",
            "Calling a blanket /test/reset endpoint wipes ALL data. "
            "Tests must only delete the specific resources they created.",
        ),
        (
            r"""(request|fetch|axios)\s*\.\s*(post|delete)\s*\(\s*['"`][^'"`]*\/reset['"`]""",
            "Calling a /reset endpoint wipes ALL data. "
            "Tests must only delete the specific resources they created.",
        ),
    ]

    # Server-side patterns: endpoints that accept no filter and wipe data
    SERVER_BLANKET_ENDPOINT_PATTERNS: List[Tuple[str, str]] = [
        (
            r"""(app|router)\s*\.\s*(post|delete|get)\s*\(\s*['"`][^'"`]*\/test\/reset""",
            "Blanket /test/reset endpoint wipes all data. "
            "Provide resource-specific delete endpoints that accept IDs: "
            "DELETE /api/test/{resource} with { ids: [...] } body.",
        ),
    ]

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        violations.extend(self._scan_test_files(root))
        violations.extend(self._scan_server_files(root))
        return violations

    def _scan_test_files(self, project_root: Path) -> List[Violation]:
        """Scan test files for blanket reset patterns."""
        violations: List[Violation] = []
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            return violations

        for ts_file in tests_dir.rglob("*.ts"):
            if ts_file.name.startswith("."):
                continue
            violations.extend(self._check_file(ts_file, self.BLANKET_DELETE_PATTERNS))
            violations.extend(self._check_file(ts_file, self.TEST_RESET_PATTERNS))

        for tsx_file in tests_dir.rglob("*.tsx"):
            if tsx_file.name.startswith("."):
                continue
            violations.extend(self._check_file(tsx_file, self.BLANKET_DELETE_PATTERNS))

        return violations

    def _scan_server_files(self, project_root: Path) -> List[Violation]:
        """Scan server-side files for blanket reset endpoints and deleteMany({})."""
        violations: List[Violation] = []
        packages_dir = project_root / "packages"
        if not packages_dir.exists():
            return violations

        for app_file in packages_dir.rglob("app.ts"):
            if "node_modules" in app_file.parts:
                continue
            violations.extend(self._check_file(app_file, self.BLANKET_DELETE_PATTERNS))
            violations.extend(self._check_file(app_file, self.SERVER_BLANKET_ENDPOINT_PATTERNS))

        for domain_pkg in self._find_domain_packages(project_root):
            server = self._server_file(domain_pkg)
            if server is None:
                continue
            violations.extend(self._check_file(server, self.BLANKET_DELETE_PATTERNS))

        return violations

    def _check_file(self, file_path: Path, patterns: List[Tuple[str, str]]) -> List[Violation]:
        """Check a single file against a list of regex patterns."""
        violations: List[Violation] = []
        content = self._read_file_content(file_path)
        if content is None:
            return violations

        lines = content.splitlines()
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue

            for pattern, message in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(self.v(message, str(file_path), line_num))

        return violations
