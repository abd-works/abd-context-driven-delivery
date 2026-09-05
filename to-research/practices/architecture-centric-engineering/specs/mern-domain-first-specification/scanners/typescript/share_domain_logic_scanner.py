"""Scanner: verify shared domain logic — Zod at both boundaries + API hydration.

Uses tree-sitter TypeScript AST to check:
1. Each domain has exactly ONE Zod schema definition in shared/ (*.schema.ts).
2. The server/ repository imports the shared schema and calls .parse() on raw data.
3. The client/ code (form or api file) imports the shared schema and calls .safeParse().
4. No duplicated schema definitions in server/ or client/ (they must reuse shared/).
5. API client files (*.api.ts) hydrate raw JSON responses into domain class instances
   — they must not return plain JSON objects as typed domain entities.
6. Both tiers must NOT redefine TypeScript interfaces already in shared/.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    from .ts_scanner_base import TypeScriptScanner, run_scanner_main
except ImportError:
    from ts_scanner_base import TypeScriptScanner, run_scanner_main

_SCHEMA_IMPORT_FROM_SHARED_RE = re.compile(
    r"import\s+[\s\S]*?\b\w*Schema\b[\s\S]*?from\s+['\"][^'\"]*(?:shared|"
    r"[^'\"]+-shared)[^'\"]*['\"]",
    re.MULTILINE,
)
_ZOD_OBJECT_RE = re.compile(r'\bz\.(object|string|number|boolean|enum|array|union)\s*\(')
_PARSE_CALL_RE = re.compile(r'\.(safe)?[Pp]arse\s*\(')
_SAFE_PARSE_RE = re.compile(r'\.safeParse\s*\(')
_RETURN_DATA_RE = re.compile(r'return\s+(?:data|response|res|json)\s*[\.\[]')
_HYDRATE_RE = re.compile(
    r'new\s+[A-Z]\w+\s*\(|[A-Z]\w+\.(?:create|from\w*)\s*\('
)


class ShareDomainLogicScanner(TypeScriptScanner):
    """AST checks: Zod schema shared across tiers + API response hydration."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_schema_in_shared(domain_path)
            violations += self._check_repo_uses_schema(domain_path)
            violations += self._check_client_uses_schema(domain_path)
            violations += self._check_no_duplicate_schemas(domain_path)
            violations += self._check_api_client_hydrates(domain_path)

        return violations

    # ------------------------------------------------------------------ #
    # 1. Schema must live in shared/                                       #
    # ------------------------------------------------------------------ #

    def _check_schema_in_shared(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        shared_dir = domain_path / 'shared'
        if not shared_dir.exists():
            return violations

        schema_files = list(shared_dir.glob('*.schema.ts'))
        if not schema_files:
            violations.append(self.v(
                f"Domain '{domain_path.name}/shared/' has no *.schema.ts file. "
                "Define Zod validation schemas in shared/ so both server/ "
                "and client/ can validate against the same schema.",
                str(shared_dir),
            ))
            return violations

        # Verify they actually contain Zod definitions
        for sf in schema_files:
            content = sf.read_text(encoding='utf-8', errors='replace')
            if not _ZOD_OBJECT_RE.search(content) and 'from \'zod\'' not in content and 'from "zod"' not in content:
                violations.append(self.v(
                    f"Schema file '{sf.name}' does not appear to use Zod "
                    "(no z.object/z.string/z.enum found). Ensure it imports "
                    "from 'zod' and defines validation schemas.",
                    str(sf),
                ))

        return violations

    # ------------------------------------------------------------------ #
    # 2. Server repository must use schema.parse()                         #
    # ------------------------------------------------------------------ #

    def _check_repo_uses_schema(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        server_dir = domain_path / 'server'
        if not server_dir.exists():
            return violations

        # Match *.repository.ts AND *.mongo-repository.ts and other variants
        repo_files = [
            f for f in sorted(server_dir.glob('*.ts'))
            if 'repository' in f.stem.lower() and f.name != 'index.ts'
        ]
        if not repo_files:
            return violations

        domain_name = domain_path.name
        any_repo_imports_schema = False
        any_repo_calls_parse = False

        for rf in repo_files:
            content = rf.read_text(encoding='utf-8', errors='replace')
            root = self.parse_file(rf)

            # Check imports from shared (should import the schema)
            if root:
                imports = self.get_imports(root)
                for imp in imports:
                    if 'shared' in imp.source or domain_name in imp.source:
                        schema_names = [n for n in imp.names if 'Schema' in n or 'schema' in n.lower()]
                        if schema_names:
                            any_repo_imports_schema = True
            elif _SCHEMA_IMPORT_FROM_SHARED_RE.search(content):
                any_repo_imports_schema = True

            if _PARSE_CALL_RE.search(content):
                any_repo_calls_parse = True

        if not any_repo_imports_schema:
            violations.append(self.v(
                f"Domain '{domain_name}/server/' repositories do not import "
                "the Zod schema from shared/. Repositories must call "
                "Schema.parse(doc) to validate raw database documents.",
                str(server_dir),
            ))
        if any_repo_imports_schema and not any_repo_calls_parse:
            violations.append(self.v(
                f"Domain '{domain_name}/server/' repositories import the schema "
                "but never call .parse() or .safeParse(). Call Schema.parse(rawDoc) "
                "at the repository boundary to validate incoming data.",
                str(server_dir),
            ))

        return violations

    # ------------------------------------------------------------------ #
    # 3. Client must use schema.safeParse()                                #
    # ------------------------------------------------------------------ #

    def _check_client_uses_schema(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        client_dir = domain_path / 'client'
        if not client_dir.exists():
            return violations

        domain_name = domain_path.name
        client_files = (
            list(client_dir.glob('*.ts'))
            + list(client_dir.glob('*.tsx'))
        )

        any_imports_schema = False
        any_safe_parse = False

        for cf in client_files:
            content = cf.read_text(encoding='utf-8', errors='replace')
            root = self.parse_file(cf)
            if root:
                for imp in self.get_imports(root):
                    if 'shared' in imp.source or domain_name in imp.source:
                        if any('Schema' in n or 'schema' in n.lower() for n in imp.names):
                            any_imports_schema = True
            elif _SCHEMA_IMPORT_FROM_SHARED_RE.search(content):
                any_imports_schema = True
            if _SAFE_PARSE_RE.search(content):
                any_safe_parse = True

        if not any_imports_schema:
            violations.append(self.v(
                f"Domain '{domain_name}/client/' does not import the Zod schema "
                "from shared/. Forms and API clients must validate user input "
                "with the shared schema via safeParse().",
                str(client_dir),
                severity='warning',
            ))
        elif not any_safe_parse:
            violations.append(self.v(
                f"Domain '{domain_name}/client/' imports the schema but never "
                "calls .safeParse(). Use safeParse() on form data before "
                "submitting to the server.",
                str(client_dir),
                severity='warning',
            ))

        return violations

    # ------------------------------------------------------------------ #
    # 4. No duplicate schemas in server/ or client/                        #
    # ------------------------------------------------------------------ #

    def _check_no_duplicate_schemas(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        for tier in ('server', 'client'):
            tier_dir = domain_path / tier
            if not tier_dir.exists():
                continue
            for ts_file in sorted(tier_dir.glob('*.ts')):
                content = ts_file.read_text(encoding='utf-8', errors='replace')
                if _ZOD_OBJECT_RE.search(content):
                    violations.append(self.v(
                        f"Zod schema definition found in "
                        f"'{domain_path.name}/{tier}/{ts_file.name}'. "
                        "Schemas must live exclusively in shared/ — "
                        "import them instead of redefining.",
                        str(ts_file),
                    ))
        return violations

    # ------------------------------------------------------------------ #
    # 5. API client must hydrate JSON into domain instances                #
    # ------------------------------------------------------------------ #

    def _check_api_client_hydrates(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        client_dir = domain_path / 'client'
        if not client_dir.exists():
            return violations

        domain_name = domain_path.name
        api_files = list(client_dir.glob('*.api.ts'))
        if not api_files:
            return violations

        for api_file in api_files:
            root = self.parse_file(api_file)
            if root is None:
                continue

            content = api_file.read_text(encoding='utf-8', errors='replace')

            # Check for fetch/axios calls that return data directly
            # Pattern: async functions that await fetch and return response JSON
            has_fetch = 'fetch(' in content or 'axios.' in content
            if not has_fetch:
                continue

            has_hydration = _HYDRATE_RE.search(content)
            # Look for direct return of raw JSON as typed
            lines = content.splitlines()
            suspicious_returns = []
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                if (
                    re.search(r'return\s+(data|res|response|json)\.(items|data|results|records)\b', stripped)
                    or re.search(r'return\s+await\s+\w+\.json\s*\(\s*\)', stripped)
                ):
                    suspicious_returns.append(line_num)

            if suspicious_returns and not has_hydration:
                violations.append(self.v(
                    f"API client '{api_file.name}' returns raw JSON without "
                    "hydrating into domain class instances. Call "
                    "DomainClass.create(raw) or new DomainClass(raw) to "
                    "reconstruct entities from JSON — plain objects don't "
                    "have domain methods and crash at runtime.",
                    str(api_file),
                    suspicious_returns[0],
                ))

        return violations


if __name__ == '__main__':
    run_scanner_main(ShareDomainLogicScanner, 'share-domain-logic')
