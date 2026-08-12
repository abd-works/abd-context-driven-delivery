"""
# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
"""
# @agent-spec-manifest python -m tools agent-spec utilities/eval/agent_bdd_spec.py
# Agent reading this file: run via mamba (CLI cursor-agent harness).
# harness: cli
# session: utilities/eval/.context/.agent_bdd_sessions/eval-session-git.json
"""Agent BDD - real context-tool run + eval.Session finish_turn on this repo."""
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import be_true, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_tool,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)
from eval.session import WorkspaceRepo, _git, find_git_root

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_PROBE_NAME = "eval-agent-git-probe"


def _remove_worktree(repo_root: Path, wt: Path) -> None:
    if wt.exists():
        try:
            _git(repo_root, "worktree", "remove", "--force", str(wt))
        except RuntimeError:
            shutil.rmtree(wt, ignore_errors=True)
            try:
                _git(repo_root, "worktree", "prune")
            except RuntimeError:
                pass
    try:
        _git(repo_root, "branch", "-D", f"session/{_PROBE_NAME}")
    except RuntimeError:
        pass


with description("an eval Session"):
    with context("with a real context-tool run and git on this clone"):
        with it("records the tool run and commits the sandbox turn"):
            expect(_REPO_ROOT is not None).to(be_true)
            assert _REPO_ROOT is not None
            main_branch = WorkspaceRepo(_REPO_ROOT).current_branch()
            wt = Path(tempfile.mkdtemp(prefix="eval-agent-git-wt-"))
            shutil.rmtree(wt)
            _remove_worktree(_REPO_ROOT, wt)
            _git(
                _REPO_ROOT,
                "worktree",
                "add",
                "-b",
                f"session/{_PROBE_NAME}",
                str(wt),
                "HEAD",
            )
            probe = wt / "sandbox" / _PROBE_NAME
            probe.mkdir(parents=True)
            try:
                with agent(_REPO_ROOT, _SESSIONS / "eval-session-git.json"):
                    read_workspace("utilities/eval/session.py")
                    read_workspace("utilities/eval/.context/module-context.md")

                    response = run_toolset(
                        toolset="echo.echo:Echoer",
                        tool="fence",
                        arguments={"body": "eval session git probe"},
                        timeout_seconds=180,
                    )
                    expect_ok_tool(response, "fence")

                    report = follow_instructions(
                        "Prove eval.Session + real git on THIS clone's linked worktree.\n"
                        f"Worktree root: {wt.as_posix()}\n"
                        f"Working-area path: {probe.as_posix()}\n"
                        f"Session name: {_PROBE_NAME}\n"
                        "1. Using shell/python with PYTHONPATH covering utilities + "
                        "context_tools/actions + primitives, construct eval.Session "
                        "with WorkspaceRepo and CDDRepo BOTH rooted at the worktree "
                        "(same git root for workspace + tool).\n"
                        "2. record_tool_call a ToolCall(toolset='echo.echo:Echoer', "
                        "name='fence', summary='eval session git probe').\n"
                        "3. Write probe.txt under the working-area path with one short line.\n"
                        "4. finish_turn(prompt='agent-bdd', result='ok', context='sandbox').\n"
                        "5. Reply with a short plain-text report including exactly these lines:\n"
                        "BRANCH: <session branch>\n"
                        "CHANGE_COMMIT: <sha>\n"
                        "TOOL_SHA: <sha>\n"
                        "SESSION_YAML: <absolute path>\n"
                        "Do not delete the worktree or switch the main worktree branch.",
                        timeout_seconds=300,
                    ).text

                    yaml_path = (
                        probe / ".context" / "sessions" / _PROBE_NAME / "session.yaml"
                    )
                    expect(yaml_path.is_file()).to(be_true)
                    expect("BRANCH: session/" in report.replace("\\", "/")).to(be_true)
                    expect("CHANGE_COMMIT:" in report).to(be_true)
                    expect("TOOL_SHA:" in report).to(be_true)
                    expect("SESSION_YAML:" in report).to(be_true)
                    expect(WorkspaceRepo(_REPO_ROOT).current_branch()).to(
                        equal(main_branch)
                    )
                    expect(find_git_root(wt) is not None).to(be_true)

                    ai_judge(
                        report,
                        "The report documents a successful eval Session finish_turn "
                        "on a session/* branch with matching CHANGE_COMMIT and TOOL_SHA "
                        "from the same git clone, plus a SESSION_YAML path.",
                    )
            finally:
                _remove_worktree(_REPO_ROOT, wt)
                expect(WorkspaceRepo(_REPO_ROOT).current_branch()).to(equal(main_branch))
