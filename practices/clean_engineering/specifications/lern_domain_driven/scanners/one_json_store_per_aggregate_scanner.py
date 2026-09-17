"""Scanner: each aggregate owns its own lowdb JSON file."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from lern_scanner_base import TypeScriptScanner
from scan.violation import Violation

_SHARED_STORE_NAMES = ("db.json", "database.json", "store.json", "data.json")
_PRESET_PATH_RE = re.compile(
    r"""JSONFile(?:Sync)?(?:Preset)?\s*(?:<[^>]*>)?\s*\(\s*['"`]([^'"`]+)['"`]""",
    re.IGNORECASE,
)
_DEFAULT_DATA_RE = re.compile(
    r"(?:defaultData|default_data)\s*(?::\s*\w+)?\s*=\s*\{([^}]+)\}",
    re.DOTALL,
)
_ARRAY_KEY_RE = re.compile(r"""['"]?(\w+)['"]?\s*:\s*\[\s*\]""")


class OneJsonStorePerAggregateScanner(TypeScriptScanner):
    """Flags a shared JSON database and multi-aggregate default data objects."""

    RULE = "one-json-store-per-aggregate"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        path_owners: Dict[str, List[str]] = {}

        for domain_path in self._find_domain_packages(root):
            server = self._server_file(domain_path)
            if server is None:
                continue
            content = self._read_file_content(server)
            if content is None:
                continue
            domain_name = domain_path.name
            violations += self._check_shared_filenames(server, content)
            violations += self._check_default_data_shape(server, content)
            for match in _PRESET_PATH_RE.finditer(content):
                store_path = match.group(1).replace("\\", "/")
                path_owners.setdefault(store_path, []).append(domain_name)
                if not self._path_names_aggregate(store_path, domain_name):
                    violations.append(
                        self.v(
                            f"Repository in '{domain_name}' opens '{store_path}', "
                            "which does not include this aggregate's name. "
                            "Use data/<aggregate>.json owned by this root only.",
                            str(server),
                            content[: match.start()].count("\n") + 1,
                        )
                    )

        for store_path, owners in path_owners.items():
            unique = sorted(set(owners))
            if len(unique) > 1:
                violations.append(
                    self.v(
                        f"JSON store '{store_path}' is opened by multiple aggregates "
                        f"({', '.join(unique)}). Each aggregate root owns its own file.",
                        store_path,
                    )
                )
        return violations

    def _check_shared_filenames(self, server: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        lower = content.lower()
        for name in _SHARED_STORE_NAMES:
            if name in lower:
                line = next(
                    (i for i, row in enumerate(content.splitlines(), 1) if name in row.lower()),
                    1,
                )
                violations.append(
                    self.v(
                        f"Shared JSON database filename '{name}' found. "
                        "Give each aggregate its own data/<aggregate>.json file.",
                        str(server),
                        line,
                    )
                )
        return violations

    def _check_default_data_shape(self, server: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        for match in _DEFAULT_DATA_RE.finditer(content):
            keys = _ARRAY_KEY_RE.findall(match.group(1))
            if len(keys) > 1:
                line = content[: match.start()].count("\n") + 1
                violations.append(
                    self.v(
                        f"lowdb default data has {len(keys)} collections "
                        f"({', '.join(keys)}). One JSON store holds one aggregate.",
                        str(server),
                        line,
                    )
                )
        return violations

    @staticmethod
    def _path_names_aggregate(store_path: str, domain_name: str) -> bool:
        stem = Path(store_path).stem.lower()
        slug = domain_name.lower()
        singular = slug[:-1] if slug.endswith("s") else slug
        return slug in stem or singular in stem
