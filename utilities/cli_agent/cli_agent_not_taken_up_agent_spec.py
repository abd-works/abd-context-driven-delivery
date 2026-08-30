# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_not_taken_up_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/cli_agent/.context/.agent_bdd_sessions/not-taken-up-48.json
"""Agent BDD — #48 NOT TAKEN UP false-negative / duplicate spawn (#48/#49).

Exercises the real CliAgent launch → pickup path (``_await_pickup`` not patched).
OS-boundary Popen/which/create_chat may be faked so the suite stays deterministic;
the pickup acceptance and existing-pid policy under test must run for real.
Stubbing out ``_await_pickup`` / ``_CliSpawner.start`` is not sufficient coverage.
"""
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from expects import be_false, be_true, equal, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir
from cli_agent.cli_agent import CliAgent, IdeCli, _CliSpawner

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


def _which_cursor(name: str) -> str | None:
    if name == "cursor-agent":
        return "/bin/cursor-agent"
    return None


def _popen(pid: int = 99):
    return SimpleNamespace(pid=pid)


with description("CliAgent launch when a doer is already live (#48)"):
    with context("when launch_sessions spawns and the transcript is slow"):
        with it(
            "should not raise NOT TAKEN UP while the spawned doer pid is still live"
        ):
            with agent(_REPO_ROOT, _SESSIONS / "not-taken-up-48.json"):
                tmp = Path(tempfile.mkdtemp(prefix="agent_bdd_48_"))
                live_pid = 515151

                def _kill(pid, _sig):
                    if int(pid) == live_pid:
                        return None
                    raise ProcessLookupError(pid)

                raised = None
                with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                    with patch(
                        "cli_agent.cli_agent.CursorCli._create_chat",
                        return_value="doer-agent-bdd-48",
                    ):
                        with patch(
                            "cli_agent.cli_agent.subprocess.Popen",
                            return_value=_popen(live_pid),
                        ):
                            with patch(
                                "cli_agent.cli_agent.os.kill", side_effect=_kill
                            ):
                                agent_under = CliAgent(
                                    workspace=str(tmp),
                                    session="agent-bdd-48",
                                )
                                agent_under._ide = IdeCli(pickup_seconds=0.0)
                                # Real _await_pickup — deliberately not patched.
                                try:
                                    agent_under.launch_sessions(
                                        tools=[], actions=None
                                    )
                                except RuntimeError as exc:
                                    raised = str(exc)

                expect(raised is None).to(be_true)

    with context("when an existing doer pid is already live before spawn"):
        with it("should not open a second console for the same resume"):
            with agent(_REPO_ROOT, _SESSIONS / "not-taken-up-48.json"):
                live_pid = 616161

                def _kill(pid, _sig):
                    if int(pid) == live_pid:
                        return None
                    raise ProcessLookupError(pid)

                with patch(
                    "cli_agent.cli_agent.subprocess.Popen", return_value=_popen(7)
                ) as spawned:
                    with patch("cli_agent.cli_agent.os.kill", side_effect=_kill):
                        result = _CliSpawner().start(
                            ["/bin/cursor-agent", "--resume", "same"],
                            tempfile.mkdtemp(prefix="agent_bdd_48_spawn_"),
                            existing_pid=live_pid,
                        )
                expect(spawned.called).to(be_false)
                expect(result.pid).to(equal(live_pid))

    with context("when the agent reads launch_sessions pickup guidance"):
        with it(
            "should tell operators not to respawn when a live doer already took the job"
        ):
            with agent(_REPO_ROOT, _SESSIONS / "not-taken-up-48.json"):
                launch = (
                    _REPO_ROOT / "utilities" / "cli_agent" / "cli_agent.py"
                ).read_text(encoding="utf-8")
                # Narrow to launch_sessions docstring / Legacy Steps — not the error string.
                legacy = (
                    launch.split("## Legacy Steps", 1)[-1].split("## ", 1)[0].lower()
                    if "## Legacy Steps" in launch
                    else ""
                )
                expect("not taken up" in legacy).to(be_true)
                # Must distinguish false-negative pickup from a true miss (no blind respawn).
                expect(
                    "already-running" in legacy
                    or "already running" in legacy
                    or "do not respawn" in legacy
                    or "live doer" in legacy
                    or "false-negative" in legacy
                    or "false negative" in legacy
                ).to(be_true)
