"""The story runtime contract the LERN canvas fixtures need from a project's step library.

``canvas-fixtures.ts`` installs its own story host to record each scenario's Givens and Whens, and reads what the
steps bound. That works only when the project's ``story-test.ts`` hands the host's ``it`` the scenario's Whens and
exports ``installStoryHost``, ``withStory`` and ``storyBindings``, and its ``repositories.ts`` exports
``domainRepositories``. Without them a bundle still builds, but its fixtures skip every action and hand the screens
nothing, so the build checks the contract first and stops, naming what is missing. The runtime itself ships as the
pattern's template, ``templates/test-utils/story-test/story-test.ts``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from cdd_guidance.patterns.lern_domain_driven.lern_domain_driven import LernDomainDriven

_PATTERN = Path(__file__).resolve().parents[4]
_STEP_LIBRARY_EXPORTS = ("installStoryHost", "withStory", "storyBindings")
# The host's it is called with the Whens the Then runs before its body: host.it(step, fn, { whens: ... }).
_HOST_IT_GIVEN_WHENS = re.compile(r"host\.it\((?:(?!host\.)[\s\S])*?\{\s*whens\b")


class StoryRuntimeMissing(RuntimeError):
    """The project's step library lacks a piece the canvas fixtures replay scenarios through."""


class StoryRuntimeContract:
    """Checks a LERN workspace's step library against what the canvas fixtures replay scenarios through."""

    def __init__(self, workspace: str | Path, story_test_folder: str | None = None) -> None:
        self.workspace = Path(workspace)
        self.story_test_folder = story_test_folder or LernDomainDriven.story_test_folder

    @staticmethod
    def template() -> Path:
        """The story runtime the LERN pattern ships, to copy into the step library folder."""
        return _PATTERN / "templates" / LernDomainDriven.story_test_folder / "story-test.ts"

    @property
    def story_test(self) -> Path:
        return self.workspace / self.story_test_folder / "story-test.ts"

    @property
    def repositories(self) -> Path:
        return self.workspace / self.story_test_folder / "repositories.ts"

    def missing(self) -> List[str]:
        """Each piece of the contract the workspace lacks, named with the file it belongs in."""
        return self._story_test_missing() + self._repositories_missing()

    def check(self) -> None:
        """Stop the fixtures build when the step library lacks any piece of the contract."""
        missing = self.missing()
        if missing:
            raise StoryRuntimeMissing(
                f"Canvas fixtures need the LERN story runtime in {self.story_test_folder}/, and it lacks:\n"
                + "\n".join(f"- {piece}" for piece in missing)
                + f"\nCopy the runtime from {self.template().as_posix()} into {self.story_test_folder}/story-test.ts, "
                  "and export domainRepositories() from repositories.ts beside it.")

    def _story_test_missing(self) -> List[str]:
        if not self.story_test.is_file():
            return [f"{self.story_test_folder}/story-test.ts: the file is missing"]
        source = self.story_test.read_text(encoding="utf-8")
        missing = [f"story-test.ts: no export {name}" for name in _STEP_LIBRARY_EXPORTS if not _exports(source, name)]
        if not _HOST_IT_GIVEN_WHENS.search(source):
            missing.append("story-test.ts: the host's it(name, fn, steps) is not given { whens }, "
                           "so the canvas cannot replay a scenario's actions")
        return missing

    def _repositories_missing(self) -> List[str]:
        if not self.repositories.is_file():
            return [f"{self.story_test_folder}/repositories.ts: the file is missing"]
        if not _exports(self.repositories.read_text(encoding="utf-8"), "domainRepositories"):
            return ["repositories.ts: no export domainRepositories"]
        return []


def _exports(source: str, name: str) -> bool:
    return re.search(rf"export\s+(?:async\s+)?(?:function|const|let)\s+{name}\b", source) is not None
