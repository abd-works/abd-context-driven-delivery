"""TestTiers - the test tiers a session records for each module: which tiers the module's tests use, and the test tool of
each, kept in its session.json."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from space.session.session_record import TEST_TIERS, SessionFields

if TYPE_CHECKING:
    from space.session.session import Session


class UnknownTestTierError(ValueError):
    """A tier was recorded that is none of the tiers a module's tests can use."""

    def __init__(self, module: str, tiers: list[str]) -> None:
        super().__init__(f"{module} cannot record the test tier {', '.join(tiers)}: the tiers are {', '.join(TEST_TIERS)}")
        self.module = module
        self.tiers = tiers


class TestToolRequiredError(ValueError):
    """A tier was recorded with no test tool, which the record keeps for each tier so the next test is written with it."""

    def __init__(self, module: str, tiers: list[str]) -> None:
        super().__init__(
            f"{module} cannot record the test tier {', '.join(tiers)} with no test tool: name the tool, such as mamba or playwright"
        )
        self.module = module
        self.tiers = tiers


class TestTiers:
    """The test tiers one session records for its modules. Every module's tests use the unit tier; a module that
    publishes operations through a server also uses the server tier, and one that shows a page the web tier. A generate
    or a render that writes tests for a module records them here, so the next one reads which tiers a story of that
    module needs a test at. A module is named by its folder's path from the project."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def recorded(self) -> dict[str, dict[str, str]]:
        """Each module's tiers with the test tool of each, as session.json holds them; none before any was recorded."""
        return self._session.record.fields.test_tiers

    def of(self, module: str) -> dict[str, str]:
        """The tiers module uses, each with its test tool; none while nothing was recorded for it."""
        return dict(self.recorded.get(self.path_of(module), {}))

    def record(self, module: str, tiers: dict[str, str]) -> dict[str, str]:
        """Keep tiers, each with its test tool, beside the tiers module already holds, and answer the module's tiers. A
        tier recorded again takes the tool named last. A tier that is none of unit, server and web, or one with no
        tool, is refused and nothing is recorded."""
        path = self.path_of(module)
        unknown = [tier for tier in tiers if tier not in TEST_TIERS]
        if unknown:
            raise UnknownTestTierError(path, unknown)
        without_tool = [tier for tier, tool in tiers.items() if not isinstance(tool, str) or not tool.strip()]
        if without_tool:
            raise TestToolRequiredError(path, without_tool)

        def kept(fields: SessionFields) -> None:
            recorded = fields.test_tiers
            fields.test_tiers = {**recorded, path: {**recorded.get(path, {}), **tiers}}

        said = ", ".join(f"{tier} {tool}" for tier, tool in tiers.items())
        self._session.record.update(kept, f"test tiers of {path}: {said}")
        return self.of(path)

    def path_of(self, module: str) -> str:
        """module as the record names it: its path from the project with forward slashes and no closing slash, so one
        module is never recorded under two spellings. The project's own folder is ``.``."""
        return PurePosixPath(module.replace("\\", "/")).as_posix().strip("/") or "."
