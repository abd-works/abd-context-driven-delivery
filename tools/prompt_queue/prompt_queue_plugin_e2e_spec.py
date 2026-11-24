"""Heavy spec: the prompt-queue plugin, loaded into a real Claude Code chat run headless (``claude -p``), keeps the chat's
queue on a real cdd server.

The plugin's own tests (hooks/register.test.tsx) stub the cdd server, the stored state and the clock; this spec runs the
same hooks for real. A SpecServer serves the PromptQueue toolset; a scratch project's .mcp.json names it ``cdd``; the CLI
at CLAUDE_CODE_EXECPATH, else claude on the PATH, loads the plugin from this checkout with ``--plugin-dir`` and takes each message through
stream-json input, so the plugin's prompt.submit, tool.call and turn hooks run as they do in a chat. The queue is then
read back through the server with prompt-queue.show.

The scratch .mcp.json names the server with no headersHelper, so a call carries no chat id of its own: the agent is told
its chat id, as the plugin always names it.

Out of scope, because only the desktop app has them: the app's update_plan and wrap_up task list, the cards the plugin
draws above the chat bar, and the chat bar's failure line.
"""
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import SpecChat, SpecServer

TOOLSETS = ("tools.prompt_queue.prompt_queue:PromptQueue",)
PLUGIN_FOLDER = _REPO_ROOT / "tools" / "prompt_queue"
# The environment the desktop app gives the chat running this spec, which would join the headless chat to that chat: its
# id, its own plugins, its messaging pipe and its terminal tools.
_CHAT_ENVIRONMENT = (
    "CLAUDE_CODE_SESSION_ID", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_PLUGIN_DIRS", "CLAUDE_CODE_MESSAGING_SOCKET",
    "CLAUDE_CODE_MESSAGING_TOKEN", "CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_TERMINAL_MCP_TOOLS",
)
# The cheapest model answers: the spec checks the plugin's hooks, not the agent's work.
_MODEL = "haiku"
# How long one turn may take, from the message sent to the chat's result.
_TURN_SECONDS = 240
# How many times the chat is asked to give the goal its steps before the spec goes on and fails on what it finds.
_SET_STEPS_ASKS = 3
_NOTICE ="<task-notification> <task-id>b1</task-id> <status>completed</status> </task-notification>"
# A paste as Claude Code hands it to the plugin: the pasted text inside its tags.
_PASTED_NOTES = '<pasted_content id="7250">\n## Notes from the backlog\nFrom `board-enhancements` the board needs a filter.\n</pasted_content>'


class ClaudeCodeNotFoundError(RuntimeError):
    """No Claude Code to run the headless chat with: CLAUDE_CODE_EXECPATH is not set and no claude is on the PATH. A
    chat in the Claude app sets the variable in its Bash tool, not always in its PowerShell tool, so the tier run from
    a shell without it starts no chat."""

    def __init__(self) -> None:
        super().__init__(
            "No Claude Code found to start a headless chat: set CLAUDE_CODE_EXECPATH to the claude executable, or put claude "
            "on the PATH, then run the e2e tier again (a Claude app chat's Bash tool has the variable; its PowerShell tool may not)"
        )


def claude_code() -> str:
    """The Claude Code executable the headless chat runs: the one the running chat names, else claude on the PATH."""
    found = os.environ.get("CLAUDE_CODE_EXECPATH") or shutil.which("claude")
    if not found:
        raise ClaudeCodeNotFoundError()
    return found


class HeadlessChat:
    """A Claude Code chat run headless on a scratch project whose .mcp.json names the spec's cdd server, with the
    prompt-queue plugin loaded from this checkout. It holds its own queue on the server, read and seeded through a
    SpecChat with the same chat id, and the tools the agent may call without asking."""

    def __init__(self, server: SpecServer, allowed_tools: tuple[str, ...] = ()) -> None:
        self.id = str(uuid.uuid4())
        self._project = Path(tempfile.mkdtemp(prefix="queue-plugin-project-"))
        self._servers = self._project / ".mcp.json"
        self._servers.write_text(json.dumps({"mcpServers": {"cdd": {"type": "http", "url": server.url}}}), encoding="utf-8")
        self._queue = SpecChat(server, self._project, chat_id=self.id)
        self._allowed_tools = allowed_tools
        self._process: subprocess.Popen | None = None
        self._lines: queue.Queue[str] = queue.Queue()

    def queue_work(self, texts: list[str], done: int = 0) -> list[dict]:
        """Queue texts on this chat's queue through the server, the first done of them marked done."""
        prompts = self._queue.answer("prompt-queue.add_all", chat=self.id, texts=texts)["prompts"]
        for prompt in prompts[:done]:
            self._queue.answer("prompt-queue.done", chat=self.id, prompt=prompt["id"])
        return self.prompts()

    def prompts(self) -> list[dict]:
        return self._queue.answer("prompt-queue.show", chat=self.id)["prompts"]

    def start(self) -> None:
        self._process = subprocess.Popen(
            self._command(), cwd=self._project, env=self._environment(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
        threading.Thread(target=self._read_output, daemon=True).start()

    def send(self, text: str) -> None:
        """Send text as the person's message and wait for the turn it starts to end. A chat that never started, since no
        Claude Code was found, fails on that, as every example after it does."""
        if self._process is None:
            raise ClaudeCodeNotFoundError()
        self._process.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        self._process.stdin.flush()
        while json.loads(self._lines.get(timeout=_TURN_SECONDS)).get("type") != "result":
            pass

    def stop(self) -> None:
        if self._process is not None:
            self._process.stdin.close()
            try:
                self._process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                self._process.kill()
        shutil.rmtree(self._project, ignore_errors=True)

    def _command(self) -> list[str]:
        allowed = ["--allowedTools", *self._allowed_tools] if self._allowed_tools else []
        return [
            claude_code(), "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
            "--session-id", self.id, "--plugin-dir", str(PLUGIN_FOLDER), "--mcp-config", str(self._servers), "--strict-mcp-config",
            "--setting-sources", "project,local", "--model", _MODEL, "--no-session-persistence", *allowed,
        ]

    def _environment(self) -> dict[str, str]:
        return {key: value for key, value in os.environ.items() if key not in _CHAT_ENVIRONMENT}

    def _read_output(self) -> None:
        for line in self._process.stdout:
            if line.strip():
                self._lines.put(line)


def texts(prompts: list[dict]) -> list[str]:
    return [prompt["text"] for prompt in prompts]


# (S) Person --> Interrupt The Queue From The Chat
with description("a chat's prompt queue as the prompt-queue plugin keeps it in a headless Claude Code chat") as self:
    with before.all:
        self.chats = Path(tempfile.mkdtemp(prefix="queue-plugin-chats-"))
        self.prior_chats = os.environ.get("CDD_CHATS_FOLDER")
        os.environ["CDD_CHATS_FOLDER"] = str(self.chats)
        self.server = SpecServer(TOOLSETS)
        self.server.start()

    with after.all:
        self.server.stop()
        if self.prior_chats is None:
            os.environ.pop("CDD_CHATS_FOLDER", None)
        else:
            os.environ["CDD_CHATS_FOLDER"] = self.prior_chats
        shutil.rmtree(self.chats, ignore_errors=True)

    with context("that the queue holds a done prompt and one to do, and no goal was last worked"):
        with before.all:
            self.chat = HeadlessChat(self.server)
            self.chat.queue_work(["Write the scenarios", "Run the unit tier"], done=1)
            self.chat.start()

        with after.all:
            self.chat.stop()

        with context("that the person sends a prompt straight to the chat"):
            with before.all:
                self.chat.send("Fix the Files app")

            with it("should go above the next prompt to do, below the done ones, marked as an interruption"):
                expect(texts(self.chat.prompts())).to(equal(["Write the scenarios", "[interruption] Fix the Files app", "Run the unit tier"]))

            with context("that the person pastes new work after that turn, which asked nothing"):
                with before.all:
                    self.chat.send(_PASTED_NOTES)

                with it("should start a goal of its own, titled by the paste's first line"):
                    expect(texts(self.chat.prompts())).to(contain("[interruption] Notes from the backlog"))

                with it("should leave the goal last worked without a step from it"):
                    sent = next(prompt for prompt in self.chat.prompts() if prompt["text"] == "[interruption] Fix the Files app")
                    expect(sent.get("steps") or []).to(equal([]))

    with context("that a background task's notice arrives in the chat as a prompt"):
        with before.all:
            self.chat = HeadlessChat(self.server)
            self.chat.queue_work(["Write the scenarios", "Run the unit tier"])
            self.chat.start()
            self.chat.send(_NOTICE)

        with after.all:
            self.chat.stop()

        with it("should not be queued as the person's prompt"):
            expect(texts(self.chat.prompts())).to(equal(["Write the scenarios", "Run the unit tier"]))

    with context("that the agent gives a done goal its steps with prompt-queue.set_steps"):
        with before.all:
            self.chat = HeadlessChat(self.server, allowed_tools=("mcp__cdd__prompt-queue_set_steps",))
            self.goal = self.chat.queue_work(["Write the scenarios", "Run the unit tier"], done=1)[0]
            self.chat.start()
            # The cheapest model now and then answers without the call, or makes it with steps it cannot read; the
            # goal is the one last worked only once its call lands, so the chat is asked again until the steps are there.
            for _ask in range(_SET_STEPS_ASKS):
                self.chat.send(
                    f'Call the tool mcp__cdd__prompt-queue_set_steps once, with chat "{self.chat.id}", prompt "{self.goal["id"]}" '
                    'and steps [{"text": "Read the epic", "state": "done"}]. Then reply only: ok')
                if any(prompt["id"] == self.goal["id"] and prompt.get("steps") for prompt in self.chat.prompts()):
                    break

        with after.all:
            self.chat.stop()

        with context("that the person then sends a message after that turn, which asked nothing"):
            with before.all:
                self.chat.send("cut the text with an ellipsis")
                self.worked = next(prompt for prompt in self.chat.prompts() if prompt["id"] == self.goal["id"])

            with it("should give the message a goal of its own"):
                expect([text for text in texts(self.chat.prompts()) if "cut the text" in text]).to(equal(["[interruption] cut the text with an ellipsis"]))

            with it("should leave the goal the agent gave steps to with only those steps"):
                expect(self.worked["steps"]).to(equal([{"text": "Read the epic", "state": "done"}]))

            with it("should leave that goal done"):
                expect(self.worked.get("is_done", False)).to(be_true)
