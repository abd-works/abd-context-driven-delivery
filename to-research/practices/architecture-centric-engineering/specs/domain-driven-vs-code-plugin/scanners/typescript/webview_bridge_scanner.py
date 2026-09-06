"""Scanner: verify webview bridge conventions.

Server view files (<domain>_view.ts) must:
- Import and extend BaseView
- Implement postMessage dispatch after mutations

engine_view.ts (top-level message dispatcher) must additionally:
- Declare a _lookup() method for routing commands to sub-views

Client files (<domain>_client.ts) must:
- Import the domain class (not just the interface)
- Not call acquireVsCodeApi() more than once
"""
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from .plugin_scanner import PluginScanner
except ImportError:
    from plugin_scanner import PluginScanner


class WebviewBridgeScanner(PluginScanner):
    """Checks webview bridge conventions in server view and client files."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        # Check engine_view.ts specifically for _lookup (top-level dispatcher)
        src_dir = project_root / 'src'
        engine_view = src_dir / 'engine' / 'view' / 'engine_view.ts'
        if engine_view.exists():
            violations.extend(self._check_engine_view(engine_view))

        # Check domain server views and clients
        domain_roots = self._find_domain_roots(project_root)
        for domain_path in domain_roots:
            view_dir = domain_path / 'view'
            if not view_dir.exists():
                continue

            view_file = view_dir / f'{domain_path.name}_view.ts'
            if view_file.exists():
                violations.extend(
                    self._check_server_view(view_file, domain_path.name)
                )

            client_file = view_dir / f'{domain_path.name}_client.ts'
            if client_file.exists():
                violations.extend(
                    self._check_client(client_file, domain_path.name)
                )

        return violations

    def _check_engine_view(self, file_path: Path) -> List[Dict[str, Any]]:
        """engine_view.ts: must extend BaseView and have _lookup() for command routing."""
        violations = []
        content = self._read_file_content(file_path)
        if content is None:
            return violations

        if not re.search(r'extends\s+BaseView\b', content):
            violations.append({
                'rule': self.rule,
                'message': (
                    "engine_view.ts does not extend BaseView. "
                    "The engine view must extend BaseView for template rendering."
                ),
                'location': str(file_path),
                'line': 0,
            })

        if not re.search(r'_lookup\s*\(', content):
            violations.append({
                'rule': self.rule,
                'message': (
                    "engine_view.ts has no _lookup() method. "
                    "The engine view must implement _lookup() to route "
                    "postMessage commands to the correct sub-view."
                ),
                'location': str(file_path),
                'line': 0,
            })

        return violations

    def _check_server_view(
        self, file_path: Path, domain_name: str
    ) -> List[Dict[str, Any]]:
        """Domain server view: must extend BaseView and call postMessage after mutations."""
        violations = []
        content = self._read_file_content(file_path)
        if content is None:
            return violations

        if not re.search(r'extends\s+BaseView\b', content):
            violations.append({
                'rule': self.rule,
                'message': (
                    f"'{domain_name}_view.ts' does not extend BaseView. "
                    "Server views must extend BaseView for template rendering."
                ),
                'location': str(file_path),
                'line': 0,
            })

        if not re.search(r'postMessage\s*\(', content):
            violations.append({
                'rule': self.rule,
                'message': (
                    f"'{domain_name}_view.ts' never calls postMessage. "
                    "Server views must dispatch state to the webview after mutations."
                ),
                'location': str(file_path),
                'line': 0,
            })

        return violations

    def _check_client(
        self, file_path: Path, domain_name: str
    ) -> List[Dict[str, Any]]:
        """Client DOM adapter: must import domain class; acquireVsCodeApi called once."""
        violations = []
        content = self._read_file_content(file_path)
        if content is None:
            return violations

        domain_class = domain_name.capitalize()

        import_pattern = rf"import\s+\{{[^}}]*\b{domain_class}\b[^}}]*\}}"
        if not re.search(import_pattern, content):
            violations.append({
                'rule': self.rule,
                'message': (
                    f"'{domain_name}_client.ts' does not import '{domain_class}'. "
                    "The client must bundle and use the same domain class as the server."
                ),
                'location': str(file_path),
                'line': 0,
            })

        acquire_count = len(re.findall(r'acquireVsCodeApi\s*\(', content))
        if acquire_count > 1:
            violations.append({
                'rule': self.rule,
                'message': (
                    f"'{domain_name}_client.ts' calls acquireVsCodeApi() "
                    f"{acquire_count} times. "
                    "It must be called exactly once and the result cached."
                ),
                'location': str(file_path),
                'line': 0,
            })

        return violations


if __name__ == '__main__':
    import sys
    context = {'project_root': sys.argv[1] if len(sys.argv) > 1 else '.'}
    scanner = WebviewBridgeScanner('server-view-extends-base-view')
    violations = scanner.scan(context)
    if violations:
        for v in violations:
            print(f"VIOLATION [{v['rule']}] {v['location']}:{v['line']}: {v['message']}")
        sys.exit(1)
    else:
        print("OK -- webview bridge conventions are valid")
