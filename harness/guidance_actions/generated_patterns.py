"""GeneratedPatterns. The patterns content is generated with, recorded where Generate writes it and read back where
Validate judges it, so content is judged with the patterns it was made with, whatever the session overlays now."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance_actions.patterns_file import PatternsFile

if TYPE_CHECKING:
    from harness.graph.pattern_overlays import PatternOverlays


class GeneratedPatterns:
    """The patterns a graph overlays, as the content an action generates records them: Generate records each applied
    pattern in the patterns file of each folder it writes content in and tells the agent how to record them in any
    other folder (``record_content``); an action that judges content reads the patterns it was generated with back
    (``recorded_for``)."""

    def __init__(self, overlays: PatternOverlays) -> None:
        self._overlays = overlays

    def record_content(self, folders: list[Path]) -> str:
        """Record each applied pattern in the patterns file of each folder content is generated in, and say how to
        record them for any other folder and how to name the roles a folder holds; none when none is applied."""
        if not self._overlays.patterns:
            return ""
        return self.instructions(self._recorded_in(folders))

    def recorded_for(self, paths: list[Path], root: Path) -> list[str]:
        """The registered patterns the content at paths was generated with, from the patterns file nearest each path
        up to root, once each; none when no folder records any."""
        found = [PatternsFile.nearest(path, root) for path in paths]
        recorded = [name for patterns in found if patterns is not None for name in patterns.patterns]
        registered = set(self._overlays.names)
        return [name for name in dict.fromkeys(recorded) if name in registered]

    def instructions(self, files: list[PatternsFile]) -> str:
        """How the agent records the applied patterns in any other folder it writes content in, naming the files they
        are recorded in already and the roles each pattern has."""
        overlays = self._overlays.graph_overlays
        names = ", ".join(overlay.name for overlay in overlays)
        written = ", ".join(file.path.as_posix() for file in files) or "none yet"
        return "\n".join([
            "## Patterns this content is generated with",
            "",
            f"This content is generated with {names}, recorded in `.context/patterns.md` at the root of each folder it is "
            f"written in ({written}). Record the same patterns at the root of any other folder you write content in. When "
            "a pattern's layers sit in several folders, name after the pattern the roles this folder holds "
            "(`- cdd_web_domain_access: Domain, Tool, Contract`); a folder that holds the whole pattern names none. Keep "
            "the patterns and roles already there. The roles each pattern has:",
            "",
            *(f"- {overlay.name}: {', '.join(overlay.roles)}" for overlay in overlays if overlay.roles),
        ])

    def _recorded_in(self, folders: list[Path]) -> list[PatternsFile]:
        """The patterns file of each folder content is generated in, once each, with each applied pattern recorded."""
        files = list({file.folder: file for file in map(PatternsFile.for_content, folders)}.values())
        applied = [overlay.name for overlay in self._overlays.graph_overlays]
        for file in files:
            file.record(applied)
        return files
