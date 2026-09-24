"""Scanner: verify layer purity - no forbidden imports in the domain core.

``<domain>.ts`` must contain only plain TypeScript and Zod. It must NOT
import Express, React, MongoDB, Mongoose, or any infrastructure/framework
library. ``server.ts`` must not import from ``client.tsx`` and vice versa.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from mern_scanner_base import MERNScanner, Violation


@dataclass
class _CrossImportScan:
    domain_path: Path
    domain_name: str
    source_tier: str
    forbidden_tier: str


class LayerPurityScanner(MERNScanner):
    """Checks domain core has no framework imports and tiers don't cross-import."""

    RULE = "maintain-layer-purity"

    FORBIDDEN_IN_CORE = [
        r"from\s+['\"]express['\"]",
        r"from\s+['\"]react['\"]",
        r"from\s+['\"]react-dom['\"]",
        r"from\s+['\"]mongodb['\"]",
        r"from\s+['\"]mongoose['\"]",
        r"from\s+['\"]@tanstack",
        r"from\s+['\"]zustand['\"]",
        r"from\s+['\"]redux['\"]",
        r"from\s+['\"]@reduxjs",
        r"import\s+.*\s+from\s+['\"]express['\"]",
        r"import\s+.*\s+from\s+['\"]react['\"]",
        r"import\s+.*\s+from\s+['\"]mongodb['\"]",
        r"import\s+.*\s+from\s+['\"]mongoose['\"]",
        r"require\(['\"]express['\"]\)",
        r"require\(['\"]react['\"]\)",
        r"require\(['\"]mongodb['\"]\)",
        r"require\(['\"]mongoose['\"]\)",
    ]

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        domain_packages = self._find_domain_packages(root)

        for domain_path in domain_packages:
            domain_name = domain_path.name

            violations.extend(self._check_core_purity(domain_path, domain_name))
            violations.extend(
                self._check_no_cross_import(
                    _CrossImportScan(domain_path, domain_name, "server", "client")
                )
            )
            violations.extend(
                self._check_no_cross_import(
                    _CrossImportScan(domain_path, domain_name, "client", "server")
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
            if not self._core_line_is_forbidden(line):
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

    def _core_line_is_forbidden(self, line: str) -> bool:
        return any(re.search(pattern, line) for pattern in self.FORBIDDEN_IN_CORE)

    def _check_no_cross_import(self, scan: _CrossImportScan) -> List[Violation]:
        violations: List[Violation] = []
        for file_path in self._find_tier_files(scan.domain_path, scan.source_tier):
            violations.extend(self._cross_import_hits(file_path, scan))
        return violations

    def _cross_import_hits(self, file_path: Path, scan: _CrossImportScan) -> List[Violation]:
        content = self._read_file_content(file_path)
        if content is None:
            return []
        violations: List[Violation] = []
        for line_num, line in enumerate(content.split("\n"), start=1):
            if not self._line_imports_forbidden_tier(line, scan):
                continue
            violations.append(
                self.v(
                    f"Domain '{scan.domain_name}/{scan.source_tier}' "
                    f"imports from '{scan.forbidden_tier}' - "
                    f"cross-tier import violation: {line.strip()}",
                    str(file_path),
                    line_num,
                )
            )
        return violations

    def _line_imports_forbidden_tier(self, line: str, scan: _CrossImportScan) -> bool:
        return any(re.search(pattern, line) for pattern in self._cross_patterns(scan))

    def _cross_patterns(self, scan: _CrossImportScan) -> List[str]:
        return [
            rf"from\s+['\"]\.\/{scan.forbidden_tier}['\"]",
            rf"from\s+['\"].*/{scan.forbidden_tier}['\"/]",
            rf"from\s+['\"]@[\w-]+/{scan.domain_name}/{scan.forbidden_tier}['\"]",
        ]
