"""Scanner: repository seam loads, creates, searches, and updates the aggregate root."""
from __future__ import annotations

from pathlib import Path
from typing import List, Set

from lern_scanner_base import TypeScriptScanner
from scan.violation import Violation

_REQUIRED = ("load", "create", "search", "update")


class RepositoryOwnsAggregateLifecycleScanner(TypeScriptScanner):
    """Domain-core *Repository interfaces must cover the aggregate-root lifecycle."""

    RULE = "repository-owns-aggregate-lifecycle"

    def scan(self, root: Path, files: List[Path]) -> List[Violation]:
        violations: List[Violation] = []
        for domain_path in self._find_domain_packages(root):
            core = self._domain_core_file(domain_path)
            if core is None:
                continue
            parsed = self.parse_file(core)
            if parsed is None:
                violations += self._regex_fallback(core, domain_path.name)
                continue
            repo_ifaces = [
                iface
                for iface in self.get_interfaces(parsed)
                if iface.name.endswith("Repository")
            ]
            if not repo_ifaces:
                violations.append(
                    self.v(
                        f"Domain '{domain_path.name}' core has no *Repository interface. "
                        "Compartment the aggregate behind a repository that load/create/"
                        "search/update the aggregate root.",
                        str(core),
                    )
                )
                continue
            for iface in repo_ifaces:
                names = {n.lower() for n in iface.method_names}
                missing = [op for op in _REQUIRED if op not in names]
                if missing:
                    violations.append(
                        self.v(
                            f"Interface '{iface.name}' is missing {', '.join(missing)}(). "
                            "A Repository returns the aggregate root via load, create, "
                            "search, and update.",
                            str(core),
                            iface.start_line,
                        )
                    )
        return violations

    def _regex_fallback(self, core: Path, domain_name: str) -> List[Violation]:
        content = core.read_text(encoding="utf-8", errors="replace")
        if "Repository" not in content:
            return [
                self.v(
                    f"Domain '{domain_name}' core has no *Repository interface.",
                    str(core),
                )
            ]
        present: Set[str] = set()
        for op in _REQUIRED:
            if f"{op}(" in content or f"{op} (" in content:
                present.add(op)
        missing = [op for op in _REQUIRED if op not in present]
        if missing:
            return [
                self.v(
                    f"Repository in '{core.name}' is missing {', '.join(missing)}(). "
                    "A Repository returns the aggregate root via load, create, "
                    "search, and update.",
                    str(core),
                )
            ]
        return []
