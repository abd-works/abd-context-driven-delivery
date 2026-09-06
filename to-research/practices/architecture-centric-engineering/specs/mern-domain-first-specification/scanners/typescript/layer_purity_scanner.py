"""Scanner: verify layer purity — no forbidden imports in shared/.

The shared/ package must contain only plain TypeScript and Zod.
It must NOT import Express, React, MongoDB, Mongoose, or any
infrastructure/framework library. server/ must not import from client/
and vice versa.
"""
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


class LayerPurityScanner(MERNScanner):
    """Checks that shared/ has no framework imports and tiers don't cross-import."""

    # Forbidden imports in shared/ tier
    FORBIDDEN_IN_SHARED = [
        r"from\s+['\"]express['\"]",
        r"from\s+['\"]react['\"]",
        r"from\s+['\"]react-dom['\"]",
        r"from\s+['\"]mongodb['\"]",
        r"from\s+['\"]mongoose['\"]",
        r"from\s+['\"]@tanstack",
        r"from\s+['\"]zustand['\"]",
        r"from\s+['\"]redux['\"]",
        r"from\s+['\"]@reduxjs",
        r"import\s+.*\s+from\s+['\"]express['\"]",
        r"import\s+.*\s+from\s+['\"]react['\"]",
        r"import\s+.*\s+from\s+['\"]mongodb['\"]",
        r"import\s+.*\s+from\s+['\"]mongoose['\"]",
        r"require\(['\"]express['\"]\)",
        r"require\(['\"]react['\"]\)",
        r"require\(['\"]mongodb['\"]\)",
        r"require\(['\"]mongoose['\"]\)",
    ]

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        domain_packages = self._find_domain_packages(project_root)

        for domain_path in domain_packages:
            domain_name = domain_path.name

            # Check shared/ for forbidden imports
            violations.extend(
                self._check_shared_purity(domain_path, domain_name)
            )

            # Check server/ doesn't import from client/
            violations.extend(
                self._check_no_cross_import(
                    domain_path, domain_name, 'server', 'client'
                )
            )

            # Check client/ doesn't import from server/
            violations.extend(
                self._check_no_cross_import(
                    domain_path, domain_name, 'client', 'server'
                )
            )

        return violations

    def _check_shared_purity(
        self, domain_path: Path, domain_name: str
    ) -> List[Dict[str, Any]]:
        """Check shared/ tier for forbidden framework imports."""
        violations = []
        shared_files = self._find_tier_files(domain_path, 'shared', '*.ts')
        shared_files.extend(self._find_tier_files(domain_path, 'shared', '*.tsx'))

        for file_path in shared_files:
            content = self._read_file_content(file_path)
            if content is None:
                continue

            lines = content.split('\n')
            for line_num, line in enumerate(lines, start=1):
                for pattern in self.FORBIDDEN_IN_SHARED:
                    if re.search(pattern, line):
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Domain '{domain_name}/shared/' has forbidden "
                                f"framework import: {line.strip()}"
                            ),
                            'location': str(file_path),
                            'line': line_num,
                        })
                        break  # One violation per line is enough

        return violations

    def _check_no_cross_import(
        self, domain_path: Path, domain_name: str,
        source_tier: str, forbidden_tier: str
    ) -> List[Dict[str, Any]]:
        """Check that source_tier doesn't import from forbidden_tier."""
        violations = []
        source_files = self._find_tier_files(domain_path, source_tier, '*.ts')
        source_files.extend(
            self._find_tier_files(domain_path, source_tier, '*.tsx')
        )

        # Pattern to detect imports from the forbidden tier's package
        cross_patterns = [
            rf"from\s+['\"].*/{forbidden_tier}['\"/]",
            rf"from\s+['\"]@project/{domain_name}/{forbidden_tier}['\"]",
            rf"from\s+['\"]\.\./\.\./{forbidden_tier}",
            rf"from\s+['\"]\.\.\/{forbidden_tier}",
        ]

        for file_path in source_files:
            content = self._read_file_content(file_path)
            if content is None:
                continue

            lines = content.split('\n')
            for line_num, line in enumerate(lines, start=1):
                for pattern in cross_patterns:
                    if re.search(pattern, line):
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Domain '{domain_name}/{source_tier}/' "
                                f"imports from '{forbidden_tier}/' — "
                                f"cross-tier import violation: {line.strip()}"
                            ),
                            'location': str(file_path),
                            'line': line_num,
                        })
                        break

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(LayerPurityScanner, 'maintain-layer-purity')
