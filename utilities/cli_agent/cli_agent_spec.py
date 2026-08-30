"""BDD spec for utilities/cli_agent/cli_agent.py â€” IdeCli, CliAgent, workspace sessions.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest â€” slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import json
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_below, be_false, be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from cli_agent.cli_agent import (
    CliAgent,
    CliBacklog,
    CliBacklogItem,
    CursorCli,
    IdeCli,
    VscodeCli,
    _CliAgentLog,
    _CliSpawner,
    JobQueue,
    _Pickup,
    _TranscriptWatch,
    _pid_alive,
)
from sub_agent.sub_agent import discover_sub_agent_tools
from workspace.workspace import Workspace, WorkSession


def _which_cursor(name: str) -> str | None:
    if name == "cursor-agent":
        return "/bin/cursor-agent"
    return None


def _which_agent_only(name: str) -> str | None:
    if name == "agent":
        return "/bin/agent"
    return None


def _cli_agent_log_records(work):
    path = _CliAgentLog().path_for(work)
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _which_code_only(name: str) -> str | None:
    if name == "code":
        return "/bin/code"
    return None


def _which_insiders_only(name: str) -> str | None:
    if name == "code-insiders":
        return "/bin/code-insiders"
    return None


def _which_both(name: str) -> str | None:
    if name == "cursor-agent":
        return "/bin/cursor-agent"
    if name == "code":
        return "/bin/code"
    return None


def _which_none(_name: str) -> str | None:
    return None


def _create_chat_ids(*ids: str):
    leftover = list(ids)

    def _create(
        self, workspace: str, *, timeout_seconds: int = IdeCli.create_chat_timeout_seconds
    ) -> str:
        return leftover.pop(0)

    return _create


def _cli_file(root: Path, name: str) -> Path:
    return root / ".context" / "sessions" / name / "cli-agent.json"


def _read_cli(root: Path, name: str) -> dict:
    return json.loads(_cli_file(root, name).read_text(encoding="utf-8"))


_SPAWN_PID = 4242
_CURSOR_PID = 99
_CODE_PID = 77


def _popen(pid: int = _SPAWN_PID):
    return SimpleNamespace(pid=pid)


def _run_agent(**kwargs) -> CliAgent:
    workspace = kwargs.pop("workspace", "")
    session = kwargs.pop("session", "")
    prompt = kwargs.pop("prompt", "")
    missing = object()
    tools = kwargs.pop("tools", missing)
    actions = kwargs.pop("actions", None)
    if tools is missing:
        tools = ["Stories"] if kwargs.get("judge") else []
    ide = IdeCli(**kwargs)
    if prompt:
        ide._prompt = prompt
    with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
        with patch("cli_agent.cli_agent.subprocess.Popen", return_value=_popen()):
            with patch.object(CliAgent, "_await_pickup", lambda *a, **k: None):
                agent = CliAgent(workspace=workspace, session=session)
                agent._ide = ide
                agent.launch_sessions(tools=tools, actions=actions)
                return agent


with description("IdeCli"):
    with context("after it is constructed with flags"):
        with it("should expose those flags as properties"):
            cli = IdeCli(model="gpt", mode="fast", agent_mode="plan", judge=True)
            expect(cli.model).to(equal("gpt"))
            expect(cli.mode).to(equal("fast"))
            expect(cli.agent_mode).to(equal("plan"))
            expect(cli.judge).to(be_true)

    with context("when detecting a vendor"):
        with it("should prefer CursorCli when both CLIs are on PATH"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_both):
                cli = IdeCli()._detect()
            expect(cli).to(be_a(CursorCli))

        with it("should detect VscodeCli when only code is on PATH"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                cli = IdeCli()._detect()
            expect(cli).to(be_a(VscodeCli))

        with it("should raise when no IDE CLI is on PATH"):
            def _detect():
                with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_none):
                    IdeCli()._detect()

            expect(_detect).to(raise_error(RuntimeError))

    with context("that writes a task prompt"):
        with it("should bind tools and one action onto a workspace Turn"):
            cli = IdeCli()
            hanging = cli._bind_turn(
                cli._blank_turn(),
                [
                    {
                        "toolset": "context_tools.stories.stories:Stories",
                        "context": {"fidelity": "scenarios", "format": "markdown"},
                    },
                    {
                        "toolset": "context_tools.clean_engineering.clean_engineering:CleanEngineering",
                        "context": {"fidelity": "model", "format": "markdown"},
                    },
                ],
                "generate.generate:Generate",
            )
            expect(hanging.action).to(equal("Generate"))
            expect(len(hanging.tool_keys)).to(equal(2))
            expect(len(hanging.tool_calls)).to(equal(2))
            expect(hanging.tool_calls[0].name).to(equal("Generate"))
            expect(hanging.tool_calls[1].name).to(equal("Generate"))
            text = cli._turn_prompt(hanging)
            expect(text).to(contain("Turn.action: Generate"))
            expect(text).to(contain("Turn.tool_keys:"))
            expect(text).to(contain("Turn.toolCalls:"))
            expect(text).to(contain("fidelity=scenarios"))
            expect(text).to(contain("fidelity=model"))
            expect(text).to(contain("format=markdown"))

        with it("should open a Turn when no tools and no action are passed"):
            cli = IdeCli()
            hanging = cli._bind_turn(cli._blank_turn(), [], None)
            expect(hanging.action).to(equal(""))
            expect(hanging.tool_keys).to(equal([]))
            expect(hanging.tool_calls).to(equal([]))
            expect(cli._turn_prompt(hanging)).to(contain("Turn.action: (none)"))

        with it("should keep a utility action with no context tools"):
            cli = IdeCli()
            hanging = cli._bind_turn(cli._blank_turn(), [], "handoff.handoff:Handoff")
            expect(hanging.action).to(equal("Handoff"))
            expect(hanging.tool_keys).to(equal([]))
            expect(cli._turn_prompt(hanging)).to(contain("Turn.action: Handoff"))

        with it("should keep prose on Turn.prompt instead of loading it as a toolset"):
            cli = IdeCli()
            hanging = cli._bind_turn(cli._blank_turn(), ["summarize the session"], None)
            expect(hanging.action).to(equal(""))
            expect(hanging.tool_keys).to(equal([]))
            expect(hanging.prompt).to(equal("summarize the session"))
            expect(cli._turn_prompt(hanging)).to(contain("Turn.prompt: summarize the session"))

        with it("should treat a prompt as the Turn when actions is prose"):
            cli = IdeCli()
            hanging = cli._bind_turn(cli._blank_turn(), [], "summarize the session")
            expect(hanging.action).to(equal(""))
            expect(hanging.prompt).to(equal("summarize the session"))
            expect(cli._turn_prompt(hanging)).to(contain("Turn.action: (none)"))
            expect(cli._turn_prompt(hanging)).to(contain("Turn.prompt: summarize the session"))

        with it("should offer later items as guidance and leave the next Turn to the CLI"):
            cli = IdeCli()
            hanging = cli._bind_turn(
                cli._blank_turn(),
                ["context_tools.stories.stories:Stories"],
                "sketch.sketch:Sketch",
            )
            text = cli._turn_prompt(hanging, ["generate.generate:Generate"])
            expect(text).to(contain("Turn.action: Sketch"))
            expect(text).to(contain("guidance"))
            expect(text).to(contain("Guidance: Generate"))
            expect(text).to(contain(cli._next_turn))
            expect(text).not_to(contain("Next Turn.action:"))
            extra = cli._turn_prompt(
                hanging, ["handoff.handoff:Handoff", "write a one-line status"]
            )
            expect(extra).to(contain("Guidance: Handoff"))
            expect(extra).to(contain("Guidance: write a one-line status"))

        with it("should copy generate lenses onto judge validate tools"):
            generate = [
                {
                    "toolset": "context_tools.stories.stories:Stories",
                    "context": {"fidelity": "scenarios", "format": "markdown"},
                },
                {
                    "toolset": "context_tools.clean_engineering.clean_engineering:CleanEngineering",
                    "context": {"fidelity": "model", "format": "markdown"},
                },
            ]
            cli = IdeCli()
            aligned = cli._align_tools(
                [
                    "context_tools.stories.stories:Stories",
                    "context_tools.clean_engineering.clean_engineering:CleanEngineering",
                ],
                generate,
            )
            expect(cli._tool_lens(aligned[0])["fidelity"]).to(equal("scenarios"))
            expect(cli._tool_lens(aligned[1])["fidelity"]).to(equal("model"))
            expect(cli._tool_lens(aligned[0])["format"]).to(equal("markdown"))
            expect(cli._lens_label(aligned[1])).to(contain("fidelity=model"))

        with it("should tell the judge to validate at those same lenses"):
            cli = IdeCli(
                judge={
                    "tools": [
                        "context_tools.stories.stories:Stories",
                        "context_tools.clean_engineering.clean_engineering:CleanEngineering",
                    ],
                    "actions": ["validate.validate:Validate"],
                }
            )
            generate = [
                {
                    "toolset": "context_tools.stories.stories:Stories",
                    "context": {"fidelity": "scenarios", "format": "markdown"},
                },
                {
                    "toolset": "context_tools.clean_engineering.clean_engineering:CleanEngineering",
                    "context": {"fidelity": "model", "format": "markdown"},
                },
            ]
            text = cli._judge_task_prompt(generate_tools=generate)
            expect(text).to(contain("fidelity=scenarios"))
            expect(text).to(contain("fidelity=model"))
            expect(text).to(contain("format=markdown"))
            expect(text).to(contain(cli._judge_reply_to_doer))
            expect(text).to(contain(cli._validate_same_lens))
            expect(text).to(contain(cli.source_scope))
            expect(text).to(contain("Turn.action: Validate"))
            expect(text.index(cli._judge_reply_to_doer)).to(
                be_below(text.index(cli._validate_same_lens))
            )

        with it("should give the judge the original job as source scope"):
            cli = IdeCli(judge=True)
            hanging = cli._bind_turn(
                cli._blank_turn(),
                [
                    {
                        "toolset": "context_tools.stories.stories:Stories",
                        "context": {"fidelity": "scenarios", "format": "markdown"},
                    }
                ],
                "generate.generate:Generate",
            )
            hanging.prompt = "scenarios for the story map"
            worker = cli._turn_prompt(hanging)
            text = cli._judge_task_prompt(
                worker, generate_tools=hanging.tool_keys, turn=hanging
            )
            expect(text).to(contain(cli._judge_reply_to_doer))
            expect(text).to(contain(cli.source_scope))
            expect(text).to(contain("--- JOB / SOURCE SCOPE ---"))
            expect(text).to(contain("scenarios for the story map"))


with description("CursorCli"):
    with context("that finds a launcher"):
        with it("should prefer cursor-agent over agent"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                expect(CursorCli()._launcher()).to(equal("/bin/cursor-agent"))

        with it("should fall back to agent"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_agent_only):
                expect(CursorCli()._launcher()).to(equal("/bin/agent"))

    with context("that builds interactive-session argv"):
        with it("should pass trust, workspace, model, and plan"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(model="sonnet", agent_mode="plan")._command(
                    "do the work", "/ws"
                )
            expect(argv).to(
                equal(
                    [
                        "/bin/cursor-agent",
                        "--force",
                        "--trust",
                        "--workspace",
                        "/ws",
                        "--model",
                        "sonnet",
                        "--mode",
                        "plan",
                        "do the work",
                    ]
                )
            )
            expect("-p" in argv).to(be_false)

        with it("should never pass print-mode flags"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(
                    model="sonnet", agent_mode="plan", print_mode=True
                )._command("do the work", "/ws")
            expect("-p" in argv).to(be_false)
            expect("stream-json" in argv).to(be_false)
            expect(argv).to(contain("--force"))

        with it("should map mode fast onto the Cursor model override"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(model="sonnet", mode="fast")._command("go", ".")
            expect(argv).to(contain("sonnet[fast=true]"))

        with it("should map mode medium onto fast=false"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(model="gpt-5", mode="medium")._command("go", ".")
            expect(argv).to(contain("gpt-5[fast=false]"))

        with it("should leave an already parameterized model alone"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(
                    model="opus[effort=high]", mode="fast"
                )._command("go", ".")
            expect(argv).to(contain("opus[effort=high]"))
            expect("opus[effort=high][fast=true]" in argv).to(be_false)

        with it("should omit --mode when agent_mode is agent"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(agent_mode="agent")._command("go", ".")
            expect("--mode" in argv).to(be_false)

        with it("should pass --resume when resume is set"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(resume="chat-123")._command("go", "/ws")
            expect(argv).to(contain("--resume"))
            expect(argv).to(contain("chat-123"))

        with it("should raise when cursor-agent is missing"):
            def _command():
                with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_none):
                    CursorCli()._command("go", ".")

            expect(_command).to(raise_error(RuntimeError))

    with context("that is asked for a judge session"):
        with it("should use the instance agent_mode on judge_command"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(agent_mode="plan")._judge_command("grade it", "/ws")
            expect(argv).to(contain("--mode"))
            expect(argv).to(contain("plan"))
            expect(argv[-1]).to(equal("grade it"))

        with it("should write the judge file and return only the worker argv"):
            tmp = tempfile.mkdtemp(prefix="cli_cmd_")
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(judge=True, agent_mode="plan")._commands(
                    "do work", tmp, judge_prompt="grade it"
                )
            expect(len(argv)).to(equal(1))
            expect(argv[0][-1]).to(contain("cli-agent-task.txt"))
            expect(argv[0]).to(contain("plan"))
            expect(
                (Path(tmp) / ".context" / "cli-agent-task.txt").read_text(
                    encoding="utf-8"
                )
            ).to(contain("do work"))
            expect(
                (Path(tmp) / ".context" / "cli-agent-judge.txt").read_text(
                    encoding="utf-8"
                )
            ).to(contain("grade it"))

        with it("should return only the worker when judge is false"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli()._commands("do work", "/ws")
            expect(len(argv)).to(equal(1))

    with context("that spawns cursor-agent"):
        with it("should Popen an interactive session"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch(
                    "cli_agent.cli_agent.subprocess.Popen", return_value=_popen(_CURSOR_PID)
                ) as spawned:
                    result = CursorCli(model="sonnet")._launch_cli("do work", "/ws")
            expect(spawned.called).to(be_true)
            argv = spawned.call_args[0][0]
            expect(argv[0]).to(equal("/bin/cursor-agent"))
            expect("-p" in argv).to(be_false)
            expect(argv).to(contain("--force"))
            expect(argv).to(contain("do work"))
            expect(result.exit_code).to(equal(0))
            expect(result.pid).to(equal(99))
            expect(result.text).to(equal("pid: 99"))

        with it("should subprocess.run create-chat"):
            completed = SimpleNamespace(
                returncode=0,
                stdout="created 11111111-1111-1111-1111-111111111111\n",
                stderr="",
            )
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch(
                    "cli_agent.cli_agent.subprocess.run", return_value=completed
                ) as spawned:
                    chat_id = CursorCli()._create_chat("/ws")
            expect(chat_id).to(equal("11111111-1111-1111-1111-111111111111"))
            expect(spawned.call_args[0][0]).to(contain("create-chat"))


with description("VscodeCli"):
    with context("that finds a launcher"):
        with it("should use code when present"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                expect(VscodeCli()._launcher()).to(equal("/bin/code"))

        with it("should fall back to code-insiders"):
            with patch(
                "cli_agent.cli_agent.shutil.which", side_effect=_which_insiders_only
            ):
                expect(VscodeCli()._launcher()).to(equal("/bin/code-insiders"))

    with context("that builds code chat argv"):
        with it("should open the workspace folder then chat in a new window"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(agent_mode="agent")._command("do the work", "/ws")
            expect(argv).to(
                equal(
                    [
                        "/bin/code",
                        "/ws",
                        "chat",
                        "--new-window",
                        "--mode",
                        "agent",
                        "do the work",
                    ]
                )
            )

        with it("should map ask to --mode ask"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(agent_mode="ask")._command("review", "/ws")
            expect(argv).to(contain("ask"))

        with it("should map plan to --mode agent"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(agent_mode="plan")._command("design", "/ws")
            expect(argv).to(contain("agent"))
            expect("plan" in argv).to(be_false)

        with it("should map edit to --mode edit"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(agent_mode="edit")._command("tweak", "/ws")
            expect(argv).to(contain("edit"))

        with it("should not invent a --model flag"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(model="gpt")._command("go", "/ws")
            expect("--model" in argv).to(be_false)

        with it("should raise when code is missing"):
            def _command():
                with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_none):
                    VscodeCli()._command("go", "/ws")

            expect(_command).to(raise_error(RuntimeError))

    with context("that is asked for a judge session"):
        with it("should use the instance agent mode on judge_command"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(agent_mode="agent")._judge_command("grade it", "/ws")
            expect(argv).to(contain("agent"))
            expect(argv[-1]).to(equal("grade it"))

        with it("should write the judge file and return only the worker argv"):
            tmp = tempfile.mkdtemp(prefix="cli_vscmd_")
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                argv = VscodeCli(judge=True)._commands(
                    "do work", tmp, judge_prompt="grade it"
                )
            expect(len(argv)).to(equal(1))
            expect(argv[0][-1]).to(contain("cli-agent-task.txt"))
            expect(
                (Path(tmp) / ".context" / "cli-agent-task.txt").read_text(
                    encoding="utf-8"
                )
            ).to(contain("do work"))
            expect(
                (Path(tmp) / ".context" / "cli-agent-judge.txt").read_text(
                    encoding="utf-8"
                )
            ).to(contain("grade it"))

    with context("that spawns code chat"):
        with it("should Popen the chat argv"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_code_only):
                with patch(
                    "cli_agent.cli_agent.subprocess.Popen", return_value=_popen(_CODE_PID)
                ) as spawned:
                    result = VscodeCli(agent_mode="ask")._launch_cli("review", "/ws")
            argv = spawned.call_args[0][0]
            expect(argv[0]).to(equal("/bin/code"))
            expect(argv).to(contain("chat"))
            expect(result.pid).to(equal(77))
            expect(result.text).to(equal("pid: 77"))


with description("CliAgent"):
    with context("that has its ide set directly"):
        with it("should hold those flags on ide for later runs"):
            agent = CliAgent()
            agent._ide = IdeCli(model="gpt", mode="medium", agent_mode="plan", judge=True)
            expect(agent.ide.model).to(equal("gpt"))
            expect(agent.ide.mode).to(equal("medium"))
            expect(agent.ide.agent_mode).to(equal("plan"))
            expect(agent.ide.judge).to(be_true)

    with context("that has no ide set"):
        with it("should detect the IDE lazily on first access"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                agent = CliAgent()
                ide = agent.ide
            expect(ide).to(be_a(CursorCli))

    with context("that has a task prompt set"):
        with it("should expose and update it via task_prompt"):
            agent = CliAgent()
            agent._ide = IdeCli()
            agent.task_prompt = "do the thing"
            expect(agent.task_prompt).to(equal("do the thing"))

    with context("launch_sessions"):
        with it("should mark launch_sessions as a sub_agent"):
            expect(getattr(CliAgent.launch_sessions, "_is_sub_agent", False)).to(be_true)

        with it("should publish kind sub_agent and launch non_blocking"):
            entry = discover_sub_agent_tools(CliAgent())[
                "launch_sessions"
            ].signature_entry
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))

        with it("should take tools and optional actions only"):
            params = discover_sub_agent_tools(CliAgent())[
                "launch_sessions"
            ].signature_entry["parameters"]
            expect("tools" in params).to(be_true)
            expect("actions" in params).to(be_true)
            expect("model" in params).to(be_false)

        with it("should tell the parent to prefer run_backlog and a minimal monitor contract"):
            text = discover_sub_agent_tools(CliAgent())[
                "launch_sessions"
            ].instructions
            expect("non-blocking" in text.lower() or "run_backlog" in text).to(be_true)
            expect("CliAgent" in text).to(be_true)
            expect("run_backlog" in text).to(be_true)
            expect("NOT TAKEN UP" in text or "not taken up" in text.lower()).to(be_true)
            expect("report back to the user" in text).to(be_true)
            expect("enqueue_jobs" in text or "Enqueue" in text).to(be_true)
            expect("complete_job" in text).to(be_true)
            expect("never launches, prompts, or scores the judge" in text or "never launches, prompts, or scores the judge" in text.lower() or "parent never launches" in text).to(be_true)

        with it("should Popen cursor-agent from run"):
            tmp = tempfile.mkdtemp(prefix="cli_run_")
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    return_value="11111111-1111-1111-1111-111111111111",
                ):
                    with patch(
                        "cli_agent.cli_agent.subprocess.Popen",
                        return_value=_popen(_SPAWN_PID),
                    ) as spawned:
                        with patch.object(CliAgent, "_await_pickup", lambda *a, **k: None):
                            text = CliAgent(
                                workspace=tmp, session="run-spec"
                            ).launch_sessions(tools=[], actions=None)
            expect(spawned.called).to(be_true)
            expect(spawned.call_args[0][0][0]).to(equal("/bin/cursor-agent"))
            expect("-p" in spawned.call_args[0][0]).to(be_false)
            expect(spawned.call_args[0][0][-1]).to(contain("cli-agent-task.txt"))
            expect("pid: 4242" in text).to(be_true)
            expect(
                "cursor-agent --resume 11111111-1111-1111-1111-111111111111" in text
            ).to(be_true)
            expect(
                "[CliAgent doer transcript](11111111-1111-1111-1111-111111111111)" in text
            ).to(be_true)
            expect("CLI processes (not IDE chats):" in text).to(be_true)
            expect("session: run-spec" in text).to(be_true)
            expect("taken up: yes" in text).to(be_true)
            expect("NOT TAKEN UP" in text).to(be_false)

        with it("should tell the parent to stop when the doer does not take the job"):
            text = discover_sub_agent_tools(CliAgent())[
                "launch_sessions"
            ].instructions
            expect("NOT TAKEN UP" in text).to(be_true)
            expect("stop immediately" in text).to(be_true)


with description("a CLI agent run"):
    with context("that has a doer session"):
        with it("should associate the doer session with the workspace session"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_assoc_"))
            with patch(
                "cli_agent.cli_agent.CursorCli._create_chat",
                _create_chat_ids("doer-1"),
            ):
                agent = _run_agent(workspace=str(tmp), session="sprint-a")
            work = agent.work_session
            expect(work.name).to(equal("sprint-a"))
            expect(work.cli_doer).to(equal("doer-1"))
            expect(_read_cli(tmp, "sprint-a")["doer"]).to(equal("doer-1"))

        with context("when the launch has no tools and no actions"):
            with it("should not bind a judge or tell the doer to contact one"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_no_judge_"))
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-1", "judge-should-not"),
                ):
                    agent = _run_agent(
                        workspace=str(tmp),
                        session="sprint-a",
                        judge=True,
                        tools=[],
                        actions=None,
                    )
                expect(agent.work_session.cli_doer).to(equal("doer-1"))
                expect(agent.work_session.cli_judge).to(equal(""))
                task = (tmp / ".context" / "cli-agent-task.txt").read_text(
                    encoding="utf-8"
                )
                expect("contact the judge" in task).to(be_false)
                expect(
                    (tmp / ".context" / "cli-agent-judge.txt").exists()
                ).to(be_false)

        with context("that also has a judge task"):
            with it("should tell the doer to contact the bound judge"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_judge_"))
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-1", "judge-1"),
                ):
                    agent = _run_agent(
                        workspace=str(tmp),
                        session="sprint-a",
                        judge="you must validate X",
                    )
                expect(agent.work_session.cli_judge).to(equal("judge-1"))
                expect(agent.ide.judge_resume).to(equal("judge-1"))
                task = (tmp / ".context" / "cli-agent-task.txt").read_text(
                    encoding="utf-8"
                )
                expect(task).to(contain("judge-1"))
                expect(task).to(contain("parent is not in this loop"))
                expect(
                    (tmp / ".context" / "cli-agent-judge.txt").read_text(
                        encoding="utf-8"
                    )
                ).to(contain("you must validate X"))

            with it("should associate the judge session with the same workspace session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_same_"))
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-1", "judge-1"),
                ):
                    agent = _run_agent(
                        workspace=str(tmp),
                        session="sprint-a",
                        judge=True,
                    )
                cli_record = _read_cli(tmp, "sprint-a")
                expect(cli_record["doer"]).to(equal("doer-1"))
                expect(cli_record["judge"]).to(equal("judge-1"))
                expect(agent.work_session.name).to(equal("sprint-a"))


with description("a workspace session"):
    with context("that is open"):
        with context("that is asked to run the agent CLI"):
            with it("should attach the doer session to that workspace session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_open_"))
                opened = Workspace(str(tmp)).open_work_session("already-open")
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-open"),
                ):
                    agent = _run_agent(workspace=str(tmp), session="already-open")
                expect(agent.work_session.name).to(equal(opened.name))
                expect(agent.work_session.cli_doer).to(equal("doer-open"))
                expect(agent.ide.resume).to(equal("doer-open"))

            with context("that has a judge task"):
                with it("should attach the judge session to that workspace session"):
                    tmp = Path(tempfile.mkdtemp(prefix="cli_open_j_"))
                    Workspace(str(tmp)).open_work_session("already-open")
                    with patch(
                        "cli_agent.cli_agent.CursorCli._create_chat",
                        _create_chat_ids("doer-open", "judge-open"),
                    ):
                        agent = _run_agent(
                            workspace=str(tmp),
                            session="already-open",
                            judge=True,
                        )
                    expect(agent.work_session.cli_judge).to(equal("judge-open"))

        with context("that runs the agent CLI again"):
            with it("should reuse the same doer session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_reuse_"))
                Workspace(str(tmp)).open_work_session("keep")
                chats = []

                def _create(self, workspace: str, *, timeout_seconds: int = IdeCli.create_chat_timeout_seconds) -> str:
                    chats.append("x")
                    return f"id-{len(chats)}"

                with patch("cli_agent.cli_agent.CursorCli._create_chat", _create):
                    first = _run_agent(workspace=str(tmp), session="keep")
                    second = _run_agent(workspace=str(tmp), session="keep")
                expect(len(chats)).to(equal(1))
                expect(second.work_session.cli_doer).to(equal(first.work_session.cli_doer))

            with context("that has a judge task"):
                with it("should reuse the same judge session"):
                    tmp = Path(tempfile.mkdtemp(prefix="cli_reuse_j_"))
                    Workspace(str(tmp)).open_work_session("keep")
                    chats = []

                    def _create(self, workspace: str, *, timeout_seconds: int = IdeCli.create_chat_timeout_seconds) -> str:
                        chats.append("x")
                        return f"id-{len(chats)}"

                    with patch("cli_agent.cli_agent.CursorCli._create_chat", _create):
                        first = _run_agent(
                            workspace=str(tmp), session="keep", judge=True
                        )
                        second = _run_agent(
                            workspace=str(tmp), session="keep", judge=True
                        )
                    expect(len(chats)).to(equal(2))
                    expect(second.work_session.cli_judge).to(
                        equal(first.work_session.cli_judge)
                    )

        with context("that is closed"):
            with it("should close the doer session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_close_"))
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-close"),
                ):
                    agent = _run_agent(workspace=str(tmp), session="closing")
                agent.work_session.close()
                expect(agent.work_session.cli_doer).to(equal(""))
                expect(_cli_file(tmp, "closing").is_file()).to(be_false)

            with context("that had a judge session"):
                with it("should close the judge session"):
                    tmp = Path(tempfile.mkdtemp(prefix="cli_close_j_"))
                    with patch(
                        "cli_agent.cli_agent.CursorCli._create_chat",
                        _create_chat_ids("doer-close", "judge-close"),
                    ):
                        agent = _run_agent(
                            workspace=str(tmp), session="closing", judge=True
                        )
                    agent.work_session.close()
                    expect(agent.work_session.cli_judge).to(equal(""))
                    expect(_cli_file(tmp, "closing").is_file()).to(be_false)


with description("a workspace that has no open session"):
    with context("that is asked to run the agent CLI"):
        with it("should open a new workspace session as if a work session had been started"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_no_open_"))
            space = Workspace(str(tmp))
            space.load()
            expect(space.current_work_session).to(equal(None))
            expect(space.work_sessions).to(equal([]))
            with patch(
                "cli_agent.cli_agent.CursorCli._create_chat",
                _create_chat_ids("doer-new"),
            ):
                agent = _run_agent(workspace=str(tmp), session="fresh")
            expect(agent.work_session.name).to(equal("fresh"))
            expect(agent.work_session.session_md.is_file()).to(be_true)

        with it("should associate the doer session with that workspace session"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_no_open_d_"))
            with patch(
                "cli_agent.cli_agent.CursorCli._create_chat",
                _create_chat_ids("doer-new"),
            ):
                agent = _run_agent(workspace=str(tmp), session="fresh")
            expect(agent.work_session.cli_doer).to(equal("doer-new"))

        with context("that has a judge task"):
            with it("should associate the judge session with that same workspace session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_no_open_j_"))
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-new", "judge-new"),
                ):
                    agent = _run_agent(
                        workspace=str(tmp), session="fresh", judge=True
                    )
                expect(agent.work_session.cli_judge).to(equal("judge-new"))
                expect(agent.work_session.cli_doer).to(equal("doer-new"))

        with context("that runs the agent CLI again in the same workspace session"):
            with it("should reuse the same doer session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_no_open_r_"))
                chats = []

                def _create(self, workspace: str, *, timeout_seconds: int = IdeCli.create_chat_timeout_seconds) -> str:
                    chats.append("x")
                    return f"id-{len(chats)}"

                with patch("cli_agent.cli_agent.CursorCli._create_chat", _create):
                    first = _run_agent(workspace=str(tmp), session="fresh")
                    second = _run_agent(workspace=str(tmp), session="fresh")
                expect(len(chats)).to(equal(1))
                expect(second.ide.resume).to(equal(first.ide.resume))

            with context("that has a judge task"):
                with it("should reuse the same judge session"):
                    tmp = Path(tempfile.mkdtemp(prefix="cli_no_open_rj_"))
                    chats = []

                    def _create(self, workspace: str, *, timeout_seconds: int = IdeCli.create_chat_timeout_seconds) -> str:
                        chats.append("x")
                        return f"id-{len(chats)}"

                    with patch("cli_agent.cli_agent.CursorCli._create_chat", _create):
                        first = _run_agent(
                            workspace=str(tmp), session="fresh", judge=True
                        )
                        second = _run_agent(
                            workspace=str(tmp), session="fresh", judge=True
                        )
                    expect(len(chats)).to(equal(2))
                    expect(second.ide.judge_resume).to(equal(first.ide.judge_resume))


with description("a folder that has no workspace sessions"):
    with context("that is asked to run the agent CLI"):
        with it("should create the workspace"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_folder_"))
            expect((tmp / ".context").exists()).to(be_false)
            with patch(
                "cli_agent.cli_agent.CursorCli._create_chat",
                _create_chat_ids("doer-folder"),
            ):
                _run_agent(workspace=str(tmp), session="from-folder")
            expect((tmp / ".context").is_dir()).to(be_true)
            expect((tmp / ".context" / "sessions").is_dir()).to(be_true)

        with it("should create a work session as if a work session had been started"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_folder_s_"))
            with patch(
                "cli_agent.cli_agent.CursorCli._create_chat",
                _create_chat_ids("doer-folder"),
            ):
                agent = _run_agent(workspace=str(tmp), session="from-folder")
            loaded = WorkSession.load(str(tmp), "from-folder")
            expect(loaded.session_md.is_file()).to(be_true)
            expect(agent.work_session.folder).to(
                equal(tmp / ".context" / "sessions" / "from-folder")
            )

        with it("should associate the doer session with that work session"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_folder_d_"))
            with patch(
                "cli_agent.cli_agent.CursorCli._create_chat",
                _create_chat_ids("doer-folder"),
            ):
                agent = _run_agent(workspace=str(tmp), session="from-folder")
            expect(_read_cli(tmp, "from-folder")["doer"]).to(equal("doer-folder"))
            expect(agent.work_session.cli_doer).to(equal("doer-folder"))

        with context("that has a judge task"):
            with it("should associate the judge session with that same work session"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_folder_j_"))
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat",
                    _create_chat_ids("doer-folder", "judge-folder"),
                ):
                    agent = _run_agent(
                        workspace=str(tmp),
                        session="from-folder",
                        judge="validate using the scanners",
                    )
                cli_record = _read_cli(tmp, "from-folder")
                expect(cli_record["judge"]).to(equal("judge-folder"))
                expect(agent.work_session.name).to(equal("from-folder"))


with description("a CLI spawn when a doer pid is already alive"):
    with context("that is asked to launch a new job"):
        with it("should still Popen so the new job is injected"):
            with patch(
                "cli_agent.cli_agent.subprocess.Popen", return_value=_popen(88)
            ) as spawned:
                result = _CliSpawner().start(
                    ["/bin/cursor-agent", "--resume", "abc"],
                    tempfile.mkdtemp(prefix="cli_inject_"),
                    existing_pid=158184,
                )
            expect(spawned.called).to(be_true)
            expect(result.pid).to(equal(88))


with description("CLI spawn role classification"):
    with it("should tag Cursor judge launch argv as judge (no --mode ask)"):
        expect(
            _CliSpawner().spawn_role(
                [
                    "cursor-agent.CMD",
                    "--resume",
                    "jid",
                    "Read .context/cli-agent-judge-launch.txt and follow it exactly.",
                ]
            )
        ).to(equal("judge"))
        expect(
            _CliSpawner().spawn_role(
                ["cursor-agent.CMD", "--resume", "did", "Read .context/cli-agent-task.txt"]
            )
        ).to(equal("doer"))
        expect(
            _CliSpawner().spawn_role(["code", "--mode", "ask", "judge please"])
        ).to(equal("judge"))


with description("a doer that does not take the new job"):
    with context("when the transcript never gains a user turn"):
        with it("should raise NOT TAKEN UP so the parent does not wait"):
            pickup = _Pickup()
            missing = Path(tempfile.mkdtemp(prefix="cli_miss_")) / "none.jsonl"
            expect(pickup.accepted(missing, 0, seconds=0.0)).to(be_false)

            def _fail():
                agent = CliAgent(workspace=".")
                agent._ide = IdeCli(pickup_seconds=0.0)
                agent._await_pickup("no-such-resume", 0)

            expect(_fail).to(raise_error(RuntimeError))

        with it("should treat a live doer pid as taken-up even without a transcript mark"):
            agent = CliAgent(workspace=".")
            agent._ide = IdeCli(pickup_seconds=0.0)
            with patch("cli_agent.cli_agent._pid_alive", return_value=True):
                agent._await_pickup("no-such-resume", 0, pid=4242)

        with it("should still raise NOT TAKEN UP when the bound pid is dead"):
            agent = CliAgent(workspace=".")
            agent._ide = IdeCli(pickup_seconds=0.0)

            def _fail():
                with patch("cli_agent.cli_agent._pid_alive", return_value=False):
                    agent._await_pickup("no-such-resume", 0, pid=4242)

            expect(_fail).to(raise_error(RuntimeError))

    with context("when resolving the Cursor transcript path"):
        with it("should hyphenate underscores in the project slug"):
            path = _Pickup().cursor_transcript(
                r"C:\Users\jeffa\AppData\Local\Temp\cli44_e2e_abc",
                "resume-id",
            )
            expect("_" in path.parts[-3]).to(be_false)
            expect("cli44-e2e-abc" in path.as_posix()).to(be_true)

    with context("when the transcript gains a user turn"):
        with it("should accept the pickup"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_got_")) / "t.jsonl"
            tmp.write_text('{"role":"user","message":{}}\n', encoding="utf-8")
            expect(_Pickup().accepted(tmp, 0, seconds=0.0)).to(be_true)


with description("a CliAgent tool surface"):
    with context("enqueue_jobs"):
        with it("should store a job list on the WorkSession and return the count"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_enq_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-enq"):
                    agent = CliAgent(workspace=str(tmp), session="enqueue")
                    result = agent.enqueue_jobs([
                        {"tools": [], "prompt": "job one"},
                        {"tools": [], "prompt": "job two"},
                    ])
            expect("job_queue: 2" in result).to(be_true)
            expect(len(agent.job_queue)).to(equal(2))

        with it("should be marked as an agent_tool"):
            expect(getattr(CliAgent.enqueue_jobs, "_is_agent_tool", False)).to(be_true)

    with context("launch_next"):
        with it("should be marked as an agent_tool"):
            expect(getattr(CliAgent.launch_next, "_is_agent_tool", False)).to(be_true)

    with context("complete_job"):
        with it("should be marked as an agent_tool"):
            expect(getattr(CliAgent.complete_job, "_is_agent_tool", False)).to(be_true)

    with context("launch_sessions with a prompt"):
        with it("should set task_prompt before launching"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_lsp_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-lsp"):
                    with patch("cli_agent.cli_agent.subprocess.Popen", return_value=_popen()):
                        with patch.object(CliAgent, "_await_pickup", lambda *a, **k: None):
                            agent = CliAgent(workspace=str(tmp), session="lsp")
                            agent.launch_sessions(tools=[], prompt="do the thing")
            expect(agent.task_prompt).to(equal("do the thing"))


with description("CliAgent work session bind before start-ticket"):
    with context("when HEAD is main and a leftover default session already exists"):
        with context("and no session name was given"):
            with it(
                "should not bind CliAgent to default â€” session comes from start-ticket"
            ):
                from workspace.git_repo import NullGitRepo

                tmp = Path(tempfile.mkdtemp(prefix="cli_pre_start_"))
                Workspace(str(tmp)).open_work_session(
                    "default", git=NullGitRepo(tmp)
                )
                agent = CliAgent(workspace=str(tmp), session="")
                with patch.object(
                    CliAgent,
                    "_session_name_from_git",
                    lambda self: "",
                ):
                    with patch(
                        "workspace.workspace.WorkSession._default_git",
                        lambda self: NullGitRepo(Path(self.workspace.path)),
                    ):
                        work = agent._ensure_work_session()
                expect(work.name).not_to(equal("default"))

            with it(
                "should not bind a durable folder-slug session while HEAD is still main"
            ):
                """Residual isolation defect: after skipping leftover default, attach
                still opens a folder-slug WorkSession on main before start-ticket.
                Durable bind must wait for session/<ticket> (+ worktree)."""
                from workspace.git_repo import NullGitRepo

                tmp = Path(tempfile.mkdtemp(prefix="cli_pre_start_slug_"))
                Workspace(str(tmp)).open_work_session(
                    "default", git=NullGitRepo(tmp)
                )
                agent = CliAgent(workspace=str(tmp), session="")
                slug = agent._session_slug_from_folder()
                with patch.object(
                    CliAgent,
                    "_session_name_from_git",
                    lambda self: "",
                ):
                    with patch(
                        "workspace.workspace.WorkSession._default_git",
                        lambda self: NullGitRepo(Path(self.workspace.path)),
                    ):
                        work = agent._ensure_work_session()
                expect(work.name).not_to(equal(slug))
                expect(agent._session in ("", None) or agent._session != slug).to(
                    be_true
                )

    with context("after start-ticket creates the ticket worktree"):
        with it(
            "should rebind workspace root to the ticket worktree for later jobs"
        ):
            """CliAgent must retarget _workspace (and session) off the parent
            checkout onto the ticket sibling worktree once start-ticket returns."""
            parent = Path(tempfile.mkdtemp(prefix="cli_parent_"))
            ticket_tree = Path(tempfile.mkdtemp(prefix="abd-cdd-99-"))
            agent = CliAgent(workspace=str(parent), session="premature-bind")
            expect(hasattr(agent, "rebind_to_worktree")).to(be_true)
            agent.rebind_to_worktree(
                str(ticket_tree), session="ticket-session-99"
            )
            expect(Path(agent._workspace_root()).resolve()).to(
                equal(ticket_tree.resolve())
            )
            expect(agent._session).to(equal("ticket-session-99"))

    with context("defect-fix job 1 prompt"):
        with it(
            "should tell the doer not to rely on a durable CliAgent session on main before start-ticket"
        ):
            template = (
                Path(__file__).resolve().parent / "job-templates" / "defect-fix.json"
            )
            jobs = json.loads(template.read_text(encoding="utf-8"))["jobs"]
            prompt = jobs[0]["prompt"].lower()
            expect(
                "durable" in prompt
                or "rebind" in prompt
                or "do not bind" in prompt
                or "before start-ticket" in prompt
            ).to(be_true)

        with it(
            "should require rebind of workspace root after start-ticket for CliAgent SubAgent and no-agent"
        ):
            template = (
                Path(__file__).resolve().parent / "job-templates" / "defect-fix.json"
            )
            module_ctx = (
                Path(__file__).resolve().parent / ".context" / "module-context.md"
            )
            text = (
                template.read_text(encoding="utf-8").lower()
                + "\n"
                + module_ctx.read_text(encoding="utf-8").lower()
            )
            expect("rebind" in text or "rebind" in text).to(be_true)
            expect(
                "worktree" in text
                and (
                    "cliagent" in text.replace("-", "")
                    or "cli agent" in text
                    or "subagent" in text.replace("-", "")
                    or "no-agent" in text
                    or "no agent" in text
                )
            ).to(be_true)


with description("a CLI agent job_queue"):
    with context("when the parent assigns two jobs"):
        with it("should store them on the WorkSession without spawning"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_q_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-q"):
                    with patch("cli_agent.cli_agent.subprocess.Popen", return_value=_popen()):
                        agent = CliAgent(workspace=str(tmp), session="queue")
                        agent.job_queue = [
                            {
                                "tools": ["context_tools.stories.stories:Stories"],
                                "actions": ["generate"],
                                "prompt": "job one",
                            },
                            {
                                "tools": [
                                    "context_tools.clean_engineering.clean_engineering:CleanEngineering"
                                ],
                                "actions": ["generate"],
                                "prompt": "job two",
                            },
                        ]
            expect(len(agent.job_queue)).to(equal(2))
            expect(agent.job_queue[0]["prompt"]).to(equal("job one"))
            expect(JobQueue().path_for(agent.work_session).is_file()).to(be_true)

        with it("should send the oldest job on launch_next and keep it until PASS"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_q2_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-q"):
                    with patch("cli_agent.cli_agent.subprocess.Popen", return_value=_popen()):
                        with patch.object(CliAgent, "_await_pickup", lambda *a, **k: None):
                            agent = CliAgent(workspace=str(tmp), session="queue")
                            agent.job_queue = [
                                {"tools": [], "actions": ["generate"], "prompt": "job one"},
                                {"tools": [], "actions": ["generate"], "prompt": "job two"},
                            ]
                            text = agent.launch_next()
            expect("taken up: yes" in text).to(be_true)
            expect("job_queue: 2" in text).to(be_true)
            expect(len(agent.job_queue)).to(equal(2))
            expect(agent.job_queue[0]["prompt"]).to(equal("job one"))

        with it("should drop the head only after complete_job"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_q3_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-q"):
                    agent = CliAgent(workspace=str(tmp), session="queue")
                    agent.job_queue = [
                        {"tools": [], "actions": ["generate"], "prompt": "job one"},
                        {"tools": [], "actions": ["generate"], "prompt": "job two"},
                    ]
                    done = agent.complete_job()
            expect(done["prompt"]).to(equal("job one"))
            expect(len(agent.job_queue)).to(equal(1))
            expect(agent.job_queue[0]["prompt"]).to(equal("job two"))

    with context("when the job_queue is empty"):
        with it("should raise so the parent does not wait"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_q0_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-q"):
                    agent = CliAgent(workspace=str(tmp), session="queue")

                    def _fail():
                        agent.launch_next()

                    expect(_fail).to(raise_error(RuntimeError))


with description("a job template"):
    with context("that is saved to the default location"):
        with it("should persist under utilities/cli_agent/job-templates/"):
            pass  # BDD: SIGNATURE

        with it("should round-trip: load returns the saved jobs unchanged"):
            pass  # BDD: SIGNATURE

    with context("that is saved to a project-specific path"):
        with it("should persist under the provided path"):
            pass  # BDD: SIGNATURE

    with context("when no template exists at the requested name"):
        with it("should return None"):
            pass  # BDD: SIGNATURE


with description("a job template store"):
    with context("that lists all templates"):
        with it("should return names of every saved template"):
            pass  # BDD: SIGNATURE

        with context("when the template folder is empty"):
            with it("should return an empty list"):
                pass  # BDD: SIGNATURE

    with context("that finds matching templates"):
        with context("when the prompt matches a template name"):
            with it("should include that template in the results"):
                pass  # BDD: SIGNATURE

        with context("when the prompt does not match any template"):
            with it("should return an empty list"):
                pass  # BDD: SIGNATURE


with description("CliAgent job template tools"):
    with context("add_template"):
        with it("should save the jobs as a named template"):
            pass  # BDD: SIGNATURE

        with context("with a path override"):
            with it("should save under the specified path"):
                pass  # BDD: SIGNATURE

    with context("list_templates"):
        with it("should return names of available templates"):
            pass  # BDD: SIGNATURE

    with context("use_template"):
        with it("should enqueue jobs from the named template"):
            pass  # BDD: SIGNATURE

        with context("with overrides provided"):
            with it("should merge overrides into the template jobs before enqueueing"):
                pass  # BDD: SIGNATURE

        with context("when the template does not exist"):
            with it("should raise so the caller can recover"):
                pass  # BDD: SIGNATURE


with description("a backlog item"):
    with context("that is a ticket reference"):
        with it("should classify #27 and 27 as ticket kind"):
            expect(CliBacklogItem.from_ref("#27").kind).to(equal("ticket"))
            expect(CliBacklogItem.from_ref("#27").ref).to(equal(27))
            expect(CliBacklogItem.from_ref(15).kind).to(equal("ticket"))

    with context("that is free text"):
        with it("should classify qualitative text as text kind"):
            item = CliBacklogItem.from_ref("session lands on default instead of defect name")
            expect(item.kind).to(equal("text"))
            expect(item.status).to(equal("pending"))


with description("a backlog"):
    with context("that is saved on the work session"):
        with it("should round-trip items and template"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-bl"):
                    agent = CliAgent(workspace=str(tmp), session="backlog-round")
                    work = agent._attach_cli_sessions()
                    backlog = CliBacklog(
                        items=[
                            CliBacklogItem.from_ref(12),
                            CliBacklogItem.from_ref("thin slice auth"),
                        ],
                        template="defect-fix",
                    )
                    backlog.save(work)
                    loaded = CliBacklog.load(work)
                    expect(loaded.template).to(equal("defect-fix"))
                    expect(len(loaded.items)).to(equal(2))
                    expect(loaded.items[0].kind).to(equal("ticket"))
                    expect(loaded.items[1].kind).to(equal("text"))

    with context("that advances through items"):
        with it("should mark the current item done and start the next"):
            backlog = CliBacklog(
                items=[
                    CliBacklogItem.from_ref(1),
                    CliBacklogItem.from_ref(2),
                ]
            )
            first = backlog.advance()
            expect(first.ref).to(equal(1))
            expect(first.status).to(equal("in_progress"))
            second = backlog.advance()
            expect(second.ref).to(equal(2))
            expect(backlog.items[0].status).to(equal("done"))
            expect(backlog.advance()).to(equal(None))

    with context("when one work session covers the whole backlog"):
        with it("should keep the same session while advancing items"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_sess_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-bl2"):
                    agent = CliAgent(workspace=str(tmp), session="one-session")
                    agent.set_backlog([12, 15], template=None)
                    work = agent._attach_cli_sessions()
                    expect(work.name).to(equal("one-session"))
                    agent.next_backlog_item()
                    expect(agent._attach_cli_sessions().name).to(equal("one-session"))


with description("CliAgent backlog tools"):
    with context("set_backlog"):
        with it("should persist items in the given order"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_set_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-set"):
                    agent = CliAgent(workspace=str(tmp), session="set-bl")
                    result = agent.set_backlog([12, "#15", "qualitative defect"], template="defect-fix")
                    expect(result).to(contain("3 item"))
                    expect(result).to(contain("defect-fix"))
                    loaded = CliBacklog.load(agent._attach_cli_sessions())
                    expect(loaded.items[0].ref).to(equal(12))
                    expect(loaded.items[1].ref).to(equal(15))
                    expect(loaded.items[2].kind).to(equal("text"))

        with context("with an order override"):
            with it("should reorder items by the given indexes"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_bl_ord_"))
                with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                    with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-ord"):
                        agent = CliAgent(workspace=str(tmp), session="ord-bl")
                        agent.set_backlog([10, 20, 30], order=[2, 0, 1])
                        loaded = CliBacklog.load(agent._attach_cli_sessions())
                        expect([i.ref for i in loaded.items]).to(equal([30, 10, 20]))

    with context("next_backlog_item"):
        with it("should advance and return None when exhausted"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_next_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-next"):
                    agent = CliAgent(workspace=str(tmp), session="next-bl")
                    agent.set_backlog([1])
                    expect(agent.next_backlog_item()).to(contain("#1"))
                    expect(agent.next_backlog_item()).to(equal(None))

        with context("when a template is bound"):
            with it("should enqueue template jobs with the item injected into prompts"):
                tmp = Path(tempfile.mkdtemp(prefix="cli_bl_tmpl_"))
                with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                    with patch("cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-tmpl"):
                        agent = CliAgent(workspace=str(tmp), session="tmpl-bl")
                        agent.add_template(
                            "slice-stories",
                            jobs=[{"prompt": "Generate story map for slice"}],
                            description="story map per thin slice",
                            path=str(tmp / "templates"),
                        )
                        agent.set_backlog(
                            ["thin slice login", "thin slice checkout"],
                            template="slice-stories",
                            path=str(tmp / "templates"),
                        )
                        # set_backlog does not take path for template store on backlog â€”
                        # next_backlog_item uses path for template load
                        msg = agent.next_backlog_item(path=str(tmp / "templates"))
                        expect(msg).to(contain("slice-stories"))
                        queue = agent.job_queue
                        expect(len(queue)).to(equal(1))
                        expect(queue[0]["prompt"]).to(contain("thin slice login"))


with description("CliAgent backlog hygiene (#46)"):
    """Red tests for up-front triage, theme:cli-agent, and finish-ticket before advance."""

    with context("a backlog that still has free-text covering an existing ticket"):
        with it("should map that free-text to the existing ticket number during up-front triage"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_triage_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-triage"
                ):
                    agent = CliAgent(workspace=str(tmp), session="hygiene-triage")
                    agent.set_backlog(
                        [
                            "CliAgent session log is incomplete vs design",
                            46,
                        ],
                        template="defect-fix",
                    )
                    # Intended seam: resolve text â†’ existing #N (no duplicate create).
                    expect(hasattr(agent, "triage_backlog")).to(be_true)
                    agent.triage_backlog(
                        find_existing=lambda text: 43
                        if "session log" in text.lower()
                        else None,
                        theme="cli-agent",
                    )
                    loaded = CliBacklog.load(agent._attach_cli_sessions())
                    text_or_mapped = loaded.items[0]
                    expect(text_or_mapped.kind).to(equal("ticket"))
                    expect(text_or_mapped.ref).to(equal(43))

    with context("when advancing past a ticket backlog item"):
        with it("should call finish-ticket before starting the next backlog item"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_finish_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-fin"
                ):
                    agent = CliAgent(workspace=str(tmp), session="hygiene-finish")
                    agent.set_backlog([41, 46], template=None)
                    agent.next_backlog_item()
                    with patch(
                        "workflow.workflow.Workflow.finish",
                        return_value={"commit": "deadbeef", "session_name": "x"},
                    ) as finish:
                        agent.next_backlog_item()
                        expect(finish.called).to(be_true)

    with context("when triaging free-text that needs a new ticket"):
        with it("should create the ticket with theme cli-agent"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_bl_theme_"))
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                with patch(
                    "cli_agent.cli_agent.CursorCli._create_chat", return_value="doer-theme"
                ):
                    agent = CliAgent(workspace=str(tmp), session="hygiene-theme")
                    agent.set_backlog(
                        ["launch_sessions NOT TAKEN UP pickup flake"],
                        template="defect-fix",
                    )
                    expect(hasattr(agent, "triage_backlog")).to(be_true)
                    created = {}

                    def _capture(**kwargs):
                        created.update(kwargs)
                        return {"number": 99, "url": "https://example/99", "theme": kwargs.get("theme", "")}

                    agent.triage_backlog(
                        find_existing=lambda _text: None,
                        capture_backlog=_capture,
                        theme="cli-agent",
                    )
                    theme_val = str(created.get("theme", "")).replace("theme:", "")
                    expect(theme_val).to(equal("cli-agent"))


with description("CliAgent session log completeness (#42)"):
    """Red tests: header with doer/judge, chat + job-queue refs, job_finished summary/refs."""

    with context("when a session starts"):
        with it("should write a header carrying doer/judge ids so cli-agent.json is not required"):
            from workspace.git_repo import NullGitRepo

            tmp = Path(tempfile.mkdtemp(prefix="cli_log_hdr_"))
            work = Workspace(str(tmp)).open_work_session(
                "log-header", git=NullGitRepo(tmp)
            )
            work.ensure_started()
            work.cli_doer = "doer-id-aaa"
            work.cli_judge = "judge-id-bbb"
            work.cli_doer_pid = 11
            work.cli_judge_pid = 22
            work.save_cli_sessions()
            log = _CliAgentLog()
            # Intended seam: one-time header (not only repeating session_start).
            if hasattr(log, "header"):
                log.header(
                    work,
                    doer=work.cli_doer,
                    judge=work.cli_judge,
                    doer_pid=work.cli_doer_pid,
                    judge_pid=work.cli_judge_pid,
                    chat=str(tmp / "chat.jsonl"),
                    job_queue=str(log.path_for(work).parent / JobQueue.filename),
                )
            else:
                log.session_start(
                    work,
                    doer=work.cli_doer,
                    judge=work.cli_judge,
                    doer_pid=work.cli_doer_pid,
                    judge_pid=work.cli_judge_pid,
                    doer_transcript=str(tmp / "doer.jsonl"),
                    judge_transcript=str(tmp / "judge.jsonl"),
                )
            records = _cli_agent_log_records(work)
            header = next((r for r in records if r.get("kind") == "header"), None)
            expect(header).not_to(equal(None))
            expect(header.get("doer")).to(equal("doer-id-aaa"))
            expect(header.get("judge")).to(equal("judge-id-bbb"))
            expect("chat" in header or "chat_link" in header).to(be_true)
            expect(
                "job_queue" in header or "job_queue_path" in header
            ).to(be_true)

        with it("should record chat and job-queue as first-class fields on the session log"):
            from workspace.git_repo import NullGitRepo

            tmp = Path(tempfile.mkdtemp(prefix="cli_log_links_"))
            work = Workspace(str(tmp)).open_work_session(
                "log-links", git=NullGitRepo(tmp)
            )
            work.ensure_started()
            queue_path = work.folder / JobQueue.filename
            queue_path.write_text("[]\n", encoding="utf-8")
            chat_path = str(tmp / "agent-transcripts" / "doer.jsonl")
            log = _CliAgentLog()
            log.session_start(
                work,
                doer="d1",
                judge="j1",
                doer_pid=1,
                judge_pid=2,
                doer_transcript=chat_path,
                judge_transcript="",
            )
            records = _cli_agent_log_records(work)
            # Designed: durable chat + job_queue on header or session_start â€” not report-only.
            found = False
            for r in records:
                chat = r.get("chat") or r.get("chat_link") or ""
                queue = r.get("job_queue") or r.get("job_queue_path") or ""
                if chat and queue:
                    found = True
                    expect(str(chat)).to(contain("doer.jsonl"))
                    expect(str(queue)).to(contain(JobQueue.filename))
                    break
            expect(found).to(be_true)

    with context("when a job finishes"):
        with it("should append a response summary and content refs on job_finished"):
            from workspace.git_repo import NullGitRepo

            tmp = Path(tempfile.mkdtemp(prefix="cli_log_sum_"))
            work = Workspace(str(tmp)).open_work_session(
                "log-summary", git=NullGitRepo(tmp)
            )
            work.ensure_started()
            log = _CliAgentLog()
            try:
                log.job_finished(
                    work,
                    index=0,
                    prompt="fix the log",
                    summary="Wrote failing tests for session log header.",
                    refs=["utilities/cli_agent/cli_agent_spec.py"],
                )
            except TypeError:
                log.job_finished(work, index=0, prompt="fix the log")
            records = _cli_agent_log_records(work)
            finished = [r for r in records if r.get("kind") == "job_finished"]
            expect(len(finished)).to(equal(1))
            row = finished[0]
            summary = row.get("summary") or row.get("response_summary") or ""
            refs = row.get("refs") or row.get("content_refs") or []
            expect(str(summary)).not_to(equal(""))
            expect(len(list(refs)) > 0).to(be_true)


with description("CliAgent session log observability"):
    """Tools/actions on job records, ts_ms, duration_s, since_last_s."""

    with it("should record tools and actions on job_started and job_finished"):
        from workspace.git_repo import NullGitRepo

        tmp = Path(tempfile.mkdtemp(prefix="cli_log_obs_"))
        work = Workspace(str(tmp)).open_work_session(
            "log-obs", git=NullGitRepo(tmp)
        )
        work.ensure_started()
        log = _CliAgentLog()
        log.job_started(
            work,
            index=1,
            prompt="Write tests",
            tools=["workflow.workflow:Workflow"],
            actions=["context_tools.bdd.bdd:Bdd"],
            judge=True,
        )
        log.job_finished(
            work,
            index=1,
            prompt="Write tests",
            tools=["workflow.workflow:Workflow"],
            actions=["context_tools.bdd.bdd:Bdd"],
            judge=True,
            summary="Added red tests.",
            refs=["utilities/cli_agent/cli_agent_spec.py"],
        )
        records = _cli_agent_log_records(work)
        started = next(r for r in records if r.get("kind") == "job_started")
        finished = next(r for r in records if r.get("kind") == "job_finished")
        expect(started.get("tools")).to(equal(["workflow.workflow:Workflow"]))
        expect(started.get("actions")).to(equal(["context_tools.bdd.bdd:Bdd"]))
        expect(started.get("judge")).to(be_true)
        expect(finished.get("tools")).to(equal(["workflow.workflow:Workflow"]))
        expect(finished.get("duration_s")).not_to(equal(None))
        expect(finished.get("ts_ms")).not_to(equal(None))

    with it("should stamp ts_ms and since_last_s on every record"):
        from workspace.git_repo import NullGitRepo

        tmp = Path(tempfile.mkdtemp(prefix="cli_log_ts_"))
        work = Workspace(str(tmp)).open_work_session(
            "log-ts", git=NullGitRepo(tmp)
        )
        work.ensure_started()
        log = _CliAgentLog()
        log.job_started(work, index=0, prompt="one")
        time.sleep(0.05)
        log.job_finished(work, index=0, prompt="one")
        records = _cli_agent_log_records(work)
        expect(records[0].get("ts_ms")).not_to(equal(None))
        expect(records[1].get("since_last_s")).not_to(equal(None))
        expect(records[1].get("since_last_s") > 0).to(be_true)

    with it("should record structured tools on spawn"):
        from workspace.git_repo import NullGitRepo

        tmp = Path(tempfile.mkdtemp(prefix="cli_log_spawn_"))
        work = Workspace(str(tmp)).open_work_session(
            "log-spawn", git=NullGitRepo(tmp)
        )
        work.ensure_started()
        log = _CliAgentLog()
        log.spawn(
            work,
            role="doer",
            resume="doer-1",
            prompt="job",
            argv="agent --resume doer-1",
            tools=["workflow.workflow:Workflow"],
            actions=["context_tools.bdd.bdd:Bdd"],
            tool_calls=["workflow.workflow:Workflow name=run"],
            job_index=2,
        )
        row = _cli_agent_log_records(work)[0]
        expect(row.get("tools")).to(equal(["workflow.workflow:Workflow"]))
        expect(row.get("actions")).to(equal(["context_tools.bdd.bdd:Bdd"]))
        expect(row.get("tool_calls")).to(
            equal(["workflow.workflow:Workflow name=run"])
        )
        expect(row.get("job_index")).to(equal(2))


with description("CliAgent cleanup"):
    with it("should remove temps it wrote and leave session.md and sketches"):
        from workspace.git_repo import NullGitRepo

        tmp = Path(tempfile.mkdtemp(prefix="cli_cleanup_"))
        session = Workspace(str(tmp)).open_work_session(
            "sprint-a", git=NullGitRepo(tmp)
        )
        session.ensure_started()
        (session.folder / "wait_judge3.py").write_text("pass\n", encoding="utf-8")
        (session.folder / "judge-verdict-1.txt").write_text("PASS\n", encoding="utf-8")
        (session.folder / "cli-agent-job-queue.json").write_text("[]\n", encoding="utf-8")
        ctx = Path(session.path) / ".context"
        (ctx / "_judge_check.py").write_text("print(1)\n", encoding="utf-8")
        (ctx / "cli-agent-put-back.txt").write_text("x\n", encoding="utf-8")
        (ctx / "story-map.md").write_text("# keep\n", encoding="utf-8")
        CliAgent.cleanup_session(session)
        expect((session.folder / "session.md").is_file()).to(be_true)
        expect((session.folder / "wait_judge3.py").exists()).to(be_false)
        expect((session.folder / "judge-verdict-1.txt").exists()).to(be_false)
        expect((session.folder / "cli-agent-job-queue.json").exists()).to(be_false)
        expect((ctx / "_judge_check.py").exists()).to(be_false)
        expect((ctx / "cli-agent-put-back.txt").exists()).to(be_false)
        expect((ctx / "story-map.md").is_file()).to(be_true)


def _orch_work(name: str):
    from workspace.git_repo import NullGitRepo

    tmp = Path(tempfile.mkdtemp(prefix=f"cli_orch_{name}_"))
    work = Workspace(str(tmp)).open_work_session(name, git=NullGitRepo(tmp))
    work.ensure_started()
    return tmp, work


with description("CliAgent run_backlog orchestrator (#44)"):
    """Judge-in-code control loop: auto-advance on PASS, structured log kinds."""

    with it("should expose run_backlog as an agent tool"):
        expect(hasattr(CliAgent, "run_backlog")).to(be_true)

    with it("should complete jobs on PASS without the doer calling complete_job"):
        tmp, work = _orch_work("pass")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [
                {"prompt": "job-a", "tools": ["workflow.workflow:Workflow"], "judge": True},
                {"prompt": "job-b", "tools": [], "judge": False},
            ],
        )
        launches = []

        def launch_job(agent_self, item):
            launches.append(item.get("prompt"))

        out = agent.run_backlog(
            launch_job=launch_job,
            wait_doer=lambda _w, _i: None,
            spawn_judge=lambda _w, _i: None,
            wait_verdict=lambda _w, _i: "PASS",
        )
        expect(out).to(contain("done"))
        expect(JobQueue().load(work)).to(equal([]))
        expect(launches).to(equal(["job-a", "job-b"]))
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect("orchestrator_started" in kinds).to(be_true)
        expect("doer_finished" in kinds).to(be_true)
        expect("verdict" in kinds).to(be_true)
        expect("orchestrator_stopped" in kinds).to(be_true)

    with it("should write cli-agent-judge.txt and log judge_started from code"):
        tmp, work = _orch_work("judge")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [{"prompt": "needs-judge", "tools": ["x"], "judge": True}],
        )
        spawn_calls = []

        def spawn_judge(w, item):
            spawn_calls.append(item.get("prompt"))
            expect((Path(tmp) / ".context" / "cli-agent-judge.txt").is_file()).to(be_true)

        agent.run_backlog(
            launch_job=lambda _a, _i: None,
            wait_doer=lambda _w, _i: None,
            spawn_judge=spawn_judge,
            wait_verdict=lambda _w, _i: "PASS",
        )
        expect(spawn_calls).to(equal(["needs-judge"]))
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect("judge_started" in kinds).to(be_true)

    with it("should stop and log error after max judge FAILs"):
        tmp, work = _orch_work("fail")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [{"prompt": "bad", "tools": ["x"], "judge": True}],
        )
        out = agent.run_backlog(
            max_fail=2,
            launch_job=lambda _a, _i: None,
            wait_doer=lambda _w, _i: None,
            spawn_judge=lambda _w, _i: None,
            wait_verdict=lambda _w, _i: "FAIL",
        )
        expect(out).to(contain("FAIL"))
        expect(len(JobQueue().load(work))).to(equal(1))
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect("recovery" in kinds).to(be_true)
        expect("error" in kinds).to(be_true)

    with it("should not append doer-ask-judge when orchestrator owns the loop"):
        tmp, work = _orch_work("thin")
        work.cli_judge = "judge-id"
        agent = CliAgent(workspace=str(tmp), session=work.name)
        agent._orchestrator_owns_loop = True
        agent._judge_job = True
        with patch.object(agent, "_spawn_worker", return_value=[]):
            with patch.object(agent, "_attach_cli_sessions", return_value=work):
                with patch.object(
                    agent,
                    "_described_turn",
                    return_value=(
                        SimpleNamespace(
                            tool_keys=[],
                            tool_calls=[],
                            action=None,
                            fidelity="",
                            format="",
                            prompt="",
                        ),
                        [],
                    ),
                ):
                    agent.launch_sessions(["workflow.workflow:Workflow"], None)
        expect("Start-Process" in agent.job).to(be_false)
        expect("contact the judge" in (agent.job or "").lower()).to(be_false)

    with it("should read PASS or FAIL from judge transcript jsonl"):
        path = Path(tempfile.mkdtemp(prefix="cli_orch_verdict_")) / "judge.jsonl"
        path.write_text(
            json.dumps({"role": "user", "content": "go"}) + "\n"
            + json.dumps({"role": "assistant", "content": "Verdict: PASS"}) + "\n",
            encoding="utf-8",
        )
        expect(_TranscriptWatch().read_verdict(path)).to(equal("PASS"))

    with it("should read PASS from Cursor message-nested assistant jsonl"):
        path = Path(tempfile.mkdtemp(prefix="cli_orch_verdict_nest_")) / "judge.jsonl"
        path.write_text(
            json.dumps(
                {
                    "role": "assistant",
                    "message": {
                        "content": [
                            {"type": "text", "text": "Evidence ok.\n\nPASS"},
                        ]
                    },
                }
            )
            + "\n"
            + json.dumps({"type": "turn_ended", "status": "success"})
            + "\n",
            encoding="utf-8",
        )
        expect(_TranscriptWatch().read_verdict(path)).to(equal("PASS"))

    with it(
        "should remove the worktree after finish when CliAgent session temps were committed (#44)"
    ):
        import subprocess
        from git.git import GitRepo, Repo
        from workspace.workspace import WorkSession

        primary = Path(tempfile.mkdtemp(prefix="cli44_finish_wt_"))
        subprocess.check_call(["git", "init"], cwd=primary, stdout=subprocess.DEVNULL)
        subprocess.check_call(["git", "config", "user.email", "e@x"], cwd=primary)
        subprocess.check_call(["git", "config", "user.name", "e"], cwd=primary)
        subprocess.check_call(
            ["git", "commit", "--allow-empty", "-m", "init"],
            cwd=primary,
            stdout=subprocess.DEVNULL,
        )
        subprocess.check_call(["git", "branch", "-M", "main"], cwd=primary)
        session = "life-single"
        WorkSession(
            workspace=str(primary).replace("\\", "/"), session=session
        ).start_work_session(name=session, goal="finish dirt")
        found = GitRepo(primary).worktree_for(f"session/{session}")
        expect(found is not None).to(be_true)
        tree = Path(found.path)
        folder = tree / ".context" / "sessions" / session
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "cli-agent.json").write_text(
            '{"doer":"d","judge":"j"}', encoding="utf-8"
        )
        (folder / "wait_judge-1.txt").write_text("tmp", encoding="utf-8")
        (folder / "job-1-response.yaml").write_text("ok: true\n", encoding="utf-8")
        Repo.git(tree, "add", "-A")
        Repo.git(tree, "commit", "-m", "e2e lifecycle artifacts")
        WorkSession(
            workspace=str(tree).replace("\\", "/"), session=session
        ).finish_work_session(outcome="done")
        expect(tree.exists()).to(be_false)
        expect(GitRepo(primary).worktree_for(f"session/{session}")).to(equal(None))

    with it("should mint a judge chat in run_backlog before spawn_judge (#44)"):
        # Guards against losing the re-attach mint when editing run_backlog.
        src = Path("utilities/cli_agent/cli_agent.py").read_text(encoding="utf-8")
        # Locate the judge branch inside run_backlog and require mint lines nearby.
        start = src.index("def run_backlog")
        chunk = src[start : start + 8000]
        expect("_judge_job = True" in chunk).to(be_true)
        expect("_attach_cli_sessions()" in chunk).to(be_true)
        expect("no judge resume" in src).to(be_true)


with description("CliAgent human check (#53)"):
    """Job property human=true: pause after doer, parent resolves looks_good / needs_fixing."""

    with it("should preserve human on the job kit like judge"):
        kit = _CliAgentLog._job_kit({"prompt": "x", "human": True, "judge": False})
        expect(kit.get("human")).to(be_true)
        kit2 = _CliAgentLog._job_kit({"prompt": "x", "human_check": True})
        expect(kit2.get("human")).to(be_true)

    with it("should treat human as needing human and not judge"):
        tmp, work = _orch_work("human-flag")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        item = {"prompt": "review me", "human": True, "judge": True, "tools": ["x"]}
        expect(agent._job_needs_human(item)).to(be_true)
        expect(agent._job_needs_judge(item)).to(be_false)

    with it("should complete on looks_good without spawning a judge"):
        tmp, work = _orch_work("human-ok")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [{"prompt": "human-job", "tools": [], "judge": False, "human": True}],
        )
        launches = []
        spawn_calls = []

        out = agent.run_backlog(
            launch_job=lambda _a, item: launches.append(item.get("prompt")),
            wait_doer=lambda _w, _i: None,
            spawn_judge=lambda _w, _i: spawn_calls.append("judge"),
            wait_human=lambda _w, _i: {"result": "looks_good"},
            wait_verdict=lambda _w, _i: "PASS",
        )
        expect(out).to(contain("done"))
        expect(JobQueue().load(work)).to(equal([]))
        expect(launches).to(equal(["human-job"]))
        expect(spawn_calls).to(equal([]))
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect("human_check_needed" in kinds).to(be_true)
        expect("human_check_resolved" in kinds).to(be_true)
        expect("judge_started" in kinds).to(be_false)
        resolved = next(
            r for r in _CliAgentLog().read_records(work) if r.get("kind") == "human_check_resolved"
        )
        expect(resolved.get("result")).to(equal("looks_good"))

    with it("should redo the same job with feedback on needs_fixing then complete"):
        tmp, work = _orch_work("human-redo")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [
                {
                    "prompt": "ship it",
                    "tools": [],
                    "judge": False,
                    "human": True,
                    "index": 0,
                }
            ],
        )
        launches = []
        human_calls = {"n": 0}

        def wait_human(_w, item):
            human_calls["n"] += 1
            if human_calls["n"] == 1:
                return {"result": "needs_fixing", "feedback": "add a test"}
            return {"result": "looks_good"}

        def launch_job(_a, item):
            launches.append(str(item.get("prompt") or ""))

        out = agent.run_backlog(
            launch_job=launch_job,
            wait_doer=lambda _w, _i: None,
            spawn_judge=lambda _w, _i: None,
            wait_human=wait_human,
        )
        expect(out).to(contain("done"))
        expect(JobQueue().load(work)).to(equal([]))
        expect(len(launches)).to(equal(2))
        expect(launches[0]).to(equal("ship it"))
        expect("HUMAN FEEDBACK" in launches[1]).to(be_true)
        expect("add a test" in launches[1]).to(be_true)
        expect(human_calls["n"]).to(equal(2))
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect(kinds.count("human_check_needed")).to(equal(2))
        expect("recovery" in kinds).to(be_true)

    with it("should expose resolve_human_check as an agent tool that writes the session file"):
        tmp, work = _orch_work("human-resolve")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [{"prompt": "gate", "human": True, "judge": False, "index": 3}],
        )
        expect(hasattr(CliAgent, "resolve_human_check")).to(be_true)
        expect(getattr(CliAgent.resolve_human_check, "_is_agent_tool", False)).to(
            be_true
        )
        with patch.object(agent, "_attach_cli_sessions", return_value=work):
            msg = agent.resolve_human_check("needs_fixing", feedback="fix docs")
        expect("needs_fixing" in msg).to(be_true)
        path = Path(work.folder) / "human-check-3.json"
        expect(path.is_file()).to(be_true)
        payload = json.loads(path.read_text(encoding="utf-8"))
        expect(payload.get("result")).to(equal("needs_fixing"))
        expect(payload.get("feedback")).to(equal("fix docs"))

    with it("should tell the parent to resolve human_check_needed"):
        text = IdeCli()._parent_checkin.lower()
        expect("human_check_needed" in text).to(be_true)
        expect("human_notified" in text or "notification" in text).to(be_true)
        expect("resolve_human_check" in text).to(be_true)
        expect("looks_good" in text or "looks good" in text).to(be_true)

    with it("should notify the human before waiting for resolution"):
        tmp, work = _orch_work("human-notify")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [
                {
                    "prompt": "needs eyes",
                    "tools": [],
                    "judge": False,
                    "human": True,
                    "index": 0,
                }
            ],
        )
        notify_calls = []
        wait_order = []

        def notify_human(_w, item, title, body):
            notify_calls.append(
                {"prompt": item.get("prompt"), "title": title, "body": body}
            )
            wait_order.append("notify")
            return "test"

        def wait_human(_w, _i):
            wait_order.append("wait")
            return {"result": "looks_good"}

        out = agent.run_backlog(
            launch_job=lambda _a, _i: None,
            wait_doer=lambda _w, _i: None,
            spawn_judge=lambda _w, _i: None,
            notify_human=notify_human,
            wait_human=wait_human,
        )
        expect(out).to(contain("done"))
        expect(len(notify_calls)).to(equal(1))
        expect(notify_calls[0]["prompt"]).to(equal("needs eyes"))
        expect("human check" in notify_calls[0]["title"].lower()).to(be_true)
        expect("needs eyes" in notify_calls[0]["body"]).to(be_true)
        expect(wait_order).to(equal(["notify", "wait"]))
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect("human_notified" in kinds).to(be_true)
        notified = next(
            r for r in _CliAgentLog().read_records(work) if r.get("kind") == "human_notified"
        )
        expect(notified.get("job_index")).to(equal(0))
        expect(notified.get("channel")).to(equal("test"))
        expect("needs eyes" in str(notified.get("body") or "")).to(be_true)

    with it("should call the OS/IDE notifier by default when human check is needed"):
        tmp, work = _orch_work("human-os-notify")
        agent = CliAgent(workspace=str(tmp), session=work.name)
        JobQueue().save(
            work,
            [{"prompt": "ping human", "human": True, "judge": False, "index": 2}],
        )
        os_calls = []

        def fake_os(title, body, *, error=False):
            os_calls.append({"title": title, "body": body, "error": error})

        with patch(
            "utilities.manifest_hook.manifest_gate_conf.show_os_notification",
            fake_os,
        ):
            out = agent.run_backlog(
                launch_job=lambda _a, _i: None,
                wait_doer=lambda _w, _i: None,
                spawn_judge=lambda _w, _i: None,
                wait_human=lambda _w, _i: {"result": "looks_good"},
            )
        expect(out).to(contain("done"))
        expect(len(os_calls)).to(equal(1))
        expect("2" in os_calls[0]["title"]).to(be_true)
        expect("ping human" in os_calls[0]["body"]).to(be_true)
        kinds = [r.get("kind") for r in _CliAgentLog().read_records(work)]
        expect("human_notified" in kinds).to(be_true)
        notified = next(
            r for r in _CliAgentLog().read_records(work) if r.get("kind") == "human_notified"
        )
        expect(notified.get("channel")).to(equal("os"))


with description("CliAgent session model"):
    with context("when .context/sessions/{session}/model is set"):
        with it("should load that model onto ide when IdeCli.model is empty"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_session_model_"))
            model_path = (
                tmp / ".context" / "sessions" / "model-sprint" / "model"
            )
            model_path.parent.mkdir(parents=True, exist_ok=True)
            model_path.write_text("composer-2.5-fast\n", encoding="utf-8")
            agent = CliAgent(workspace=str(tmp), session="model-sprint")
            expect(agent.ide.model).to(equal("composer-2.5-fast"))

        with it("should pass the session model as --model on cursor argv"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_session_model_argv_"))
            model_path = tmp / ".context" / "sessions" / "argv-sprint" / "model"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            model_path.write_text("kimi-k3-max\n", encoding="utf-8")
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                host = CursorCli()
                host.bind_workspace(str(tmp), "argv-sprint")
                argv = host._command("go", str(tmp))
            expect(argv).to(contain("--model"))
            expect(argv).to(contain("kimi-k3-max"))

    with context("when IdeCli.model is already set"):
        with it("should keep the explicit model over the session file"):
            tmp = Path(tempfile.mkdtemp(prefix="cli_explicit_model_"))
            model_path = tmp / ".context" / "sessions" / "keep" / "model"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            model_path.write_text("kimi-k3-max\n", encoding="utf-8")
            agent = CliAgent(workspace=str(tmp), session="keep")
            agent._ide = IdeCli(model="composer-2.5-fast")
            expect(agent.ide.model).to(equal("composer-2.5-fast"))
