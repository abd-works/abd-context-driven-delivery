"""The files a prototype screen's markup source needs in a canvas version (*ScreenFiles*).

A screen ported from another Claude Design canvas draws that canvas's component, a ``.dc.html`` file, which loads
scripts and stylesheets by relative links; a page taken from an existing app links its stylesheets. Each version
carries its own copies of those files (``each-version-carries-its-files``), so the source names them and the render
copies them into the version's project folder. The component is copied beside the screens, its links to the files
copied repointed at the copies from where it now sits, and the links the source names to drop (a vendor script the
canvas supplies itself, a prototype tool's script) removed with their line.

See ``story_canvas.md`` beside this file, *Prototype screens*."""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

# A script or stylesheet tag, its link (src or href) in group 2, and the line break after it.
_LINKED_TAG = re.compile(
    r"(<script\b[^>]*?\bsrc=[\"']([^\"']+)[\"'][^>]*>\s*</script>|<link\b[^>]*?\bhref=[\"']([^\"']+)[\"'][^>]*>)(\r?\n)?",
    re.IGNORECASE)
# A link that leaves the project: a URL with a scheme, a path from the site's root, an anchor, inline data.
_OFF_PROJECT = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|/|#)", re.IGNORECASE)


@dataclass(frozen=True)
class ScreenFiles:
    """What a markup source needs in the version: *component*, the file it draws (a ported canvas's ``.dc.html``);
    *needs*, each file or folder it loads, by the path its copy takes in the version's project folder; and *dropped*,
    patterns of the links in the component to remove rather than copy."""

    component: Optional[Path] = None
    needs: Mapping[str, Path] = field(default_factory=dict)
    dropped: Sequence[str] = ()

    def copy_into(self, project: Path, component_at: str = "") -> list[Path]:
        """Copy every file it needs into project, over any copy already there, and the component to component_at, a
        path in project, with its links rewritten; with no component_at the component is not copied. Returns the
        files written."""
        written = [self._copy(source, project / target) for target, source in self.needs.items()]
        if self.component is not None and component_at:
            target = project / component_at
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(self.relinked(project, target), encoding="utf-8")
            written.append(target)
        return written

    def relinked(self, project: Path, target: Path) -> str:
        """The component's text as it reads at target: each link to a file it needs pointed at that file's copy, each
        link matching *dropped* removed, every other link as it was."""
        def rewritten(tag: re.Match) -> str:
            link = tag.group(2) or tag.group(3)
            if any(re.search(pattern, link) for pattern in self.dropped):
                return ""
            copy = self._copy_of(link, project)
            if copy is None:
                return tag.group(0)
            relative = Path(os.path.relpath(copy, target.parent)).as_posix()
            return tag.group(0).replace(f'"{link}"', f'"{relative}"').replace(f"'{link}'", f"'{relative}'")

        return _LINKED_TAG.sub(rewritten, self.component.read_text(encoding="utf-8"))

    def _copy_of(self, link: str, project: Path) -> Optional[Path]:
        """Where the file link names, read from the component's folder, is copied in project; None for a link that
        leaves the project or names a file it does not copy."""
        if _OFF_PROJECT.match(link):
            return None
        linked = (self.component.parent / link).resolve()
        for target, source in self.needs.items():
            source = Path(source).resolve()
            if linked == source or linked.is_relative_to(source):
                return project / target / linked.relative_to(source)
        return None

    def _copy(self, source: Path, target: Path) -> Path:
        """Copy the file or folder source to target, over what is there."""
        target.parent.mkdir(parents=True, exist_ok=True)
        if Path(source).is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copyfile(source, target)
        return target
