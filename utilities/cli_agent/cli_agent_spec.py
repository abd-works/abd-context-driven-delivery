"""BDD spec for utilities/cli_agent/cli_agent.py — IdeCli, CliAgent, workspace sessions.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import json
import sys
import tempfile
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

from expects import be_a, be_false, be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from cli_agent.cli_agent import (
    CliAgent,
    CursorCli,
    IdeCli,
    VscodeCli,
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
    ide = IdeCli(**kwargs)
    if prompt:
        ide._prompt = prompt
    with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
        with patch("cli_agent.cli_agent.subprocess.Popen", return_value=_popen()):
            agent = CliAgent(ide=ide, workspace=workspace, session=session)
            agent.launch_sessions(tools=[], actions=None)
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

        with it("should pass print-mode flags only when print_mode is set"):
            with patch("cli_agent.cli_agent.shutil.which", side_effect=_which_cursor):
                argv = CursorCli(
                    model="sonnet", agent_mode="plan", print_mode=True
                )._command("do the work", "/ws")
            expect(argv).to(contain("-p"))
            expect(argv).to(contain("--force"))
            expect(argv).to(contain("stream-json"))

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
    with context("that is constructed with IdeCli flags"):
        with it("should hold them on ide for later runs"):
            agent = CliAgent(
                ide=IdeCli(model="gpt", mode="medium", agent_mode="plan", judge=True)
            )
            expect(agent.ide.model).to(equal("gpt"))
            expect(agent.ide.mode).to(equal("medium"))
            expect(agent.ide.agent_mode).to(equal("plan"))
            expect(agent.ide.judge).to(be_true)

    with context("launch_sessions"):
        with it("should mark launch_sessions as a sub_agent"):
            expect(getattr(CliAgent.launch_sessions, "_is_sub_agent", False)).to(be_true)

        with it("should publish kind sub_agent and launch non_blocking"):
            entry = discover_sub_agent_tools(CliAgent(ide=IdeCli()))[
                "launch_sessions"
            ].signature_entry
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))

        with it("should take tools and optional actions only"):
            params = discover_sub_agent_tools(CliAgent(ide=IdeCli()))[
                "launch_sessions"
            ].signature_entry["parameters"]
            expect("tools" in params).to(be_true)
            expect("actions" in params).to(be_true)
            expect("model" in params).to(be_false)

        with it("should tell the parent to spawn the IDE CLI"):
            text = discover_sub_agent_tools(CliAgent(ide=IdeCli()))[
                "launch_sessions"
            ].instructions
            expect("run_all" in text).to(be_true)
            expect("IdeCli.spawn" in text).to(be_true)
            expect("start_work_session" in text).to(be_true)
            expect("must not call" in text).to(be_true)
            expect("process reference" in text).to(be_true)
            expect("--resume" in text).to(be_true)
            expect("not IDE chats" in text).to(be_true)
            expect("check" in text).to(be_true)
            expect("report" in text).to(be_true)
            expect("-p" in text).to(be_true)
            expect("doer only" in text).to(be_true)
            expect("Do not prompt, launch, or score the judge" in text).to(be_true)

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
                        text = CliAgent(
                            ide=IdeCli(), workspace=tmp, session="run-spec"
                        ).launch_sessions(tools=[], actions=None)
            expect(spawned.called).to(be_true)
            expect(spawned.call_args[0][0][0]).to(equal("/bin/cursor-agent"))
            expect("-p" in spawned.call_args[0][0]).to(be_false)
            expect(spawned.call_args[0][0][-1]).to(contain("cli-agent-task.txt"))
            expect("pid: 4242" in text).to(be_true)
            expect(
                "cursor-agent --resume 11111111-1111-1111-1111-111111111111" in text
            ).to(be_true)
            expect("CLI processes (not IDE chats):" in text).to(be_true)
            expect("session: run-spec" in text).to(be_true)


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
                expect(task).to(contain("--resume judge-1"))
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
