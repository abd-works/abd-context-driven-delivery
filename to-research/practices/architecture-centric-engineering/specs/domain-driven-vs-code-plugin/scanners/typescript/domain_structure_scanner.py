"""Scanner: verify domain-first folder structure.

Each domain root under src/ must have:
- A domain entity file: <domain>.ts
- A server extension file: <domain>_server.ts (or is a pure domain — warning if absent)
- A view/ subfolder containing <domain>_view.ts and <domain>_client.ts

The engine/ folder must contain engine.ts and base_view.ts.
"""
from pathlib import Path
from typing import List, Dict, Any

try:
    from .plugin_scanner import PluginScanner
except ImportError:
    from plugin_scanner import PluginScanner


class DomainStructureScanner(PluginScanner):
    """Checks domain-first folder structure for VS Code plugin projects."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        src_dir = project_root / 'src'
        if not src_dir.exists():
            violations.append({
                'rule': self.rule,
                'message': "No src/ directory found. Expected src/<domain>/ structure.",
                'location': str(project_root),
                'line': 0,
            })
            return violations

        # Check engine/ folder
        violations.extend(self._check_engine(src_dir))

        # Check domain roots
        domain_roots = self._find_domain_roots(project_root)
        if not domain_roots:
            violations.append({
                'rule': self.rule,
                'message': (
                    "No domain roots found under src/. "
                    "Expected at least one folder containing a <name>.ts entity file."
                ),
                'location': str(src_dir),
                'line': 0,
            })
            return violations

        for domain_path in domain_roots:
            violations.extend(self._check_domain_root(domain_path))

        return violations

    def _check_engine(self, src_dir: Path) -> List[Dict[str, Any]]:
        violations = []
        engine_dir = src_dir / 'engine'
        if not engine_dir.exists():
            violations.append({
                'rule': self.rule,
                'message': "Missing src/engine/ directory (composition root).",
                'location': str(src_dir),
                'line': 0,
            })
            return violations

        for required in ('engine.ts', 'base_view.ts'):
            if not (engine_dir / required).exists():
                violations.append({
                    'rule': self.rule,
                    'message': f"src/engine/ is missing required file '{required}'.",
                    'location': str(engine_dir),
                    'line': 0,
                })

        view_dir = engine_dir / 'view'
        if view_dir.exists():
            for required in ('engine_view.ts', 'engine_client.ts'):
                if not (view_dir / required).exists():
                    violations.append({
                        'rule': self.rule,
                        'message': f"src/engine/view/ is missing '{required}'.",
                        'location': str(view_dir),
                        'line': 0,
                    })

        return violations

    def _check_domain_root(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations = []
        name = domain_path.name

        # Domain entity must exist
        if not (domain_path / f'{name}.ts').exists():
            violations.append({
                'rule': self.rule,
                'message': f"Domain root '{name}/' is missing entity file '{name}.ts'.",
                'location': str(domain_path),
                'line': 0,
            })

        # Server extension — warning if absent (pure domains are valid)
        if not (domain_path / f'{name}_server.ts').exists():
            violations.append({
                'rule': self.rule,
                'message': (
                    f"Domain root '{name}/' has no server extension '{name}_server.ts'. "
                    "If persistence is not needed, this warning can be suppressed."
                ),
                'location': str(domain_path),
                'line': 0,
            })

        # view/ subfolder
        view_dir = domain_path / 'view'
        if not view_dir.exists():
            violations.append({
                'rule': self.rule,
                'message': f"Domain root '{name}/' is missing a view/ subfolder.",
                'location': str(domain_path),
                'line': 0,
            })
        else:
            for required in (f'{name}_view.ts', f'{name}_client.ts'):
                if not (view_dir / required).exists():
                    violations.append({
                        'rule': self.rule,
                        'message': f"Domain '{name}/view/' is missing required file '{required}'.",
                        'location': str(view_dir),
                        'line': 0,
                    })

        return violations


if __name__ == '__main__':
    import sys
    context = {'project_root': sys.argv[1] if len(sys.argv) > 1 else '.'}
    scanner = DomainStructureScanner('domain-root-owns-its-folder')
    violations = scanner.scan(context)
    if violations:
        for v in violations:
            print(f"VIOLATION [{v['rule']}] {v['location']}:{v['line']}: {v['message']}")
        sys.exit(1)
    else:
        print("OK — domain structure is valid")
