"""Scanner: property casing - camelCase in TS, snake_case in JSON/bodies.

Checks:
1. TypeScript interface/class properties are camelCase (no snake_case).
2. JSON body construction in the client HTTP boundary uses snake_case keys.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from lern_scanner_base import TypeScriptScanner, Violation

_SNAKE_CASE_PROP_RE = re.compile(r"(?:readonly\s+)?(\w+_\w+)\s*[?:]")
_CAMEL_IN_JSON_RE = re.compile(r"body:\s*JSON\.stringify\(\s*\{([^}]+)\}", re.DOTALL)
_CAMEL_KEY_IN_OBJ_RE = re.compile(r"([a-z][a-zA-Z]+[A-Z]\w*)\s*:")
_INTERFACE_BLOCK_RE = re.compile(r"interface\s+(\w+)[^{]*\{([^}]+)\}", re.DOTALL)

_RAW_TYPE_RE = re.compile(
    r"^(Raw\w+|\w+(?:Data|Report|Payload|Record|Def|Definition|Config|Intent|Entry|Schema|Spec|Body|Json|Info|State|Snapshot))$"
)


class CasingTransformScanner(TypeScriptScanner):
    """Check property casing conventions across TS and JSON boundaries."""

    RULE = "property-casing-transform"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []

        for domain_path in self._find_domain_packages(root):
            violations += self._check_ts_properties(domain_path)
            violations += self._check_json_bodies(domain_path)

        return violations

    def _check_ts_properties(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        for ts_file in self._domain_ts_files(domain_path):
            violations.extend(self._snake_case_properties_in(ts_file))
        return violations

    def _domain_ts_files(self, domain_path: Path):
        for tier in ("shared", "client", "server"):
            yield from self._find_tier_files(domain_path, tier)

    def _snake_case_properties_in(self, ts_file: Path) -> List[Violation]:
        content = self._read_file_content(ts_file)
        if content is None:
            return []
        violations: List[Violation] = []
        for block_match in _INTERFACE_BLOCK_RE.finditer(content):
            if _RAW_TYPE_RE.match(block_match.group(1)):
                continue
            violations.extend(self._snake_props_in_block(ts_file, block_match.group(2)))
        return violations

    def _snake_props_in_block(self, ts_file: Path, block: str) -> List[Violation]:
        violations: List[Violation] = []
        for prop_match in _SNAKE_CASE_PROP_RE.finditer(block):
            prop = prop_match.group(1)
            if prop.startswith("_"):
                continue
            camel = self._to_camel(prop)
            violations.append(
                self.v(
                    f"Property '{prop}' in {ts_file.name} uses snake_case. "
                    f"TypeScript properties must be camelCase: '{camel}'.",
                    str(ts_file),
                    severity="error",
                )
            )
        return violations

    def _check_json_bodies(self, domain_path: Path) -> List[Violation]:
        client = self._client_file(domain_path)
        if client is None:
            return []
        content = self._read_file_content(client)
        if content is None:
            return []
        return self._camel_keys_in_json_bodies(client, content)

    def _camel_keys_in_json_bodies(self, client: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        for body_match in _CAMEL_IN_JSON_RE.finditer(content):
            for key_match in _CAMEL_KEY_IN_OBJ_RE.finditer(body_match.group(1)):
                key = key_match.group(1)
                snake = self._to_snake(key)
                violations.append(
                    self.v(
                        f"JSON body key '{key}' in {client.name} uses camelCase. "
                        f"HTTP bodies must use snake_case: '{snake}'.",
                        str(client),
                        severity="error",
                    )
                )
        return violations

    def _to_camel(self, snake: str) -> str:
        parts = snake.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def _to_snake(self, camel: str) -> str:
        return re.sub(r"([A-Z])", r"_\1", camel).lower().lstrip("_")
