"""Scanner: verify naming conventions for each tier.

Checks that:
- server/ contains: *.routes.ts, *.controller.ts, *.service.ts, *.repository.ts
- client/ contains: *.api.ts, use*.ts (hook), *.tsx (component)
- shared/ contains: *.schema.ts or domain entity .ts files
"""
from pathlib import Path
from typing import List, Dict, Any, Set

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


class NamingConventionScanner(MERNScanner):
    """Checks that each tier follows the expected file naming conventions."""

    # Required file patterns per tier (at least one file matching each pattern)
    SERVER_REQUIRED_PATTERNS = {
        'routes': '*.routes.ts',
        'controller': '*.controller.ts',
        'service': '*.service.ts',
        'repository': '*.repository.ts',
    }

    CLIENT_REQUIRED_PATTERNS = {
        'api client': '*.api.ts',
        'hook': 'use*.ts',
        'component': '*.tsx',
    }

    SHARED_REQUIRED_PATTERNS = {
        'schema': '*.schema.ts',
    }

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        domain_packages = self._find_domain_packages(project_root)

        for domain_path in domain_packages:
            domain_name = domain_path.name

            # Check server/ naming conventions
            violations.extend(
                self._check_tier_patterns(
                    domain_path, domain_name, 'server',
                    self.SERVER_REQUIRED_PATTERNS
                )
            )

            # Check client/ naming conventions
            violations.extend(
                self._check_tier_patterns(
                    domain_path, domain_name, 'client',
                    self.CLIENT_REQUIRED_PATTERNS
                )
            )

            # Check shared/ naming conventions
            violations.extend(
                self._check_tier_patterns(
                    domain_path, domain_name, 'shared',
                    self.SHARED_REQUIRED_PATTERNS
                )
            )

        return violations

    def _check_tier_patterns(
        self, domain_path: Path, domain_name: str,
        tier: str, required_patterns: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Check that at least one file matches each required pattern in a tier."""
        violations = []
        tier_dir = domain_path / tier

        if not tier_dir.exists():
            # Structure scanner handles missing tiers — skip here
            return violations

        for pattern_name, glob_pattern in required_patterns.items():
            matching_files = list(tier_dir.glob(glob_pattern))
            if not matching_files:
                violations.append({
                    'rule': self.rule,
                    'message': (
                        f"Domain '{domain_name}/{tier}/' is missing a "
                        f"{pattern_name} file (expected pattern: {glob_pattern})."
                    ),
                    'location': str(tier_dir),
                    'line': 0,
                })

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(NamingConventionScanner, 'use-domain-language')
