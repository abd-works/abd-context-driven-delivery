"""Scanner: verify test data isolation — no blanket resets.

Detects dangerous patterns that wipe all data instead of only
test-created data. Scans:
- Test files (tests/**) for blanket API reset calls or unfiltered deletes
- Server files (packages/**/server/, packages/app-server/) for blanket
  reset endpoints that accept no resource-specific filter

Violations include:
- deleteMany({}) with empty filter
- drop() / dropCollection() calls
- Endpoints named /test/reset or similar that wipe entire collections
- beforeAll/beforeEach/afterAll/afterEach hooks that call blanket reset APIs
"""
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


class TestIsolationScanner(MERNScanner):
    """Checks that tests and server code never use blanket data resets."""

    # Patterns that indicate blanket deletion in TypeScript/JavaScript files
    BLANKET_DELETE_PATTERNS = [
        # deleteMany with empty filter — the most common offender
        (
            r'deleteMany\s*\(\s*\{\s*\}\s*\)',
            'deleteMany({}) with empty filter deletes ALL documents. '
            'Use a filter like { id: { $in: ids } } to delete only test-created data.'
        ),
        # drop() on a collection
        (
            r'\.drop\s*\(\s*\)',
            'Calling .drop() destroys the entire collection. '
            'Delete specific documents by ID instead.'
        ),
        # dropCollection
        (
            r'dropCollection\s*\(',
            'dropCollection() destroys the entire collection. '
            'Delete specific documents by ID instead.'
        ),
        # dropDatabase
        (
            r'dropDatabase\s*\(',
            'dropDatabase() destroys the entire database. '
            'Delete specific documents by ID instead.'
        ),
    ]

    # Patterns in test files that indicate blanket reset API calls
    TEST_RESET_PATTERNS = [
        # POST/DELETE to a /test/reset endpoint
        (
            r"""(request|fetch|axios)\s*\.\s*(post|delete|get)\s*\(\s*['"`][^'"`]*\/test\/reset""",
            'Calling a blanket /test/reset endpoint wipes ALL data. '
            'Tests must only delete the specific resources they created.'
        ),
        # request.post('/api/reset') or similar
        (
            r"""(request|fetch|axios)\s*\.\s*(post|delete)\s*\(\s*['"`][^'"`]*\/reset['"`]""",
            'Calling a /reset endpoint wipes ALL data. '
            'Tests must only delete the specific resources they created.'
        ),
    ]

    # Server-side patterns: endpoints that accept no filter and wipe data
    SERVER_BLANKET_ENDPOINT_PATTERNS = [
        # Route handler for /test/reset
        (
            r"""(app|router)\s*\.\s*(post|delete|get)\s*\(\s*['"`][^'"`]*\/test\/reset""",
            'Blanket /test/reset endpoint wipes all data. '
            'Provide resource-specific delete endpoints that accept IDs: '
            'DELETE /api/test/{resource} with { ids: [...] } body.'
        ),
    ]

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        # Scan test files
        violations.extend(self._scan_test_files(project_root))

        # Scan server files (app-server + domain server tiers)
        violations.extend(self._scan_server_files(project_root))

        return violations

    def _scan_test_files(self, project_root: Path) -> List[Dict[str, Any]]:
        """Scan test files for blanket reset patterns."""
        violations = []
        tests_dir = project_root / 'tests'
        if not tests_dir.exists():
            return violations

        for ts_file in tests_dir.rglob('*.ts'):
            if ts_file.name.startswith('.'):
                continue
            violations.extend(
                self._check_file(ts_file, self.BLANKET_DELETE_PATTERNS)
            )
            violations.extend(
                self._check_file(ts_file, self.TEST_RESET_PATTERNS)
            )

        for tsx_file in tests_dir.rglob('*.tsx'):
            if tsx_file.name.startswith('.'):
                continue
            violations.extend(
                self._check_file(tsx_file, self.BLANKET_DELETE_PATTERNS)
            )

        return violations

    def _scan_server_files(self, project_root: Path) -> List[Dict[str, Any]]:
        """Scan server-side files for blanket reset endpoints and deleteMany({})."""
        violations = []
        packages_dir = project_root / 'packages'
        if not packages_dir.exists():
            return violations

        # Check app-server composition root
        app_server = packages_dir / 'app-server'
        if app_server.exists():
            for ts_file in app_server.rglob('*.ts'):
                if 'node_modules' in str(ts_file):
                    continue
                violations.extend(
                    self._check_file(ts_file, self.BLANKET_DELETE_PATTERNS)
                )
                violations.extend(
                    self._check_file(ts_file, self.SERVER_BLANKET_ENDPOINT_PATTERNS)
                )

        # Check domain server tiers
        for domain_pkg in self._find_domain_packages(project_root):
            server_dir = domain_pkg / 'server'
            if not server_dir.exists():
                continue
            for ts_file in server_dir.rglob('*.ts'):
                if 'node_modules' in str(ts_file):
                    continue
                violations.extend(
                    self._check_file(ts_file, self.BLANKET_DELETE_PATTERNS)
                )

        return violations

    def _check_file(
        self, file_path: Path, patterns: List[tuple]
    ) -> List[Dict[str, Any]]:
        """Check a single file against a list of regex patterns."""
        violations = []
        try:
            content = file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return violations

        lines = content.splitlines()
        for line_num, line in enumerate(lines, start=1):
            # Skip comment-only lines
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue

            for pattern, message in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        'rule': self.rule,
                        'message': message,
                        'location': str(file_path),
                        'line': line_num,
                    })

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(TestIsolationScanner, 'use-thorough-e2e-tests')
