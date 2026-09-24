"""Scanner: verify layer purity - no forbidden imports in the domain core.

``<domain>.ts`` must contain only plain TypeScript and Zod. It must NOT
import Express, React, lowdb, or any infrastructure/framework
library. ``server.ts`` must not import from ``client.tsx`` and vice versa.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from lern_scanner_base import LERNScanner, Violation


@dataclass
class _CrossTierImport:
    domain_path: Path
    domain_name: str
    source_tier: str
    forbidden_tier: str


class LayerPurityScanner(LERNScanner):
    """Checks domain core has no framework imports and tiers don't cross-import."""

    RULE = "maintain-layer-purity"

    FORBIDDEN_IN_CORE = [
        r"from\s+['\"]express['\"]",
        r"from\s+['\"]react['\"]",
        r"from\s+['\"]react-dom['\"]",
        r"from\s+['\"]lowdb['\"]",
        r"from\s+['\"]lowdb/",
        r"from\s+['\"]@tanstack",
        r"from\s+['\"]zustand['\"]",
        r"from\s+['\"]redux['\"]",
        r"from\s+['\"]@reduxjs",
        r"import\s+.*\s+from\s+['\"]express['\"]",
        r"import\s+.*\s+from\s+['\"]react['\"]",
        r"import\s+.*\s+from\s+['\"]lowdb['\"]",
        r"import\s+.*\s+from\s+['\"]lowdb/",
        r"require\(['\"]express['\"]\)",
        r"require\(['\"]react['\"]\)",
        r"require\(['\"]lowdb['\"]\)",
        r"require\(['\"]lowdb/",
    ]

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        domain_packages = self._find_domain_packages(root)

        for domain_path in domain_packages:
            domain_name = domain_path.name

            violations.extend(self._check_core_purity(domain_path, domain_name))
            violations.extend(
                self._check_no_cross_import(
                    _CrossTierImport(domain_path, domain_name, "server", "client")
                )
            )
            violations.extend(
                self._check_no_cross_import(
                    _CrossTierImport(domain_path, domain_name, "client", "server")
                )
            )

        return violations

    def _check_core_purity(self, domain_path: Path, domain_name: str) -> List[Violation]:
        violations: List[Violation] = []
        for file_path in self._find_tier_files(domain_path, "shared"):
            violations.extend(self._forbidden_core_imports(file_path, domain_name))
        return violations

    def _forbidden_core_imports(self, file_path: Path, domain_name: str) -> List[Violation]:
        content = self._read_file_content(file_path)
        if content is None:
            return []
        violations: List[Violation] = []
        for line_num, line in enumerate(content.split("\n"), start=1):
            if not self._line_has_forbidden_core_import(line):
                continue
            violations.append(
                self.v(
                    f"Domain '{domain_name}' core file has forbidden "
                    f"framework import: {line.strip()}",
                    str(file_path),
                    line_num,
                )
            )
        return violations

    def _line_has_forbidden_core_import(self, line: str) -> bool:
        return any(re.search(pattern, line) for pattern in self.FORBIDDEN_IN_CORE)

    def _check_no_cross_import(self, crossing: _CrossTierImport) -> List[Violation]:
        violations: List[Violation] = []
        for file_path in self._find_tier_files(crossing.domain_path, crossing.source_tier):
            violations.extend(self._cross_import_hits(file_path, crossing))
        return violations

    def _cross_import_hits(self, file_path: Path, crossing: _CrossTierImport) -> List[Violation]:
        content = self._read_file_content(file_path)
        if content is None:
            return []
        patterns = [
            rf"from\s+['\"]\.\/{crossing.forbidden_tier}['\"]",
            rf"from\s+['\"].*/{crossing.forbidden_tier}['\"/]",
            rf"from\s+['\"]@[\w-]+/{crossing.domain_name}/{crossing.forbidden_tier}['\"]",
        ]
        violations: List[Violation] = []
        for line_num, line in enumerate(content.split("\n"), start=1):
            if not any(re.search(pattern, line) for pattern in patterns):
                continue
            violations.append(
                self.v(
                    f"Domain '{crossing.domain_name}/{crossing.source_tier}' "
                    f"imports from '{crossing.forbidden_tier}' - "
                    f"cross-tier import violation: {line.strip()}",
                    str(file_path),
                    line_num,
                )
            )
        return violations
