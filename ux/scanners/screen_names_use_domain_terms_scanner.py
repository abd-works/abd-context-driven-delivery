"""screen-names-use-domain-terms — screen labels should appear in collected domain terms."""

from __future__ import annotations

from ux_workspace_base import UxWorkspaceScanner


class ScreenNamesUseDomainTermsScanner(UxWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_ux_map():
            return
        domain_terms = set()
        for screen in workspace.ux_map.screens:
            domain_terms.update(term.strip().lower() for term in screen.domain_terms)
            domain_terms.update(term.strip().lower() for term in screen.domain_concepts)
        for content_type in workspace.ux_map.content_types:
            domain_terms.add(content_type.name.strip().lower())
        if not domain_terms:
            return
        for screen in workspace.ux_map.screens:
            # Tab-state suffix: compare base name before " — "
            base = screen.name.split(" — ")[0].split(" - ")[0].strip().lower()
            if base not in domain_terms and screen.name.strip().lower() not in domain_terms:
                yield self.violation(
                    f"screen {screen.name!r} is not in domain terms/content types on the map",
                    location=f"screen:{screen.name}",
                    severity="warning",
                )
