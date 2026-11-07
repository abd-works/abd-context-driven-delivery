"""The agent a spec drives inside ``with agent(...) as run:``: one block of instructs, toolset runs, and judgements.

``agent(workspace, session_file)`` opens the block: the cursor-agent CLI (``agent_cli_bdd.py``) or in-chat inbox files
(``agent_chat_bdd.py``), chosen by ``AGENT_BDD_IN_CHAT``. Both are an *AgentBlock*, which owns everything a step does
except how the agent answers: logging, the artifact files, toolset runs in the block's workspace, and the judge's verdict.
"""
from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from cdd_guidance.practices.agent_bdd.agent_bdd_common import (
    INSTRUCT_TIMEOUT_SECONDS,
    JUDGE_LAUNCH,
    JUDGE_TASK,
    JUDGE_TIMEOUT_SECONDS,
    READ_TIMEOUT_SECONDS,
    TOOL_RUN_TIMEOUT_SECONDS,
    AgentHarnessError,
    AgentJudgeError,
    AgentResult,
    HarnessLog,
    JudgeResult,
    RunResponse,
    ToolsRunYaml,
    ToolsetInvoke,
    _ShellCapture,
)
from cdd_guidance.practices.agent_bdd.conf import AgentBddConf
from cdd_guidance.practices.agent_bdd.yaml_fence import YamlFence


class AgentBlock:
    """One agent session a spec drives. A subclass says how the agent answers a prompt and a judge task."""

    log_name = "agent_bdd"

    def __init__(self, workspace: Path, session_file: Path) -> None:
        self._workspace = workspace.resolve()
        self._session_file = session_file
        self._yaml = YamlFence()
        # Reads and runs the toolset requests the prompts hold, in this block's workspace.
        self._tools_run_yaml = ToolsRunYaml(self._workspace)
        self._log = HarnessLog(self.log_name)
        self._log_dir = session_file.parent / "logs" / session_file.stem
        self._instruct_count = 0
        self.last_shell_captures: list[_ShellCapture] = []
        self.session_shell_captures: list[_ShellCapture] = []

    @classmethod
    @contextmanager
    def opened(cls, workspace: Path, session_file: Path) -> Iterator["AgentBlock"]:
        """One agent session for the steps inside the block."""
        block = cls(workspace, session_file)
        block._open()
        yield block

    def _open(self) -> None:
        """Start the agent session; the in-chat agent needs nothing started."""

    # -- steps a spec takes ---------------------------------------------------------------

    def instruct(self, prompt: str, *, timeout_seconds: int = INSTRUCT_TIMEOUT_SECONDS) -> AgentResult:
        """Give the agent a natural-language step, such as reading a file or following an action's instructions."""
        prefix = self._next_instruct_prefix("setup")
        self._log.write(f"{prefix} prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
        self._write_artifact(f"{prefix}-prompt.txt", prompt)
        result = self._answer(prefix, prompt, timeout_seconds)
        self._write_artifact(f"{prefix}-response.txt", result.text)
        if result.stderr.strip():
            self._write_artifact(f"{prefix}-stderr.txt", result.stderr)
        return result

    def read_workspace(self, path: str, *, timeout_seconds: int = READ_TIMEOUT_SECONDS) -> AgentResult:
        """Prime the agent by reading a workspace-relative file."""
        return self.instruct(f"Read {path} from the workspace.", timeout_seconds=timeout_seconds)

    def instruct_use_tool(self, prompt: str, *, timeout_seconds: int = INSTRUCT_TIMEOUT_SECONDS) -> RunResponse:
        """Run the toolset request the prompt holds in-process, in this block's workspace; fails when it outlives
        timeout_seconds."""
        request_yaml = self._tools_run_yaml.yaml_from_prompt(prompt)
        if not request_yaml:
            raise AgentHarnessError("prompt must contain a toolset: run request block")
        prefix = self._next_instruct_prefix("run")
        self._write_artifact(f"{prefix}-prompt.txt", prompt)
        self._write_artifact(f"{prefix}-stdin.yaml", request_yaml)
        cli_output = self._tools_run_yaml.run_request(request_yaml, timeout_seconds, prefix)
        return self._recorded_response(prefix, cli_output)

    def run_toolset(
        self,
        *,
        toolset: str,
        tool: str | None = None,
        action: str | None = None,
        context: Mapping[str, Any] | None = None,
        arguments: Mapping[str, Any] | None = None,
        timeout_seconds: int = TOOL_RUN_TIMEOUT_SECONDS,
    ) -> RunResponse:
        """Invoke one toolset member in-process, in this block's workspace; fails with ToolRunTimedOut when it outlives
        timeout_seconds."""
        invoke = ToolsetInvoke.for_toolset(
            toolset, self._workspace, tool=tool, action=action, context=context, arguments=arguments
        )
        return invoke.run(timeout_seconds)

    def ai_judge(self, output: str, rubric: str, *, timeout_seconds: int = JUDGE_TIMEOUT_SECONDS) -> JudgeResult:
        """Judge output against rubric; raises AssertionError(reason) on FAIL, so it reads like ``expect``."""
        self._echo("judge rubric:", rubric)
        self._echo("judge output:", output)
        self._write_artifact("judge-rubric.txt", rubric)
        self._write_artifact("judge-output.txt", output)
        task_path = self._write_artifact("judge-prompt.txt", JUDGE_TASK.format(rubric=rubric, output=output))
        launch_prompt = JUDGE_LAUNCH.format(path=task_path.relative_to(self._workspace).as_posix())
        self._write_artifact("judge-launch.txt", launch_prompt)
        answer = self._judge_answer(launch_prompt, timeout_seconds)
        verdict = self._verdict(answer)
        if verdict.failed():
            raise AssertionError(f"ai_judge FAIL - {verdict.reason}")
        return verdict

    def generate_and_judge(self, pass_path: str | Path, rubric: str | None = None, *,
                           timeout_seconds: int = INSTRUCT_TIMEOUT_SECONDS) -> str:
        """Generate something similar to the pass fixture, judge it, and return the artifact for human review."""
        from cdd_guidance.practices.agent_bdd.spec_helpers import generate_similar_prompt, generate_similar_rubric

        artifact = self.instruct(generate_similar_prompt(pass_path), timeout_seconds=timeout_seconds).text
        self.ai_judge(artifact, rubric or generate_similar_rubric(pass_path))
        return artifact

    # -- how the agent answers -------------------------------------------------------------

    def _answer(self, prefix: str, prompt: str, timeout_seconds: int) -> AgentResult:
        raise NotImplementedError(f"{type(self).__name__} must say how its agent answers a prompt")

    def _judge_answer(self, launch_prompt: str, timeout_seconds: int) -> AgentResult:
        raise NotImplementedError(f"{type(self).__name__} must say how its judge answers")

    # -- what every block records ----------------------------------------------------------

    def _verdict(self, answer: AgentResult) -> JudgeResult:
        self._write_artifact("judge-response.txt", answer.text)
        if answer.stderr.strip():
            self._write_artifact("judge-stderr.txt", answer.stderr)
        if answer.exit_code != 0:
            raise AgentHarnessError(f"judge agent exited {answer.exit_code}", prefix="judge", exit_code=answer.exit_code,
                                    stdout=answer.text, stderr=answer.stderr, log_dir=self._log_dir)
        verdict = JudgeResult.from_stdout(answer.text, answer.elapsed_seconds)
        self._write_artifact("judge-verdict.txt", f"{verdict.verdict}\n\n{verdict.reason}\n")
        if verdict.verdict == "ERROR":
            raise AgentJudgeError(f"judge returned no parseable JSON verdict: {verdict.reason}", prefix="judge",
                                  stdout=answer.text, stderr=answer.stderr, log_dir=self._log_dir)
        self._log.write(f"judge verdict: {verdict.verdict} - {verdict.reason}")
        return verdict

    def _recorded_response(self, prefix: str, cli_output: str) -> RunResponse:
        self._write_artifact(f"{prefix}-cli-output.yaml", cli_output)
        response = RunResponse.from_cli_output(cli_output)
        fields = {
            "ok": response.ok,
            "toolset": response.toolset,
            "tool": response.tool,
            "action": response.action,
            "result": response.result,
            "instructions": response.instructions,
            "tools": response.tools,
            "arguments": response.arguments,
            "resources": response.resources,
        }
        self._write_artifact(f"{prefix}-ai-response.yaml",
                             self._yaml.dump_manifest({key: value for key, value in fields.items() if value is not None}))
        return response

    def _echo(self, heading: str, text: str) -> None:
        self._log.write(heading)
        sys.__stdout__.write(text + "\n")
        sys.__stdout__.flush()

    def _write_artifact(self, name: str, content: str) -> Path:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        path = self._log_dir / name
        path.write_text(content, encoding="utf-8")
        return path

    def _next_instruct_prefix(self, label: str) -> str:
        self._instruct_count += 1
        return f"instruct-{self._instruct_count:03d}-{label}"


@contextmanager
def agent(workspace: Path, session_file: Path, *, in_chat: bool | None = None) -> Iterator[AgentBlock]:
    """The agent block for the steps inside: in chat when in_chat is set, or when ``AGENT_BDD_IN_CHAT`` says so, else
    the cursor-agent CLI. The agent's secrets and import paths load here, when a spec runs an agent, so importing the
    practice leaves the MCP host's environment alone."""
    AgentBddConf().configure()
    chosen = _in_chat_from_env() if in_chat is None else in_chat
    if chosen:
        from cdd_guidance.practices.agent_bdd.agent_chat_bdd import ChatAgentBlock as block_type
    else:
        from cdd_guidance.practices.agent_bdd.agent_cli_bdd import CliAgentBlock as block_type
    with block_type.opened(workspace, session_file) as block:
        yield block


def _in_chat_from_env() -> bool:
    return os.environ.get("AGENT_BDD_IN_CHAT", "").strip().lower() in {"1", "true", "yes"}
