"""vocabulary-traces-to-domain-source - terms must trace to a domain source.

Applicability gate: skips when no domain source is present. Term-by-term
traceability is AI-judge territory - this scanner yields no mechanical
violations of its own.
"""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner

_DOMAIN_SOURCE_NAMES = (
    "domain-specification.md",
    "domain-model.md",
    "domain-language.md",
    "domain-glossary.md",
)


class VocabularyTracesToDomainSourceScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return
        if not self._has_domain_source(workspace):
            return
        return
        yield  # pragma: no cover - keeps method a generator

    def _has_domain_source(self, workspace) -> bool:
        for name in _DOMAIN_SOURCE_NAMES:
            for candidate in workspace.root.rglob(name):
                if candidate.is_file():
                    return True
        return False
