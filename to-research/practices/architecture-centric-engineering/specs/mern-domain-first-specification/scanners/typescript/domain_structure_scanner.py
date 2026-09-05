"""Scanner: verify domain-first package structure.

Checks that each domain module under packages/ contains the required
shared/, client/, and server/ tier directories, each with an index.ts
and package.json file.
"""
from pathlib import Path
from typing import List, Dict, Any

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


class DomainStructureScanner(MERNScanner):
    """Checks domain packages have the required shared/client/server structure."""

    REQUIRED_TIERS = ('shared', 'client', 'server')
    REQUIRED_FILES_PER_TIER = ('index.ts', 'package.json')

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        domain_packages = self._find_domain_packages(project_root)

        if not domain_packages:
            packages_dir = project_root / 'packages'
            if packages_dir.exists():
                violations.append({
                    'rule': self.rule,
                    'message': (
                        'No domain packages found under packages/. '
                        'Expected at least one domain folder with shared/, client/, server/ subdirs.'
                    ),
                    'location': str(packages_dir),
                    'line': 0,
                })
            return violations

        for domain_path in domain_packages:
            domain_name = domain_path.name

            # Check each required tier exists
            for tier in self.REQUIRED_TIERS:
                tier_dir = domain_path / tier
                if not tier_dir.exists():
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Domain '{domain_name}' is missing required "
                            f"'{tier}/' directory."
                        ),
                        'location': str(domain_path),
                        'line': 0,
                    })
                    continue

                # Check required files within the tier
                for required_file in self.REQUIRED_FILES_PER_TIER:
                    file_path = tier_dir / required_file
                    if not file_path.exists():
                        violations.append({
                            'rule': self.rule,
                            'message': (
                                f"Domain '{domain_name}/{tier}/' is missing "
                                f"required file '{required_file}'."
                            ),
                            'location': str(tier_dir),
                            'line': 0,
                        })

            # Check shared/ has at least one schema or entity file
            shared_dir = domain_path / 'shared'
            if shared_dir.exists():
                ts_files = list(shared_dir.glob('*.ts'))
                non_index_files = [f for f in ts_files if f.name != 'index.ts']
                if not non_index_files:
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Domain '{domain_name}/shared/' has no domain "
                            f"entity or schema files. Expected at least one "
                            f".ts file (entity, value object, or schema)."
                        ),
                        'location': str(shared_dir),
                        'line': 0,
                    })

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(DomainStructureScanner, 'organize-by-domain-module')
