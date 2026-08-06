"""Scanner: property casing - camelCase in TS, snake_case in JSON/bodies.

Checks:
1. TypeScript interface/class properties are camelCase (no snake_case).
2. JSON body construction in the client HTTP boundary uses snake_case keys.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from mern_scanner_base import TypeScriptScanner
from utilities.scanners.violation import Violation

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

        for tier in ("shared", "client", "server"):
            for ts_file in self._find_tier_files(domain_path, tier):
                content = self._read_file_content(ts_file)
                if content is None:
                    continue

                for block_match in _INTERFACE_BLOCK_RE.finditer(content):
                    type_name = block_match.group(1)
                    if _RAW_TYPE_RE.match(type_name):
                        continue
                    block = block_match.group(2)
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
        violations: List[Violation] = []
        client = self._client_file(domain_path)
        if client is None:
            return violations

        content = self._read_file_content(client)
        if content is None:
            return violations

        for body_match in _CAMEL_IN_JSON_RE.finditer(content):
            body_content = body_match.group(1)
            for key_match in _CAMEL_KEY_IN_OBJ_RE.finditer(body_content):
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

    @staticmethod
    def _to_camel(snake: str) -> str:
        parts = snake.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    @staticmethod
    def _to_snake(camel: str) -> str:
        return re.sub(r"([A-Z])", r"_\1", camel).lower().lstrip("_")
