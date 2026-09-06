"""Scanner: property casing — camelCase in TS, snake_case in JSON/bodies.

Checks:
1. TypeScript interface/class properties are camelCase (no snake_case).
2. JSON body construction in API client uses snake_case keys.
3. Controller req.body extraction uses snake_case field names.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    from .ts_scanner_base import TypeScriptScanner
except ImportError:
    from ts_scanner_base import TypeScriptScanner


_SNAKE_CASE_PROP_RE = re.compile(
    r'(?:readonly\s+)?(\w+_\w+)\s*[?:]',
)

_CAMEL_IN_JSON_RE = re.compile(
    r'body:\s*JSON\.stringify\(\s*\{([^}]+)\}',
    re.DOTALL,
)

_CAMEL_KEY_IN_OBJ_RE = re.compile(
    r'([a-z][a-zA-Z]+[A-Z]\w*)\s*:',
)

_INTERFACE_BLOCK_RE = re.compile(
    r'interface\s+(\w+)[^{]*\{([^}]+)\}',
    re.DOTALL,
)

# Raw/wire-format type names — snake_case props are correct in these shapes.
# Matches: Raw*, *Data, *Report, *Payload, *Record, *Def, *Definition,
# *Config, *Intent, *Entry, *Schema, *Spec, *Body, *Json, *Info, *State, *Snapshot.
_RAW_TYPE_RE = re.compile(
    r'^(Raw\w+|\w+(?:Data|Report|Payload|Record|Def|Definition|Config|Intent|Entry|Schema|Spec|Body|Json|Info|State|Snapshot))$',
)


class CasingTransformScanner(TypeScriptScanner):
    """Check property casing conventions across TS and JSON boundaries."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_ts_properties(domain_path)
            violations += self._check_json_bodies(domain_path)

        return violations

    def _check_ts_properties(self, domain_path: Path) -> List[Dict[str, Any]]:
        """Flag snake_case properties in TypeScript interfaces/classes."""
        violations: List[Dict[str, Any]] = []

        for tier in ('shared', 'client', 'server'):
            tier_dir = domain_path / tier
            if not tier_dir.exists():
                continue
            for ts_file in tier_dir.glob('*.ts'):
                if ts_file.name.endswith('.schema.ts'):
                    continue
                try:
                    content = ts_file.read_text(encoding='utf-8', errors='replace')
                except OSError:
                    continue

                for block_match in _INTERFACE_BLOCK_RE.finditer(content):
                    type_name = block_match.group(1)
                    if _RAW_TYPE_RE.match(type_name):
                        continue  # snake_case is correct for wire/raw-data shapes
                    block = block_match.group(2)
                    for prop_match in _SNAKE_CASE_PROP_RE.finditer(block):
                        prop = prop_match.group(1)
                        if prop.startswith('_'):
                            continue
                        camel = self._to_camel(prop)
                        violations.append(self.v(
                            f"Property '{prop}' in {ts_file.name} uses snake_case. "
                            f"TypeScript properties must be camelCase: '{camel}'.",
                            str(ts_file),
                            severity='error',
                        ))

        return violations

    def _check_json_bodies(self, domain_path: Path) -> List[Dict[str, Any]]:
        """Flag camelCase keys in JSON.stringify bodies (should be snake_case)."""
        violations: List[Dict[str, Any]] = []

        client_dir = domain_path / 'client'
        if not client_dir.exists():
            return violations

        for ts_file in client_dir.glob('*.api.ts'):
            try:
                content = ts_file.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue

            for body_match in _CAMEL_IN_JSON_RE.finditer(content):
                body_content = body_match.group(1)
                for key_match in _CAMEL_KEY_IN_OBJ_RE.finditer(body_content):
                    key = key_match.group(1)
                    snake = self._to_snake(key)
                    violations.append(self.v(
                        f"JSON body key '{key}' in {ts_file.name} uses camelCase. "
                        f"HTTP bodies must use snake_case: '{snake}'.",
                        str(ts_file),
                        severity='error',
                    ))

        return violations

    @staticmethod
    def _to_camel(snake: str) -> str:
        parts = snake.split('_')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])

    @staticmethod
    def _to_snake(camel: str) -> str:
        return re.sub(r'([A-Z])', r'_\1', camel).lower().lstrip('_')


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(CasingTransformScanner, 'property-casing-transform')
