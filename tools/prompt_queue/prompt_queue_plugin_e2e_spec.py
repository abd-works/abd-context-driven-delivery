"""E2e spec: the prompt-queue plugin, loaded into a real Claude Code chat run headless (``claude -p``), keeps the chat's
queue on a real cdd server.

The plugin's own tests (hooks/register.test.tsx) stub the cdd server, the stored state and the clock; this spec runs the
same hooks for real. A SpecServer serves the PromptQueue toolset; a scratch project's .mcp.json names it ``cdd``; the CLI
at CLAUDE_CODE_EXECPATH, else claude on the PATH, loads the plugin from this checkout with ``--plugin-dir`` and takes each message through
stream-json input, so the plugin's prompt.submit, tool.call and turn hooks run as they do in a chat. The queue is then
read back through the server with prompt-queue.show.

The scratch .mcp.json names the chat in the header the app's connect script sends, so a call that names no chat, or the
chat's id, reaches this chat's queue, as it does in the app.

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

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.mcp_address import CHAT_HEADER
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
# How long the chat stays quiet after a result before the messages sent during a turn count as all answered.
_QUIET_SECONDS = 45
_NOTICE = "<task-notification> <task-id>b1</task-id> <status>completed</status> </task-notification>"
# What the Claude app puts before a message sent while a board viewer is open: the viewer's live state, never the
# person's words. Its card name is one no message of the person's uses, so a title holding it holds the viewer's state.
_VIEWER_STATE = '<artifact-view-context>{"board": "Story map", "selected": "Zanzibar lane"}</artifact-view-context>\n'
_QUESTION = _VIEWER_STATE + "why is the band grey?"
_ANSWER = "yes"
_WORK = _VIEWER_STATE + "Please add a flush button to the queue band"
# A turn that works long enough for messages to arrive while it runs: a command in the foreground, since the chat
# refuses a bare sleep.
_LONG_TURN = "Run the Bash command `ping -n 31 127.0.0.1` in the foreground, then reply only: pinged"
# The tools the agent may call without asking: the queue's, to place work, and Bash, for the long turn.
_QUEUE_TOOLS = (
    "mcp__cdd__prompt-queue_add", "mcp__cdd__prompt-queue_add_interruption", "mcp__cdd__prompt-queue_show",
    "mcp__cdd__prompt-queue_set_steps", "mcp__cdd__prompt-queue_remove", "Bash",
)


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
        self._servers.write_text(json.dumps({"mcpServers": {"cdd": {"type": "http", "url": server.url, "headers": {CHAT_HEADER: self.id}}}}), encoding="utf-8")
        self._queue = SpecChat(server, self._project, chat_id=self.id)
        self._allowed_tools = allowed_tools
        self._process: subprocess.Popen | None = None
        self._lines: queue.Queue[str] = queue.Queue()
        # Each tool the agent called, with its input, so a failing example can say what the chat did.
        self.calls: list[str] = []

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
        self._write(text)
        self._wait_for(lambda event: event.get("type") == "result")

    def send_while_working(self, turn: str, messages: list[str]) -> None:
        """Send turn, and once its agent is calling a tool, send each of messages while that turn still works; then
        wait until every message is answered and the chat is quiet."""
        if self._process is None:
            raise ClaudeCodeNotFoundError()
        self._write(turn)
        self._wait_for(_runs_a_command)
        for message in messages:
            self._write(message)
        self._wait_for(lambda event: event.get("type") == "result")
        try:
            while True:
                self._lines.get(timeout=_QUIET_SECONDS)
        except queue.Empty:
            pass

    def _write(self, text: str) -> None:
        self._process.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        self._process.stdin.flush()

    def _wait_for(self, arrived) -> None:
        while not arrived(json.loads(self._lines.get(timeout=_TURN_SECONDS))):
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
                self._note_calls(line)
                self._lines.put(line)

    def _note_calls(self, line: str) -> None:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return
        if _calls_a_tool(event):
            self.calls += [f'{block["name"]} {json.dumps(block.get("input"))[:200]}' for block in event["message"]["content"] if block.get("type") == "tool_use"]


def _calls_a_tool(event: dict) -> bool:
    """Whether a line of the chat's output is the agent calling a tool, so its turn is still working."""
    content = event.get("message", {}).get("content") if event.get("type") == "assistant" else None
    return isinstance(content, list) and any(block.get("type") == "tool_use" for block in content)


def _runs_a_command(event: dict) -> bool:
    """Whether a line of the chat's output is the agent starting the long turn's command."""
    return _calls_a_tool(event) and any(block.get("name") == "Bash" for block in event["message"]["content"])


def texts(prompts: list[dict]) -> list[str]:
    return [prompt["text"] for prompt in prompts]


def entries(prompts: list[dict]) -> list[str]:
    """Every title the queue shows: each card's text, and each step's text under its card's."""
    return [title for prompt in prompts for title in [prompt["text"], *(f'{prompt["text"]} / {step["text"]}' for step in prompt.get("steps") or [])]]


def placed(before: list[dict], after: list[dict]) -> list[str]:
    """The titles the queue shows after that it did not show before: the cards and steps the chat put on it."""
    shown = set(entries(before))
    return [title for title in entries(after) if title not in shown]


def _holds_viewer_state(title: str) -> bool:
    return "Zanzibar" in title or "artifact-view-context" in title


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

    with context("that the queue holds a done goal and one to do, and no turn is working"):
        with before.all:
            self.chat = HeadlessChat(self.server, allowed_tools=_QUEUE_TOOLS)
            self.start = self.chat.queue_work(["Write the scenarios", "Run the unit tier"], done=1)
            self.chat.start()

        with after.all:
            self.chat.stop()

        with context("that the person asks a question, with a board viewer open"):
            with before.all:
                self.chat.send(_QUESTION)
                self.asked = self.chat.prompts()

            with it("should put nothing on the queue"):
                expect(placed(self.start, self.asked)).to(equal([]))

            with context("that the person then answers"):
                with before.all:
                    self.chat.send(_ANSWER)
                    self.answered = self.chat.prompts()

                with it("should put nothing on the queue"):
                    expect(placed(self.asked, self.answered)).to(equal([]))

                with context("that the person then asks for work, with a board viewer open"):
                    with before.all:
                        self.chat.send(_WORK)
                        self.worked = self.chat.prompts()

                    with it("should put the work on the queue"):
                        expect([title for title in placed(self.answered, self.worked) if "flush" in title.lower()]).not_to(equal([]))

                    with it("should keep the viewer's state out of every title"):
                        expect([title for title in entries(self.worked) if _holds_viewer_state(title)]).to(equal([]))

    with context("that a turn is working"):
        with before.all:
            self.chat = HeadlessChat(self.server, allowed_tools=_QUEUE_TOOLS)
            self.start = self.chat.queue_work(["Write the scenarios", "Run the unit tier"], done=1)
            self.chat.start()

        with after.all:
            self.chat.stop()

        with context("that the person sends a question, an answer and a work request, with a board viewer open"):
            with before.all:
                self.chat.send_while_working(_LONG_TURN, [_QUESTION, _ANSWER, _WORK])
                # The turn's own message asks for work too, so the agent may queue it; it is not one of the three.
                self.placed = [title for title in placed(self.start, self.chat.prompts()) if "ping" not in title.lower()]

            with it("should put the work request on the queue"):
                expect([title for title in self.placed if "flush" in title.lower()]).not_to(equal([]))

            with it("should put nothing else on the queue"):
                expect([title for title in self.placed if "flush" not in title.lower()]).to(equal([]))

            with it("should keep the viewer's state out of every title"):
                expect([title for title in entries(self.chat.prompts()) if _holds_viewer_state(title)]).to(equal([]))

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
