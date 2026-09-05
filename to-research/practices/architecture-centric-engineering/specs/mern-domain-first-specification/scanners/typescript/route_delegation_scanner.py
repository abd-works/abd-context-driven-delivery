"""Scanner: route handlers must delegate to domain-server, not repository directly.

Flags *.routes.ts handlers that call repo.* or repository methods inline
instead of delegating to a server-side domain class.
"""
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


class RouteDelegationScanner(MERNScanner):
    """Checks route files delegate to domain-server rather than calling repo directly."""

    REPO_CALL = re.compile(
        r"\b(?:repo|repository)\.\w+\(",
        re.IGNORECASE,
    )
    SHARED_DOMAIN_IN_ROUTE = re.compile(
        r"new\s+\w+\s*\([^)]*\)\s*\.\s*(?:filter|search|map|reduce)\w*\(",
    )

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for routes_file in project_root.rglob("*.routes.ts"):
            if "node_modules" in routes_file.parts:
                continue
            violations.extend(self._check_routes_file(routes_file))

        for router_file in project_root.rglob("*Router.ts"):
            if "node_modules" in router_file.parts:
                continue
            violations.extend(self._check_routes_file(router_file))

        return violations

    def _check_routes_file(self, path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return violations

        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if self.REPO_CALL.search(line):
                violations.append({
                    "rule": self.rule,
                    "message": (
                        "Route handler calls repository directly — delegate to "
                        "<<domain>>-server domain class instead."
                    ),
                    "location": str(path),
                    "line": i,
                })
            if self.SHARED_DOMAIN_IN_ROUTE.search(line):
                violations.append({
                    "rule": self.rule,
                    "message": (
                        "Route handler applies shared domain logic inline — "
                        "move to server-side domain class."
                    ),
                    "location": str(path),
                    "line": i,
                })

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(RouteDelegationScanner, 'delegate-routes-to-domain-server')
