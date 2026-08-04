"""Scanner: verify domain-first package structure.

Checks that each domain module under packages/ contains the three-file
layout: ``<domain>.ts`` (core), ``<domain>-server.ts``,
``<domain>-client.tsx``, plus a package.json with matching export entrypoints.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from mern_scanner_base import MERNScanner
from utilities.scanners.violation import Violation


class DomainStructureScanner(MERNScanner):
    """Checks domain packages have <domain>.ts + <domain>-server.ts + <domain>-client.tsx."""

    RULE = "organize-by-domain-module"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        project_root = root

        domain_packages = self._find_domain_packages(project_root)

        if not domain_packages:
            packages_dir = project_root / "packages"
            if packages_dir.exists():
                violations.append(
                    self.v(
                        "No domain packages found under packages/. "
                        "Expected at least one domain folder with "
                        "<domain>.ts, <domain>-server.ts, and <domain>-client.tsx.",
                        str(packages_dir),
                    )
                )
            return violations

        for domain_path in domain_packages:
            domain_name = domain_path.name
            singular = domain_name.rstrip("s")

            if self._domain_core_file(domain_path) is None:
                violations.append(
                    self.v(
                        f"Domain '{domain_name}' is missing required "
                        f"'{domain_name}.ts' (domain core).",
                        str(domain_path),
                    )
                )

            if not (domain_path / "package.json").exists():
                violations.append(
                    self.v(
                        f"Domain '{domain_name}' is missing required "
                        "file 'package.json'.",
                        str(domain_path),
                    )
                )

            if self._server_file(domain_path) is None:
                violations.append(
                    self.v(
                        f"Domain '{domain_name}' is missing required "
                        f"'{singular}-server.ts' (server tier).",
                        str(domain_path),
                    )
                )

            if self._client_file(domain_path) is None:
                violations.append(
                    self.v(
                        f"Domain '{domain_name}' is missing required "
                        f"'{singular}-client.tsx' (client tier with views).",
                        str(domain_path),
                    )
                )

        return violations
