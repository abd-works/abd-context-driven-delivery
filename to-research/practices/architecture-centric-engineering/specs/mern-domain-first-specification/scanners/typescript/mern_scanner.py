"""Base scanner for MERN architecture compliance checks."""
from pathlib import Path
from typing import List, Dict, Any, Optional


class MERNScanner:
    """Base class for domain-first MERN architecture scanners."""

    def __init__(self, rule: str):
        self.rule = rule

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Override in subclasses. Returns list of violation dicts."""
        return []

    def _get_project_root(self, context: Dict[str, Any]) -> Optional[Path]:
        """Extract project root from context."""
        root = context.get('project_root')
        if root:
            return Path(root)
        return None

    def _find_domain_packages(self, project_root: Path) -> List[Path]:
        """Find all domain package directories under packages/.
        
        A domain package is a directory under packages/ that contains
        at least one of: shared/, client/, server/.
        Excludes app-server/ and app-client/ (composition roots).
        """
        packages_dir = project_root / 'packages'
        if not packages_dir.exists():
            return []

        excluded = {'app-server', 'app-client', 'node_modules'}
        domain_packages = []

        for child in packages_dir.iterdir():
            if not child.is_dir():
                continue
            if child.name in excluded or child.name.startswith('.'):
                continue
            # Check if it looks like a domain package
            has_tier = any(
                (child / tier).is_dir()
                for tier in ('shared', 'client', 'server')
            )
            if has_tier:
                domain_packages.append(child)

        return domain_packages

    def _find_tier_files(self, domain_path: Path, tier: str, pattern: str = '*.ts') -> List[Path]:
        """Find files matching a glob pattern within a specific tier of a domain package."""
        tier_dir = domain_path / tier
        if not tier_dir.exists():
            return []
        return list(tier_dir.glob(pattern))

    def _find_test_folders(self, project_root: Path) -> List[Path]:
        """Find all lowest-level sub-epic test folders under tests/."""
        tests_dir = project_root / 'tests'
        if not tests_dir.exists():
            return []

        sub_epic_folders = []
        for epic_dir in tests_dir.iterdir():
            if not epic_dir.is_dir() or epic_dir.name.startswith('.'):
                continue
            for sub_epic_dir in epic_dir.rglob('*'):
                if not sub_epic_dir.is_dir():
                    continue
                # A lowest-level sub-epic folder contains test files directly
                has_test_files = any(
                    f.name.endswith(('.test.ts', '.test.tsx', '.spec.ts'))
                    for f in sub_epic_dir.iterdir()
                    if f.is_file()
                )
                if has_test_files:
                    sub_epic_folders.append(sub_epic_dir)

        return sub_epic_folders

    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Safely read file content, returning None on failure."""
        try:
            return file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return None
