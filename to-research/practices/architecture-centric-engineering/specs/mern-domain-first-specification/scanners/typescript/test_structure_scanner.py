"""Scanner: verify story-driven test structure.

Checks that each lowest-level sub-epic folder under tests/ contains:
- All 3 tier test files: *_server.test.ts, *_client.test.tsx, *_e2e.spec.ts
- A helpers/ directory with base, server, client, and e2e helper files
"""
from pathlib import Path
from typing import List, Dict, Any

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


class TestStructureScanner(MERNScanner):
    """Checks that test folders follow the story-driven 3-tier pattern."""

    REQUIRED_TIER_SUFFIXES = {
        'server test': '_server.test.ts',
        'client test': '_client.test.tsx',
        'e2e test': '_e2e.spec.ts',
    }

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        sub_epic_folders = self._find_test_folders(project_root)

        for folder in sub_epic_folders:
            sub_epic_name = folder.name

            # Check for all 3 tier test files
            for tier_name, suffix in self.REQUIRED_TIER_SUFFIXES.items():
                matching = [
                    f for f in folder.iterdir()
                    if f.is_file() and f.name.endswith(suffix)
                ]
                if not matching:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Sub-epic '{sub_epic_name}/' is missing a "
                            f"{tier_name} file (expected: *{suffix})."
                        ),
                        'location': str(folder),
                        'line': 0,
                    })

            # Check for helpers/ directory
            helpers_dir = folder / 'helpers'
            if not helpers_dir.exists():
                violations.append({
                    'rule': self.rule,
                    'message': (
                        f"Sub-epic '{sub_epic_name}/' is missing the "
                        f"'helpers/' directory for shared test helpers."
                    ),
                    'location': str(folder),
                    'line': 0,
                })
            else:
                # Check for required helper files
                self._check_helper_files(
                    helpers_dir, sub_epic_name, violations
                )

        return violations

    def _check_helper_files(
        self, helpers_dir: Path, sub_epic_name: str,
        violations: List[Dict[str, Any]]
    ) -> None:
        """Check that helper directory contains required helper files."""
        required_suffixes = {
            'base helper': ['.base.ts'],
            'server helper': ['.server.ts'],
            'client helper': ['.client.ts', '.client.tsx'],
            'e2e helper': ['.e2e.ts'],
        }

        for helper_name, suffixes in required_suffixes.items():
            matching = [
                f for f in helpers_dir.iterdir()
                if f.is_file() and any(f.name.endswith(s) for s in suffixes)
            ]
            if not matching:
                violations.append({
                    'rule': self.rule,
                    'message': (
                        f"Sub-epic '{sub_epic_name}/helpers/' is missing "
                        f"a {helper_name} file (expected: *{suffixes[0]})."
                    ),
                    'location': str(helpers_dir),
                    'line': 0,
                })


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(TestStructureScanner, 'test-story-driven')
