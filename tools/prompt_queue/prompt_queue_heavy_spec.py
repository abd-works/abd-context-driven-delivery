"""Heavy spec: an agent's chat queues and works through its prompts with the prompt-queue tools of a real cdd server."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import SpecChat, SpecServer

TOOLSETS = ("tools.prompt_queue.prompt_queue:PromptQueue",)


def texts(queue: dict) -> list[str]:
    return [prompt["text"] for prompt in queue["prompts"]]


# (S) Agent --> Queue Prompts Through The Cdd Server
with description("a chat's prompt queue through the cdd server") as self:
    with before.all:
        self.server = SpecServer(TOOLSETS)
        self.server.start()
        self.project = Path(tempfile.mkdtemp(prefix="queue-project-"))
        self.chat = SpecChat(self.server, self.project)

    with after.all:
        self.server.stop()

    with context("that the agent queues a list of work naming no chat"):
        with before.all:
            self.queued = self.chat.answer("prompt-queue.add_all", chat="", texts=["Write the scenarios", "Run the unit tier"])

        with it("should hold the work on the calling chat's queue, in order"):
            expect(texts(self.chat.answer("prompt-queue.show", chat=""))).to(equal(["Write the scenarios", "Run the unit tier"]))

        with context("that the agent marks the first prompt done"):
            with before.all:
                first = self.queued["prompts"][0]["id"]
                self.left = self.chat.answer("prompt-queue.done", chat="", prompt=first)

            with it("should keep only the work still to do"):
                expect(texts(self.left)).to(equal(["Run the unit tier"]))

        with context("that another chat reads its own queue"):
            with it("should hold none of this chat's work"):
                expect(texts(SpecChat(self.server, self.project).answer("prompt-queue.show", chat=""))).to(equal([]))
