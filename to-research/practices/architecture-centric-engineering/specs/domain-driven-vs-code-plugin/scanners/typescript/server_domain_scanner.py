"""Scanner: verify server domain extends the domain entity.

Each <domain>_server.ts file must:
- Import the base domain class (not just the interface)
- Use `extends <Domain>` in the class declaration
- NOT wrap the domain class as a field (delegation pattern is forbidden)
"""
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from .plugin_scanner import PluginScanner
except ImportError:
    from plugin_scanner import PluginScanner


class ServerDomainScanner(PluginScanner):
    """Checks that server domain files extend (not wrap) the domain class."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        domain_roots = self._find_domain_roots(project_root)

        for domain_path in domain_roots:
            server_file = domain_path / f'{domain_path.name}_server.ts'
            if not server_file.exists():
                continue  # Pure domains without server extension are valid
            violations.extend(
                self._check_server_domain(server_file, domain_path.name)
            )

        return violations

    def _check_server_domain(
        self, file_path: Path, domain_name: str
    ) -> List[Dict[str, Any]]:
        violations = []
        content = self._read_file_content(file_path)
        if content is None:
            return violations

        domain_class = domain_name.capitalize()

        # Must extend the base domain class
        extends_pattern = rf'class\s+{domain_class}Server\s+extends\s+{domain_class}\b'
        if not re.search(extends_pattern, content):
            violations.append({
                'rule': self.rule,
                'message': (
                    f"'{domain_name}_server.ts' should declare "
                    f"'class {domain_class}Server extends {domain_class}' "
                    f"but no such declaration was found. "
                    f"Use inheritance, not composition."
                ),
                'location': str(file_path),
                'line': 0,
            })

        # Must NOT store the domain as a field (delegation anti-pattern)
        delegation_patterns = [
            rf'private\s+\w+\s*[:=].*\bnew\s+{domain_class}\b',
            rf'private\s+\w+:\s*I?{domain_class}\b',
        ]
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            for pattern in delegation_patterns:
                if re.search(pattern, line):
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"'{domain_name}_server.ts' stores '{domain_class}' "
                            f"as a field — use 'extends {domain_class}' instead: "
                            f"{line.strip()}"
                        ),
                        'location': str(file_path),
                        'line': line_num,
                    })
                    break

        return violations


if __name__ == '__main__':
    import sys
    context = {'project_root': sys.argv[1] if len(sys.argv) > 1 else '.'}
    scanner = ServerDomainScanner('server-domain-extends-domain')
    violations = scanner.scan(context)
    if violations:
        for v in violations:
            print(f"VIOLATION [{v['rule']}] {v['location']}:{v['line']}: {v['message']}")
        sys.exit(1)
    else:
        print("OK — server domain structure is valid")
