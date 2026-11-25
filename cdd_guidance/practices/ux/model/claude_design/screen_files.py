"""The files a prototype screen's markup source needs in a canvas version (*ScreenFiles*).

A screen ported from another Claude Design canvas draws that canvas's component, a ``.dc.html`` file, which loads
scripts and stylesheets by relative links; a page taken from an existing app links its stylesheets. Each version
carries its own copies of those files (``each-version-carries-its-files``), so the source names them and the render
copies them into the version's project folder. The component is copied beside the screens, its links to the files
copied repointed at the copies from where it now sits, and the links the source names to drop (a vendor script the
canvas supplies itself, a prototype tool's script) removed with their line.

A story screen draws in a frame of its own size (``.canvas-screen``, a size container named ``canvas-screen``), while
the browser window around the canvas is always wide. So each stylesheet copied, and each ``<style>`` block of the
component, has its width and height ``@media`` rules turned into ``@container canvas-screen`` rules and ``vw`` into
``cqw`` (*ContainerCss*, the size conversion ``mounted_view/scope-css.mjs`` makes), and the screen lays out at its own
width. Selectors stay as written: a ported design system's tokens answer to ``:root`` and to the theme the component
sets on ``<html>``.

See ``story_canvas.md`` beside this file, *Prototype screens*."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

# A script or stylesheet tag, its link (src or href) in group 2, and the line break after it.
_LINKED_TAG = re.compile(
    r"(<script\b[^>]*?\bsrc=[\"']([^\"']+)[\"'][^>]*>\s*</script>|<link\b[^>]*?\bhref=[\"']([^\"']+)[\"'][^>]*>)(\r?\n)?",
    re.IGNORECASE)
# A link that leaves the project: a URL with a scheme, a path from the site's root, an anchor, inline data.
_OFF_PROJECT = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|/|#)", re.IGNORECASE)
# A <style> block: its opening tag, its stylesheet, and its closing tag.
_STYLE_BLOCK = re.compile(r"(<style\b[^>]*>)([\s\S]*?)(</style>)", re.IGNORECASE)
# What the size conversion changes: a media rule, or a length in the window's width.
_SIZED = re.compile(r"@media\b|\dvw\b", re.IGNORECASE)
SCOPE_CSS = Path(__file__).resolve().parent / "mounted_view" / "scope-css.mjs"


class ContainerCssFailed(RuntimeError):
    """Node could not convert a screen's stylesheets to container rules, so the screen would lay out as the window."""


class ContainerCss:
    """The size conversion of ``mounted_view/scope-css.mjs`` (``containerCss``): each width and height ``@media`` rule
    becomes an ``@container canvas-screen`` rule, ``vw`` becomes ``cqw``, and every selector and every other media rule
    stays as written. One Node run converts every stylesheet handed to it; a stylesheet with no media rule and no
    ``vw`` is handed back as it is, without starting Node."""

    def converted(self, stylesheets: Sequence[str]) -> list[str]:
        """Each of stylesheets converted, in the same order."""
        sized = [index for index, text in enumerate(stylesheets) if _SIZED.search(text)]
        if not sized:
            return list(stylesheets)
        try:
            run = subprocess.run(["node", str(SCOPE_CSS), "--container"], input=json.dumps([stylesheets[index] for index in sized]),
                                 capture_output=True, text=True, encoding="utf-8", check=True)
        except (OSError, subprocess.CalledProcessError) as failed:
            detail = getattr(failed, "stderr", "") or str(failed)
            raise ContainerCssFailed(f"The screen's stylesheets could not be converted to container rules:\n{detail.strip()}") from failed
        found = list(stylesheets)
        for index, text in zip(sized, json.loads(run.stdout)):
            found[index] = text
        return found


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
        path in project, with its links rewritten; with no component_at the component is not copied. Each stylesheet
        copied, and each ``<style>`` block of the component, lays out by the screen's frame (*ContainerCss*). Returns
        the files written."""
        written = [self._copy(source, project / target) for target, source in self.needs.items()]
        stylesheets = [path for copy in written for path in ([copy] if copy.is_file() else sorted(copy.rglob("*"))) if path.suffix.lower() == ".css"]
        component = self.relinked(project, project / component_at) if self.component is not None and component_at else None
        blocks = list(_STYLE_BLOCK.finditer(component)) if component is not None else []
        texts = [path.read_text(encoding="utf-8") for path in stylesheets] + [block.group(2) for block in blocks]
        converted = ContainerCss().converted(texts)
        for path, original, text in zip(stylesheets, texts, converted):
            if text != original:
                path.write_text(text, encoding="utf-8")
        if component is not None:
            styles = iter(converted[len(stylesheets):])
            target = project / component_at
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_STYLE_BLOCK.sub(lambda block: block.group(1) + next(styles) + block.group(3), component), encoding="utf-8")
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
