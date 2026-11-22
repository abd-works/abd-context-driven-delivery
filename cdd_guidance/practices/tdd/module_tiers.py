"""ModuleTiers: the test tiers the tests of one fidelity show their modules use, recorded in the session the fidelity
works in, with what is left for the agent to decide."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.practices.tdd.tiers import recorded_tier_of, test_tool_of

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from harness.guidance.worked_session import WorkedSession

# The file that makes a folder a module: its card.
_MODULE_CARD = Path(".context") / "module-context.md"
# The tiers only a module that is an app uses, which no generate or render records without a test file that shows it.
_APP_TIERS = ("server", "web")
_RECORD_TOOL = "session.record_test_tier"


class ModuleTiers:
    """The test tiers of the modules one fidelity writes tests for, in the session it works in. A module is a folder
    that holds a module card. It reads the tier of each test file from the file's name and the module from the folder
    the file sits in, records what both say, and says what neither says, so the agent decides that and records it."""

    def __init__(self, fidelity: FidelityGuidance, session: WorkedSession) -> None:
        self._fidelity = fidelity
        self._session = session
        self._project = session.checkout.root.resolve()
        # What it could not tell, each a sentence that says what the agent records.
        self._undecided: list[str] = []

    def recorded_from(self, files: list[Path] | None) -> str:
        """Record the tiers files show, and the unit tier of each module the fidelity writes under, then answer what
        the session's record holds and what is left to decide. With no files, the files the fidelity has in the session
        that its branch changed are read. A tier a module's record already holds keeps the tool recorded for it."""
        held = self._session.test_tiers.recorded
        shown = self._shown_by(self._changed_files() if files is None else files)
        for module in self._modules_written_under():
            shown.setdefault(module, {}).setdefault("unit", self._tool_of_language("unit", module))
        for module, tiers in shown.items():
            new = {tier: tool for tier, tool in tiers.items() if tool and tier not in held.get(module, {})}
            if new:
                self._session.test_tiers.record(module, new)
        return self._said(list(shown))

    def _shown_by(self, files: list[Path]) -> dict[str, dict[str, str | None]]:
        """The tiers the test files among files show, by module, each with its test tool where the file says it. A test
        file under no module's folder, and one whose tool its name does not say, is left to the agent."""
        shown: dict[str, dict[str, str | None]] = {}
        for file in files:
            tier = recorded_tier_of(file.name)
            if tier is None:
                continue
            module, tool = self._module_of(file.parent), test_tool_of(tier, file.suffix)
            if module is None:
                self._undecided.append(f"{self._named(file)} is a test at the {tier} tier, under no module's folder: record the {tier} tier for the module it tests.")
            elif tool is None:
                self._undecided.append(f"{self._named(file)} is a test at the {tier} tier of {module}, and its name does not say its test tool: record the {tier} tier of {module} with the test tool the module's tests run with.")
                # The tier is shown with no tool, so the language the fidelity works in is not guessed for it.
                shown.setdefault(module, {}).setdefault(tier, None)
            else:
                shown.setdefault(module, {})[tier] = tool
        return shown

    def _tool_of_language(self, tier: str, module: str) -> str | None:
        """The test tool of the language the fidelity works in; where that does not say, the tier is left to the agent."""
        tool = test_tool_of(tier, self._fidelity.format.extension)
        if tool is None and not self._session.test_tiers.of(module).get(tier):
            self._undecided.append(f"{module} has no {tier} tier recorded, and {self._fidelity.format.name or 'the format chosen'} does not say its test tool: record the {tier} tier of {module} with the test tool the module's tests run with.")
        return tool

    def _changed_files(self) -> list[Path]:
        """The files the fidelity has in the session that are there and that the session's branch changed."""
        entries = (entry for listed in self._fidelity.session_output.written.files().values() for entry in listed)
        return [self._session.paths.path_named(entry.path) for entry in entries if entry.exists and entry.is_changed]

    def _modules_written_under(self) -> list[str]:
        """The module of each folder the fidelity writes under in the session; a folder in no module names none."""
        modules = (self._module_of(Path(root)) for root in self._fidelity.session_output.roots)
        return list(dict.fromkeys(module for module in modules if module))

    def _module_of(self, folder: Path) -> str | None:
        """The path from the project of the nearest folder, folder itself or one above it, that holds a module card;
        none for a folder outside the project or under no module. The project's own folder is no module: its card
        describes every module."""
        folder = folder.resolve()
        if self._project not in folder.parents:
            return None
        for candidate in (folder, *folder.parents):
            if candidate == self._project:
                return None
            if (candidate / _MODULE_CARD).is_file():
                return candidate.relative_to(self._project).as_posix()
        return None

    def _named(self, file: Path) -> str:
        resolved = file.resolve()
        return resolved.relative_to(self._project).as_posix() if self._project in resolved.parents else file.as_posix()

    def _said(self, modules: list[str]) -> str:
        """What the session's record holds for modules, and what the agent decides and records."""
        recorded = self._session.test_tiers.recorded
        held = [f"{module}: {', '.join(f'{tier} ({tool})' for tier, tool in recorded[module].items())}" for module in modules if recorded.get(module)]
        parts = ["### Test tiers of the module", self._held_line(held)]
        parts += [self._app_tiers_question(module, recorded.get(module, {})) for module in modules]
        parts += [f"{line} Call `{_RECORD_TOOL}` with the session, the module's folder, the tier and the test tool." for line in self._undecided]
        if not modules and not self._undecided:
            parts.append(
                f"This {self._fidelity.slug} writes under no module's folder, so this command cannot tell which module the "
                f"tests are for. Before you write a test, name the module (the folder that holds its `.context/module-context.md`) "
                f"and call `{_RECORD_TOOL}` with the unit tier and its test tool; record the server tier too when the "
                "module publishes operations through the cdd server or another server, and the web tier when it shows a page."
            )
        parts += [self._gone_report(module, tiers) for module, tiers in recorded.items() if not (self._project / module).is_dir()]
        parts.append("A story of a module whose record names the server or web tier has a test at that tier (`story-tested-at-each-recorded-tier`).")
        return "\n\n".join(part for part in parts if part)

    def _gone_report(self, module: str, tiers: dict[str, str]) -> str:
        """What to tell the person about a recorded module whose folder was renamed or deleted: the record is left as
        it is, since only they know whether the module moved or is gone."""
        held = ", ".join(f"{tier} ({tool})" for tier, tool in tiers.items())
        return (
            f"The record names {module}, whose folder is no longer there, with {held}. Tell the person: the record is "
            f"left as it is, and they remove it from `test_tiers` in session.json, or record the tiers again under the "
            f"module's new folder, because only they know whether the module moved or is gone."
        )

    def _held_line(self, held: list[str]) -> str:
        if not held:
            return "The session's session.json records no test tiers for the modules of this work yet (`test_tiers`)."
        return f"The session's session.json records the test tiers each module uses, each with its test tool (`test_tiers`): {'; '.join(held)}."

    def _app_tiers_question(self, module: str, tiers: dict[str, str]) -> str:
        """The question of the tiers module's record does not name, which only the module's code answers."""
        missing = [tier for tier in _APP_TIERS if tier not in tiers]
        if not missing:
            return ""
        asked = {
            "server": "publishes operations through the cdd server or another server (the server tier)",
            "web": "shows a page (the web tier)",
        }
        return (
            f"This command cannot tell whether {module} {' or '.join(asked[tier] for tier in missing)}: no test file of "
            f"that tier is there. Read the module's code and decide before you write its tests, and record each tier it "
            f"needs by calling `{_RECORD_TOOL}` with the session, {module}, the tier and the test tool."
        )
