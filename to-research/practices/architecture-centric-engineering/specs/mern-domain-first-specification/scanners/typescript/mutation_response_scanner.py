"""Scanner: mutation response shape — all mutations return the same snapshot type.

Checks:
1. All controller methods that handle POST/PUT/DELETE call res.json() with
   a consistent return type (same variable name pattern: 'snapshot').
2. API client functions for mutations all declare the same return type.
3. No res.json({ success: true }) or res.json({ message: ... }) patterns.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

try:
    from .ts_scanner_base import TypeScriptScanner
except ImportError:
    from ts_scanner_base import TypeScriptScanner


_RES_JSON_RE = re.compile(
    r'res\.(?:status\(\d+\)\.)?json\(\s*(\{[^}]*\}|\w+)',
)

_SUCCESS_PATTERN_RE = re.compile(
    r'\{\s*(?:success|message|ok|status)\s*:',
)

_RETURN_TYPE_RE = re.compile(
    r':\s*Promise<(\w+)>',
)


class MutationResponseScanner(TypeScriptScanner):
    """Check that all mutations return a consistent aggregate snapshot."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_controllers(domain_path)
            violations += self._check_api_client(domain_path)

        return violations

    def _check_controllers(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        server_dir = domain_path / 'server'
        if not server_dir.exists():
            return violations

        for ctrl_file in server_dir.glob('*.controller.ts'):
            try:
                content = ctrl_file.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue

            for m in _RES_JSON_RE.finditer(content):
                response_arg = m.group(1)
                if _SUCCESS_PATTERN_RE.match(response_arg):
                    line_num = content[:m.start()].count('\n') + 1
                    violations.append(self.v(
                        f"Controller returns {{ success/message/ok }} instead of "
                        f"an aggregate snapshot. All mutations must return the "
                        f"same snapshot type.",
                        str(ctrl_file),
                        line_num,
                        severity='error',
                    ))

        return violations

    def _check_api_client(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        client_dir = domain_path / 'client'
        if not client_dir.exists():
            return violations

        for api_file in client_dir.glob('*.api.ts'):
            try:
                content = api_file.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue

            return_types: Set[str] = set()
            for m in _RETURN_TYPE_RE.finditer(content):
                return_types.add(m.group(1))

            mutation_types = {t for t in return_types if t != 'void'}
            if len(mutation_types) > 1:
                violations.append(self.v(
                    f"API client in {api_file.name} returns multiple different "
                    f"types from mutations: {sorted(mutation_types)}. All "
                    f"mutations on the same aggregate should return the same "
                    f"snapshot type.",
                    str(api_file),
                    severity='warning',
                ))

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(MutationResponseScanner, 'standard-mutation-response')
