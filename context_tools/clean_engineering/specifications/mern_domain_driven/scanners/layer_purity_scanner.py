"""Scanner: verify layer purity - no forbidden imports in the domain core.

``<domain>.ts`` must contain only plain TypeScript and Zod. It must NOT
import Express, React, MongoDB, Mongoose, or any infrastructure/framework
library. ``server.ts`` must not import from ``client.tsx`` and vice versa.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from mern_scanner_base import MERNScanner
from utilities.scanners.violation import Violation


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
                self._check_no_cross_import(domain_path, domain_name, "server", "client")
            )
            violations.extend(
                self._check_no_cross_import(domain_path, domain_name, "client", "server")
            )

        return violations

    def _check_core_purity(self, domain_path: Path, domain_name: str) -> List[Violation]:
        violations: List[Violation] = []
        for file_path in self._find_tier_files(domain_path, "shared"):
            content = self._read_file_content(file_path)
            if content is None:
                continue

            lines = content.split("\n")
            for line_num, line in enumerate(lines, start=1):
                for pattern in self.FORBIDDEN_IN_CORE:
                    if re.search(pattern, line):
                        violations.append(
                            self.v(
                                f"Domain '{domain_name}' core file has forbidden "
                                f"framework import: {line.strip()}",
                                str(file_path),
                                line_num,
                            )
                        )
                        break

        return violations

    def _check_no_cross_import(
        self, domain_path: Path, domain_name: str, source_tier: str, forbidden_tier: str
    ) -> List[Violation]:
        violations: List[Violation] = []
        source_files = self._find_tier_files(domain_path, source_tier)

        cross_patterns = [
            rf"from\s+['\"]\.\/{forbidden_tier}['\"]",
            rf"from\s+['\"].*/{forbidden_tier}['\"/]",
            rf"from\s+['\"]@[\w-]+/{domain_name}/{forbidden_tier}['\"]",
        ]

        for file_path in source_files:
            content = self._read_file_content(file_path)
            if content is None:
                continue

            lines = content.split("\n")
            for line_num, line in enumerate(lines, start=1):
                for pattern in cross_patterns:
                    if re.search(pattern, line):
                        violations.append(
                            self.v(
                                f"Domain '{domain_name}/{source_tier}' "
                                f"imports from '{forbidden_tier}' - "
                                f"cross-tier import violation: {line.strip()}",
                                str(file_path),
                                line_num,
                            )
                        )
                        break

        return violations
