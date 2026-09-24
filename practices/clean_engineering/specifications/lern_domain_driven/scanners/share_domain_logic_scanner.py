"""Scanner: verify shared domain logic - Zod at both boundaries + HTTP hydration.

Uses tree-sitter TypeScript AST to check:
1. Domain core (``<domain>.ts``) defines the Zod schema once.
2. ``server.ts`` repository code imports/uses that schema via ``.parse()``.
3. ``client.tsx`` uses the same schema (``.parse()`` / ``.safeParse()``).
4. No duplicated schema definitions in server.ts or client.tsx.
5. HTTP boundary in client.tsx hydrates raw JSON into domain instances.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from lern_scanner_base import TypeScriptScanner, Violation

_ZOD_OBJECT_RE = re.compile(r"\bz\.(object|string|number|boolean|enum|array|union)\s*\(")
_PARSE_CALL_RE = re.compile(r"\.(safe)?[Pp]arse\s*\(")
_SAFE_PARSE_RE = re.compile(r"\.safeParse\s*\(")
_HYDRATE_RE = re.compile(
    r"new\s+[A-Z]\w+\s*\(|[A-Z]\w+\.(?:create|from\w*)\s*\(|\bto[A-Z]\w*\s*\("
)
_RAW_JSON_RETURN_RE = re.compile(
    r"return\s+(data|res|response|json)\.(items|data|results|records)\b"
    r"|return\s+(?:await\s+)?\w+\.json\s*\(\s*\)"
)


@dataclass
class _SchemaParseCheck:
    path: Path
    domain_name: str
    relative_name: str
    missing_schema: str
    missing_parse: str
    content: str
    has_parse: bool
    warning: bool = False


class ShareDomainLogicScanner(TypeScriptScanner):
    """AST checks: Zod schema shared across tiers + HTTP response hydration."""

    RULE = "share-domain-logic"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []

        for domain_path in self._find_domain_packages(root):
            violations += self._check_schema_in_core(domain_path)
            violations += self._check_server_uses_schema(domain_path)
            violations += self._check_client_uses_schema(domain_path)
            violations += self._check_no_duplicate_schemas(domain_path)
            violations += self._check_http_client_hydrates(domain_path)

        return violations

    def _check_schema_in_core(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        core = self._domain_core_file(domain_path)
        if core is None:
            return violations

        content = core.read_text(encoding="utf-8", errors="replace")
        if not _ZOD_OBJECT_RE.search(content) and "from 'zod'" not in content and 'from "zod"' not in content:
            violations.append(
                self.v(
                    f"Domain core '{core.name}' does not appear to use Zod "
                    "(no z.object/z.string/z.enum found). Define validation "
                    "schemas in the domain core so server.ts and client.tsx "
                    "can validate against the same schema.",
                    str(core),
                )
            )
        return violations

    def _check_server_uses_schema(self, domain_path: Path) -> List[Violation]:
        server = self._server_file(domain_path)
        if server is None:
            return []
        content = server.read_text(encoding="utf-8", errors="replace")
        return self._missing_schema_parse(
            _SchemaParseCheck(
                server,
                domain_path.name,
                "server.ts",
                (
                    f"Domain '{domain_path.name}/server.ts' does not reference the "
                    "Zod schema from the domain core. The repository must call "
                    "Schema.parse(doc) to validate raw database documents."
                ),
                (
                    f"Domain '{domain_path.name}/server.ts' references a schema "
                    "but never calls .parse() or .safeParse(). Call "
                    "Schema.parse(rawDoc) at the repository boundary."
                ),
                content,
                bool(_PARSE_CALL_RE.search(content)),
            )
        )

    def _check_client_uses_schema(self, domain_path: Path) -> List[Violation]:
        client = self._client_file(domain_path)
        if client is None:
            return []
        content = client.read_text(encoding="utf-8", errors="replace")
        return self._missing_schema_parse(
            _SchemaParseCheck(
                client,
                domain_path.name,
                "client.tsx",
                (
                    f"Domain '{domain_path.name}/client.tsx' does not reference the "
                    "Zod schema from the domain core. HTTP clients must validate "
                    "responses with the shared schema."
                ),
                (
                    f"Domain '{domain_path.name}/client.tsx' references a schema but "
                    "never calls .parse() or .safeParse()."
                ),
                content,
                bool(_PARSE_CALL_RE.search(content) or _SAFE_PARSE_RE.search(content)),
                warning=True,
            )
        )

    def _missing_schema_parse(self, check: _SchemaParseCheck) -> List[Violation]:
        has_schema_ref = bool(re.search(r"\b\w+Schema\b", check.content))
        severity = "warning" if check.warning else "error"
        if not has_schema_ref:
            return [self.v(check.missing_schema, str(check.path), severity=severity)]
        if check.has_parse:
            return []
        return [self.v(check.missing_parse, str(check.path), severity=severity)]

    def _check_no_duplicate_schemas(self, domain_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        for tier, getter in (("server", self._server_file), ("client", self._client_file)):
            path = getter(domain_path)
            if path is None:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            if _ZOD_OBJECT_RE.search(content):
                violations.append(
                    self.v(
                        f"Zod schema definition found in '{domain_path.name}/{path.name}'. "
                        "Schemas must live exclusively in the domain core "
                        f"({domain_path.name}.ts) - import them instead of redefining.",
                        str(path),
                    )
                )
        return violations

    def _check_http_client_hydrates(self, domain_path: Path) -> List[Violation]:
        client = self._client_file(domain_path)
        if client is None:
            return []
        content = client.read_text(encoding="utf-8", errors="replace")
        if "fetch(" not in content and "axios." not in content:
            return []
        if _HYDRATE_RE.search(content):
            return []
        line_num = self._first_raw_json_return(content)
        if line_num is None:
            return []
        return [
            self.v(
                f"HTTP client in '{client.name}' returns raw JSON without "
                "hydrating into domain instances. Call toDomainEntity(raw) "
                "or new DomainClass(raw) — plain objects don't have domain "
                "methods and crash at runtime.",
                str(client),
                line_num,
            )
        ]

    def _first_raw_json_return(self, content: str) -> int | None:
        for line_num, line in enumerate(content.splitlines(), 1):
            if _RAW_JSON_RETURN_RE.search(line.strip()):
                return line_num
        return None
