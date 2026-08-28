# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: agent - EditAGovernedAssetHelper backed by a live agent session.
# All five scenarios require a real Cursor agent to verify that the manifest
# gate fires and delivers guidance in the agent's context. There is no
# domain-tier substitute for scenarios 1-3 (the gate fires inside Cursor's
# hook pipeline, not in a subprocess call) and scenarios 4-5 probe real
# in-use source files that must not be mutated.
#
# Scenarios 1-3 use the disposable GatedWidget fixture and restore it after
# each test. Scenarios 4-5 are read-only probes against real source files.

"""Agent tier test-helper for `Edit A Governed Asset`."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[6]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from agent_bdd import agent, instruct  # noqa: E402
from agent_bdd.spec_helpers import repo_root_from, sessions_dir  # noqa: E402
from expects import contain, expect  # noqa: E402

from edit_a_governed_asset_story import (  # noqa: E402
    create_edit_a_governed_asset_story,
)

_SESSIONS = sessions_dir(__file__)
_FIXTURE_PY = "primitives/tools/hooks/examples/gated_widget/gated_widget.py"
_FIXTURE_ABS = _REPO_ROOT / _FIXTURE_PY
_BDD_SOURCE = "context_tools/bdd/bdd.py"
_ASSETS_SOURCE = "primitives/assets/assets.py"


class AgentHelper:
    """Implements EditAGovernedAssetHelper via live agent sessions."""

    def __init__(self) -> None:
        self._fixture_original: str = ""
        self._result_text: str = ""
        self._second_result_text: str = ""
        self._session_ctx = None

    def _open_session(self, session_file: str) -> None:
        self._session_ctx = agent(_REPO_ROOT, _SESSIONS / session_file)
        self._session_ctx.__enter__()

    def _close_session(self) -> None:
        if self._session_ctx is not None:
            self._session_ctx.__exit__(None, None, None)
            self._session_ctx = None

    def _restore_fixture(self) -> None:
        if self._fixture_original:
            _FIXTURE_ABS.write_text(self._fixture_original, encoding="utf-8")
            self._fixture_original = ""

    # ---- scenario 1: first touch delivers guidance -------------------------

    def given_a_governed_asset_not_yet_touched_this_chat(self) -> None:
        self._fixture_original = _FIXTURE_ABS.read_text(encoding="utf-8")
        self._open_session("first-touch.json")

    def when_agent_reads_the_asset(self) -> None:
        result = instruct(
            f"Read {_FIXTURE_PY} from the workspace. Report back exactly what came "
            f"back with the read - including any system_reminder, agent_message, or "
            f"MANIFEST GATE text you saw - verbatim.",
            timeout_seconds=150,
        )
        self._result_text = result.text

    def then_governing_toolset_guidance_is_delivered(self) -> None:
        try:
            expect(self._result_text).to(contain("MANIFEST GATE"))
        finally:
            self._close_session()
            self._restore_fixture()

    # ---- scenario 2: edit proceeds directly on that same touch -------------

    def when_agent_edits_the_asset(self) -> None:
        result = instruct(
            f"Using the edit tool, append a one-line comment `# probe` to the end of "
            f"{_FIXTURE_PY}. Do not run `python -m tools run` or any manifest command "
            f"first - go straight to the edit. Then state literally, on its own line, "
            f"either `RESULT: EDIT SUCCEEDED` or `RESULT: EDIT BLOCKED` depending on "
            f"what actually happened, and quote any `permission`, `agent_message`, or "
            f"`user_message` fields you saw, verbatim.",
            timeout_seconds=150,
        )
        self._result_text = result.text

    def then_edit_proceeds_directly_without_a_compliance_step(self) -> None:
        try:
            expect(self._result_text).to(contain("RESULT: EDIT SUCCEEDED"))
            expect(self._result_text).not_to(contain("EDIT BLOCKED"))
        finally:
            self._close_session()
            self._restore_fixture()

    # ---- scenario 3: repeat touch refers back to guidance already in context

    def given_the_same_asset_with_guidance_already_in_context(self) -> None:
        self._fixture_original = _FIXTURE_ABS.read_text(encoding="utf-8")
        self._open_session("repeat-touch.json")

    def when_agent_touches_the_asset_again(self) -> None:
        first = instruct(
            f"Using the edit tool, append a one-line comment `# probe-1` to the end "
            f"of {_FIXTURE_PY}. Then state literally `RESULT: EDIT SUCCEEDED` or "
            f"`RESULT: EDIT BLOCKED` depending on what actually happened.",
            timeout_seconds=240,
        )
        second = instruct(
            f"Using the edit tool, append a further one-line comment `# probe-2` to "
            f"the end of {_FIXTURE_PY} - the same file you just edited a moment ago "
            f"in this same chat. Then state literally `RESULT: EDIT SUCCEEDED` or "
            f"`RESULT: EDIT BLOCKED` depending on what actually happened.",
            timeout_seconds=240,
        )
        self._result_text = first.text
        self._second_result_text = second.text

    def then_edit_still_proceeds_directly(self) -> None:
        try:
            expect(self._result_text).to(contain("RESULT: EDIT SUCCEEDED"))
            expect(self._second_result_text).to(contain("RESULT: EDIT SUCCEEDED"))
            expect(self._second_result_text).not_to(contain("EDIT BLOCKED"))
        finally:
            self._close_session()
            self._restore_fixture()

    # ---- scenario 4: a governing tool's own source is itself governed ------

    def given_a_context_tools_own_source_file(self) -> None:
        self._open_session("recursive-governance.json")

    def when_agent_reads_that_context_tools_source(self) -> None:
        result = instruct(
            f"Read {_BDD_SOURCE} from the workspace. Report back exactly what came "
            f"back with the read - including any system_reminder, agent_message, or "
            f"MANIFEST GATE text you saw - verbatim. Do not edit the file.",
            timeout_seconds=150,
        )
        self._result_text = result.text

    def then_gate_delivers_that_tools_own_governing_guidance(self) -> None:
        try:
            expect(self._result_text).to(contain("MANIFEST GATE"))
            expect(self._result_text.lower()).to(contain("bdd"))
        finally:
            self._close_session()

    # ---- scenario 5: base primitives are governed too ----------------------

    def given_a_base_primitives_own_source_file(self) -> None:
        self._open_session("base-primitive-governance.json")

    def when_agent_reads_that_base_primitive(self) -> None:
        result = instruct(
            f"Read {_ASSETS_SOURCE} from the workspace. Report back exactly what came "
            f"back with the read - including any system_reminder, agent_message, or "
            f"MANIFEST GATE text you saw - verbatim. Do not edit the file.",
            timeout_seconds=150,
        )
        self._result_text = result.text

    def then_gate_still_delivers_its_governing_guidance(self) -> None:
        try:
            expect(self._result_text).to(contain("MANIFEST GATE"))
        finally:
            self._close_session()


globals().update(create_edit_a_governed_asset_story(AgentHelper()))
