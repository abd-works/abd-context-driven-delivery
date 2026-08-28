# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - RecoverFromAManifestThatWontLoadHelper backed by the real
# manifest_gate module. Real: manifest_gate.run_manifests / handle_post_tool_use.
# Stubbed: the subprocess.run call the manifest command would otherwise make.

"""Domain tier test-helper for `Recover From A Manifest That Won't Load`."""

from __future__ import annotations

import subprocess
import sys
import tempfile
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

from recover_from_a_manifest_that_wont_load_story import (  # noqa: E402
    create_recover_from_a_manifest_that_wont_load_story,
)
import utilities.manifest_hook.manifest_gate as gate  # noqa: E402

_GATED_FILE = (
    '# @toolset-manifest python -m tools manifest a.b:C\n'
    '"""docstring."""\n'
)


class DomainHelper:
    def __init__(self) -> None:
        self._path: str = ""
        self._call_count = 0
        self._result: dict = {}
        self._patcher = None

    def _write_gated_file(self) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(_GATED_FILE)
            return fh.name

    # scenario 1: manifest succeeds on retry --------------------------------
    def given_manifest_errors_on_first_run(self) -> None:
        self._path = self._write_gated_file()
        self._call_count = 0

        def flaky_run(*args, **kwargs):
            self._call_count += 1
            if self._call_count == 1:
                raise subprocess.TimeoutExpired(cmd="manifest", timeout=30)
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok", stderr="")

        self._patcher = patch.object(subprocess, "run", side_effect=flaky_run)
        self._patcher.start()

    def when_gate_retries_up_to_two_times(self) -> None:
        self._result = gate.handle_post_tool_use({"file_path": self._path})
        self._patcher.stop()

    def then_manifest_succeeds_within_retries(self) -> None:
        assert self._call_count == 2, "expected exactly one retry before success"
        assert "ok" in self._result.get("additional_context", "")
        assert "FAILURE" not in self._result.get("user_message", "").upper()

    # scenario 2: every retry failing raises a loud notification ------------
    def given_manifest_still_fails_after_two_retries(self) -> None:
        self._path = self._write_gated_file()
        self._patcher = patch.object(
            subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(cmd="manifest", timeout=30),
        )
        self._patcher.start()

    def when_gate_gives_up_retrying(self) -> None:
        self._result = gate.handle_post_tool_use({"file_path": self._path})
        self._patcher.stop()

    def then_gate_raises_all_caps_failure_notification(self) -> None:
        message = self._result.get("user_message", "")
        assert message, "expected a user_message when every retry fails"
        assert message == message.upper(), "failure notification must be all-caps"
        assert "FAIL" in message


globals().update(create_recover_from_a_manifest_that_wont_load_story(DomainHelper()))
