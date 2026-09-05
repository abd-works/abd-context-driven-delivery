"""Base scanner for domain-driven VS Code plugin architecture compliance checks."""
from pathlib import Path
from typing import List, Dict, Any, Optional


class PluginScanner:
    """Base class for VS Code plugin architecture scanners.

    Project root layout expected:
      src/
        <domain>/
          <domain>.ts             — domain entity + interface
          <domain>_server.ts      — server domain (persistence)
          view/
            <domain>_view.ts      — server view
            <domain>_client.ts    — client DOM adapter
            <Domain>.html
        engine/
          engine.ts
          base_view.ts
          view/
            engine_view.ts
            engine_client.ts
      test/
        <domain>/
          <domain>.test.ts
          <domain>_test.ts
          <domain>_view.test.ts
    """

    def __init__(self, rule: str):
        self.rule = rule

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Override in subclasses. Returns list of violation dicts."""
        return []

    def _get_project_root(self, context: Dict[str, Any]) -> Optional[Path]:
        root = context.get('project_root')
        if root:
            return Path(root)
        return None

    def _find_domain_roots(self, project_root: Path) -> List[Path]:
        """Find domain root directories under src/.

        A domain root is any directory under src/ that contains
        a <name>.ts file (the domain entity) at its top level.
        Excludes 'engine' (infrastructure) and hidden directories.
        """
        src_dir = project_root / 'src'
        if not src_dir.exists():
            return []

        excluded = {'engine', 'node_modules'}
        roots = []

        for child in src_dir.iterdir():
            if not child.is_dir():
                continue
            if child.name in excluded or child.name.startswith('.'):
                continue
            # A domain root has its entity file named after the folder
            if (child / f'{child.name}.ts').exists():
                roots.append(child)

        return roots

    def _find_domain_files(self, domain_path: Path, pattern: str = '*.ts') -> List[Path]:
        """Find TypeScript files in a domain root (top level and view/)."""
        files = list(domain_path.glob(pattern))
        view_dir = domain_path / 'view'
        if view_dir.exists():
            files.extend(view_dir.glob(pattern))
        return files

    def _read_file_content(self, file_path: Path) -> Optional[str]:
        try:
            return file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return None
