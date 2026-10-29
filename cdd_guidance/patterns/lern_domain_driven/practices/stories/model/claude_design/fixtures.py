"""LERN canvas fixtures: the shared stories and their example fixtures, bundled to run on a Claude Design canvas.

A canvas screen's *Load from fixture* calls ``CanvasFixtures.load(story, scenario)``: every in-memory repository
is emptied and the scenario's Givens run through the real story runtime, so the screen draws what the story set up.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List

_HERE = Path(__file__).resolve().parent
_ENTRY_TEMPLATE = _HERE / "canvas-fixtures.ts"
_BUILD_SCRIPT = _HERE / "build-canvas-fixtures.mjs"


class LernCanvasFixtures:
    """Builds ``canvas-fixtures.js`` from a LERN workspace's ``*.story.shared.ts`` files."""

    story_test_folder = "test-utils/story-test"
    tests_folder = "tests"
    work_folder = ".temp/canvas-fixtures"
    shared_story_glob = "*.story.shared.ts"
    examples_glob = "*.examples.ts"
    seed_pastes_module = "test-utils/seed-overlay/seed-pastes"

    def __init__(self, workspace: str | Path, story_test_folder: str | None = None, resettables: Iterable[str] = ()) -> None:
        """*resettables*: ``module#export`` names (module relative to the workspace, without .ts) of other test state
        whose ``_reset()`` must run with the repositories' on every load — gateways, clocks."""
        self.workspace = Path(workspace)
        self.story_test_folder = story_test_folder or self.story_test_folder
        self.resettables = list(resettables)

    def shared_story_files(self) -> List[Path]:
        return sorted((self.workspace / self.tests_folder).rglob(self.shared_story_glob))

    def example_files(self) -> List[Path]:
        return sorted((self.workspace / self.tests_folder).rglob(self.examples_glob))

    def entry(self, story_names: Iterable[str]) -> str:
        """The bundle's entry: the story runtime, the domain repositories, and every shared story."""
        work = self.workspace / self.work_folder
        imports = [f"import '{self._relative(work, path)}';" for path in self.shared_story_files()]
        examples = [f"import * as examples{index} from '{self._relative(work, path)}';" for index, path in enumerate(self.example_files())]
        modules = ", ".join(f"examples{index}" for index in range(len(examples)))
        return (_ENTRY_TEMPLATE.read_text(encoding="utf-8")
                .replace("__STORY_TEST__", self._relative(work, self.workspace / self.story_test_folder))
                .replace("__IMPORTS__", "\n".join(imports))
                .replace("__EXAMPLES__", "\n".join(examples))
                .replace("__EXAMPLE_MODULES__", modules)
                .replace("__SEED_PASTES__", self._seed_pastes(work))
                .replace("__RESETTABLE_IMPORTS__", "\n".join(self._resettable_imports(work)))
                .replace("__RESETTABLES__", ", ".join(f"resettable{index}" for index in range(len(self.resettables))))
                .replace("__STORIES__", json.dumps(list(story_names), ensure_ascii=False)))

    def build(self, story_names: Iterable[str], out_file: str | Path) -> Path:
        """Write the entry beside the workspace's sources and bundle it to *out_file* with esbuild."""
        work = self.workspace / self.work_folder
        work.mkdir(parents=True, exist_ok=True)
        entry = work / "canvas-fixtures.ts"
        entry.write_text(self.entry(story_names), encoding="utf-8")
        script = work / _BUILD_SCRIPT.name
        shutil.copyfile(_BUILD_SCRIPT, script)
        out = Path(out_file).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["node", str(script), str(entry), str(out)], cwd=self.workspace, check=True,
                       shell=os.name == "nt", capture_output=True, text=True)
        return out

    def _seed_pastes(self, work: Path) -> str:
        """Dev mode's seed pastes, when the workspace has them; otherwise no screen has any."""
        module = self.workspace / f"{self.seed_pastes_module}.ts"
        if module.is_file():
            return f"import {{ seedPastes }} from '{self._relative(work, module)}';"
        return "const seedPastes = (): unknown[] => [];"

    def _resettable_imports(self, work: Path) -> List[str]:
        imports = []
        for index, name in enumerate(self.resettables):
            module, export = name.split("#")
            imports.append(f"import {{ {export} as resettable{index} }} from '{self._relative(work, self.workspace / module)}';")
        return imports

    def _relative(self, start: Path, target: Path) -> str:
        relative = Path(os.path.relpath(target, start)).as_posix()
        relative = relative.removesuffix(".ts")
        return relative if relative.startswith(".") else f"./{relative}"
