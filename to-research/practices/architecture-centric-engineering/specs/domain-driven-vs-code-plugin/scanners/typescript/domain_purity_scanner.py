"""Scanner: verify domain layer purity.

Domain entity files (<domain>.ts) must not import vscode, Node built-ins
(fs, path, os), or DOM types. They must be plain TypeScript so they can
run in tests without any VS Code context.
"""
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from .plugin_scanner import PluginScanner
except ImportError:
    from plugin_scanner import PluginScanner


class DomainPurityScanner(PluginScanner):
    """Checks that domain entity files contain no platform imports."""

    FORBIDDEN_IN_DOMAIN = [
        # VS Code API
        r"from\s+['\"]vscode['\"]",
        r"require\(['\"]vscode['\"]\)",
        r"import\s+\*\s+as\s+vscode",
        # Node.js built-ins
        r"from\s+['\"]fs['\"]",
        r"from\s+['\"]path['\"]",
        r"from\s+['\"]os['\"]",
        r"from\s+['\"]child_process['\"]",
        r"require\(['\"]fs['\"]\)",
        r"require\(['\"]path['\"]\)",
        r"require\(['\"]os['\"]\)",
        # DOM globals (import-style usage is rare, but guard against typed imports)
        r"from\s+['\"]@types/jsdom['\"]",
    ]

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        domain_roots = self._find_domain_roots(project_root)

        for domain_path in domain_roots:
            entity_file = domain_path / f'{domain_path.name}.ts'
            if not entity_file.exists():
                continue
            violations.extend(
                self._check_domain_purity(entity_file, domain_path.name)
            )

        return violations

    def _check_domain_purity(
        self, file_path: Path, domain_name: str
    ) -> List[Dict[str, Any]]:
        violations = []
        content = self._read_file_content(file_path)
        if content is None:
            return violations

        for line_num, line in enumerate(content.split('\n'), start=1):
            for pattern in self.FORBIDDEN_IN_DOMAIN:
                if re.search(pattern, line):
                    violations.append({
                        'rule': self.rule,
                        'message': (
                            f"Domain entity '{domain_name}/{domain_path.name}.ts' "
                            f"has forbidden platform import: {line.strip()}"
                        ).replace('domain_name', domain_name),
                        'location': str(file_path),
                        'line': line_num,
                    })
                    break
        return violations


if __name__ == '__main__':
    import sys
    import json
    context = {'project_root': sys.argv[1] if len(sys.argv) > 1 else '.'}
    scanner = DomainPurityScanner('domain-layer-has-no-platform-imports')
    violations = scanner.scan(context)
    if violations:
        for v in violations:
            print(f"VIOLATION [{v['rule']}] {v['location']}:{v['line']}: {v['message']}")
        sys.exit(1)
    else:
        print("OK — no domain purity violations")
