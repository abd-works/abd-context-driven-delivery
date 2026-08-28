# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - SeeTheManifestRunAsItHappensHelper backed by the real
# manifest_gate hook handlers and the real CLI's _manifest_main.
# Real: manifest_gate_conf (patched to force mode), gate.handle_post_tool_use,
# tools.cli._ToolsCli. Stubbed: nothing - GatedWidget is a real, cheap toolset.

"""Domain tier test-helper for `See The Manifest Run As It Happens`."""

from __future__ import annotations

import io
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

_REPO_ROOT = Path(__file__).resolve().parents[6]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from see_the_manifest_run_as_it_happens_story import (  # noqa: E402
    create_see_the_manifest_run_as_it_happens_story,
)
from utilities.manifest_hook import manifest_gate_conf  # noqa: E402
from tools.cli import _ToolsCli  # noqa: E402
import utilities.manifest_hook.manifest_gate as gate  # noqa: E402

_GATED_WIDGET_TARGET = "tools.hooks.examples.gated_widget.gated_widget:GatedWidget"
_GATED_FILE = (
    f"# @toolset-manifest python -m tools manifest {_GATED_WIDGET_TARGET}\n"
    '"""docstring."""\n'
)


class DomainHelper:
    def __init__(self) -> None:
        self._path: str = ""
        self._mode_patcher = None
        self._result: dict = {}
        self._stdout = ""
        self._stderr = ""

    def _write_gated_file(self) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(_GATED_FILE)
            return fh.name

    def _stop_patcher(self) -> None:
        if self._mode_patcher is not None:
            self._mode_patcher.stop()
            self._mode_patcher = None

    # normal mode, hook-triggered run ---------------------------------------
    def given_normal_mode_active(self) -> None:
        self._mode_patcher = patch.object(manifest_gate_conf, "read_mode", return_value="normal")
        self._mode_patcher.start()

    def when_manifest_runs_via_hook(self) -> None:
        self._path = self._write_gated_file()
        self._result = gate.handle_post_tool_use({"file_path": self._path})

    def then_one_message_confirms_the_run(self) -> None:
        # Exact wording is still open (see the sketch) - what matters here is
        # that exactly one non-empty manifest-gate confirmation came back.
        message = self._result.get("user_message", "")
        assert message
        assert "manifest gate" in message.lower()
        assert "\n" not in message, "normal mode should be a single message, not a narration"
        self._stop_patcher()

    # normal mode, direct CLI call - no hook involved -----------------------
    def when_manifest_runs_via_direct_cli_call(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            _ToolsCli.instance().main(["manifest", _GATED_WIDGET_TARGET])
        self._stdout, self._stderr = out.getvalue(), err.getvalue()

    def then_cli_confirmation_still_appears(self) -> None:
        assert "ran" in self._stderr.lower()
        self._stop_patcher()

    # verbose mode, hook-triggered run --------------------------------------
    def given_verbose_mode_active(self) -> None:
        self._mode_patcher = patch.object(manifest_gate_conf, "read_mode", return_value="verbose")
        self._mode_patcher.start()

    def when_governed_asset_touched(self) -> None:
        self._path = self._write_gated_file()
        self._result = gate.handle_post_tool_use({"file_path": self._path})
        self._stop_patcher()

    def then_hook_firing_reported(self) -> None:
        assert "hook fired" in self._result.get("user_message", "").lower()

    def then_manifest_executing_reported(self) -> None:
        assert "executing" in self._result.get("user_message", "").lower()

    def then_manifest_loaded_reported(self) -> None:
        assert "manifest loaded" in self._result.get("user_message", "").lower()


globals().update(create_see_the_manifest_run_as_it_happens_story(DomainHelper()))
