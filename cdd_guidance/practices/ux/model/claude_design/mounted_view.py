"""A story's screen drawn by the product's own production view, mounted on the canvas: the fourth source of a
screen's markup, beside written, taken from an app, and ported (``story_screen.py``).

*MountedViewBundle* bundles the project's view entry with esbuild into one design-system folder of the canvas
version (``project/ds/<folder>/``): the views and what they import, the product's stylesheets scoped to the screen's
frame, and the stand-ins a canvas needs (``mounted_view/``):

- a React shim, so views compiled for React 19's automatic JSX run on the canvas's React 18.3.1;
- ``fetch``, answered by the project's ``canvasRoutes``, which run the domain operation on the objects the scenario's
  fixture built, so a view draws what the story holds and never a table written for the canvas;
- ``window.location``, which moves the story explorer to the story a page belongs to (``canvasNavigation``) instead
  of moving the artboard away;
- ``scope-css.mjs``, which keeps the product's stylesheet inside the screen's frame.

The view entry is the project's seam: it exports each screen by name, as a component that takes ``bound`` (every object
the scenario bound, under its own name), ``repositories`` (what its Givens filled) and ``position`` (where the step
group places the screen), and makes the view's clients from them; ``canvasRoutes`` (``METHOD /path`` → answer); and
``canvasNavigation`` (path → story). *MountedViewMarkup* draws one of those screens through ``x-import``.

See ``story_canvas.md`` beside this file, *Prototype screens*."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from cdd_guidance.practices.ux.model.claude_design.story_screen import ScreenMarkup

RUNTIME_FOLDER = Path(__file__).resolve().parent / "mounted_view"
BUILD_SCRIPT = "build-mounted-views.mjs"
# Where the build writes the bundle's generated entry, inside the project, so esbuild resolves the project's packages.
WORK_FOLDER = ".temp/mounted-views"
DESIGN_SYSTEMS_FOLDER = "ds"


class MountedViewsNotBuilt(RuntimeError):
    """The project's views could not be bundled for the canvas, so the screens that mount them would draw nothing."""


@dataclass(frozen=True)
class MountedViewBundle:
    """The project's production views bundled for the canvas: *project_root*, the project whose ``node_modules``
    holds esbuild; *entry*, its view entry, from the project's root; *folder*, the design-system folder the bundle
    takes in a canvas version (``project/ds/<folder>/``, also the bundle's file name); *namespace*, the global the
    canvas reads its components from; *tsconfig*, the project's TypeScript settings, whose paths resolve its imports."""

    project_root: Path
    entry: str
    folder: str = "paradise"
    namespace: str = "Paradise"
    tsconfig: str = "tsconfig.json"
    _built: set = field(default_factory=set, compare=False, hash=False, repr=False)

    @property
    def head(self) -> str:
        """What a screen in ``project/screens/`` loads: the scoped stylesheet, then the bundle."""
        base = f"../{DESIGN_SYSTEMS_FOLDER}/{self.folder}/{self.folder}"
        return f'<link rel="stylesheet" href="{base}.css">\n<script src="{base}.js"></script>'

    @property
    def component(self) -> str:
        """The component every mounted screen draws, by its global name."""
        return f"{self.namespace}.CanvasMount"

    def build(self, project: Path) -> list[Path]:
        """Bundle the views into *project* (a canvas version's ``project/`` folder), once for each folder; answers the
        files written. Stops with *MountedViewsNotBuilt*, naming what esbuild said, when the bundle cannot be built."""
        outdir = Path(project) / DESIGN_SYSTEMS_FOLDER / self.folder
        if outdir.resolve() not in self._built:
            self._run_build(outdir)
            self._built.add(outdir.resolve())
        return sorted(path for path in outdir.rglob("*") if path.is_file())

    def _run_build(self, outdir: Path) -> None:
        root = Path(self.project_root).resolve()
        work = root / WORK_FOLDER
        work.mkdir(parents=True, exist_ok=True)
        script = work / BUILD_SCRIPT
        shutil.copyfile(RUNTIME_FOLDER / BUILD_SCRIPT, script)
        config = work / "config.json"
        config.write_text(json.dumps(self._config(work, outdir)), encoding="utf-8")
        try:
            subprocess.run(["node", str(script), str(config)], cwd=root, check=True, capture_output=True, text=True,
                           encoding="utf-8", shell=os.name == "nt")
        except subprocess.CalledProcessError as failed:
            raise MountedViewsNotBuilt(f"The project's views ({self.entry}) could not be bundled for the canvas:\n"
                                       f"{(failed.stderr or failed.stdout or '').strip()}") from failed

    def _config(self, work: Path, outdir: Path) -> dict:
        root = Path(self.project_root).resolve()
        return {"entry": str(root / self.entry), "runtime": str(RUNTIME_FOLDER), "work": str(work),
                "outdir": str(outdir.resolve()), "name": self.folder, "namespace": self.namespace,
                "tsconfig": str(root / self.tsconfig)}


@dataclass(frozen=True)
class MountedViewMarkup(ScreenMarkup):
    """A screen drawn by the production view the project's entry exports as *view*, from *bundle*, inside the
    screen's frame (``.canvas-screen``, which *StoryScreen* draws and whose width the bundle's container rules read),
    in a wrapper of its own (``.canvas-mount``, which the bundle's scoped selectors and design tokens answer to, so a
    ported screen in the same kind of frame keeps its own theme). It hands the view every
    object the scenario bound, the repositories, the step group's position, and the explorer's ``go``. *size* is the
    hint size the editor gives it."""

    view: str
    bundle: MountedViewBundle
    size: str = "100%,844px"

    @property
    def head(self) -> str:
        return self.bundle.head

    def body_for(self, position_settings: list[str]) -> str:
        given = 'bound="{{ bound }}" repositories="{{ repositories }}" position="{{ position }}" go="{{ go }}"'
        return (f'<div class="canvas-mount">\n<x-import component-from-global-scope="{self.bundle.component}" '
                f'view="{self.view}" {given} hint-size="{self.size}"></x-import>\n</div>')

    def copy_files(self, project: Path) -> list[Path]:
        """Bundle the project's views into the version, where the screen's head loads them."""
        return self.bundle.build(project)

    def sources(self) -> dict[str, Path]:
        """The bundle's folder in the version comes from the project's view entry, its production code."""
        return {f"{DESIGN_SYSTEMS_FOLDER}/{self.bundle.folder}": Path(self.bundle.project_root) / self.bundle.entry}
