"""Heavy spec: an agent's chat queues and works through its prompts with the prompt-queue tools of a real cdd server."""
import json
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.chat.chat import CHATS_FOLDER
from harness.mcp.spec_support import SpecChat, SpecServer

TOOLSETS = ("tools.prompt_queue.prompt_queue:PromptQueue",)


def texts(queue: dict) -> list[str]:
    return [prompt["text"] for prompt in queue["prompts"]]


# (S) Agent --> Queue Prompts Through The Cdd Server
with description("a chat's prompt queue through the cdd server") as self:
    with before.all:
        # Chat folders go to a throwaway folder, never the person's own ~/.claude/cdd-chats.
        self.prior_chats = os.environ.get("CDD_CHATS_FOLDER")
        os.environ["CDD_CHATS_FOLDER"] = tempfile.mkdtemp(prefix="queue-chats-")
        self.server = SpecServer(TOOLSETS)
        self.server.start()
        self.project = Path(tempfile.mkdtemp(prefix="queue-project-"))
        self.chat = SpecChat(self.server, self.project)

    with after.all:
        self.server.stop()
        if self.prior_chats is None:
            os.environ.pop("CDD_CHATS_FOLDER", None)
        else:
            os.environ["CDD_CHATS_FOLDER"] = self.prior_chats

    with context("that the agent queues a list of work naming no chat"):
        with before.all:
            self.queued = self.chat.answer("prompt-queue.add_all", chat="", texts=["Write the scenarios", "Run the unit tier"])

        with it("should hold the work on the calling chat's queue, in order"):
            expect(texts(self.chat.answer("prompt-queue.show", chat=""))).to(equal(["Write the scenarios", "Run the unit tier"]))

        with context("that the agent marks the first prompt done"):
            with before.all:
                first = self.queued["prompts"][0]["id"]
                self.left = self.chat.answer("prompt-queue.done", chat="", prompt=first)

            with it("should keep the prompt in its place, marked done"):
                expect([(prompt["text"], prompt.get("is_done", False)) for prompt in self.left["prompts"]]).to(equal([("Write the scenarios", True), ("Run the unit tier", False)]))

            with context("that the person sends a message about the done goal"):
                with before.all:
                    first = self.queued["prompts"][0]["id"]
                    self.filed = self.chat.answer("prompt-queue.add_interruption", chat="", prompt=first, text="cut the text with an ellipsis")

                with it("should file it under that goal as a step not started, marked as the person's interruption, and open the goal again"):
                    goal = self.filed["prompts"][0]
                    expect([goal["steps"], goal.get("is_done", False)]).to(equal([[{"text": "[interruption] cut the text with an ellipsis", "state": "pending"}], False]))

                with after.all:
                    self.chat.answer("prompt-queue.done", chat="", prompt=self.queued["prompts"][0]["id"])

            with context("that the agent clears the queue"):
                with before.all:
                    self.cleared = self.chat.answer("prompt-queue.clear", chat="")

                # The chat works in its project's main session, whose work folder keeps the queue archive.
                with it("should keep a copy of the prompts clear takes off, as JSON in the queue archive of the session the chat works in"):
                    archive = self.project / ".sessions" / "main" / "queue-archive"
                    archived = [json.loads(saved.read_text(encoding="utf-8")) for saved in archive.glob("*.json")]
                    expect([[prompt["text"] for prompt in copy["prompts"]] for copy in archived]).to(equal([["Write the scenarios"]]))

                with it("should leave the work still to do"):
                    expect(texts(self.cleared)).to(equal(["Run the unit tier"]))

        with context("that the person flushes the queue"):
            with before.all:
                self.flushed = self.chat.answer("prompt-queue.flush", chat="")

            with it("should keep a copy of the whole queue file in the queue archive of the session the chat works in"):
                archive = self.project / ".sessions" / "main" / "queue-archive"
                copies = [json.loads(saved.read_text(encoding="utf-8")) for saved in archive.glob("prompt-queue-*.json")]
                expect([texts(copy) for copy in copies]).to(equal([["Run the unit tier"]]))

            with it("should take nothing off when nothing is done"):
                expect(texts(self.flushed)).to(equal(["Run the unit tier"]))

        with context("that another chat reads its own queue"):
            with it("should hold none of this chat's work"):
                expect(texts(SpecChat(self.server, self.project).answer("prompt-queue.show", chat=""))).to(equal([]))

    with context("that an agent names a chat by a path out of the chats folder"):
        with before.all:
            _, self.refusal = self.chat.call("prompt-queue.add", chat="..\\escape-chat", text="Run the heavy tier")

        with it("should refuse the call, since a chat id is never a path"):
            expect(self.refusal).to(contain("escape-chat' is not a chat id"))

        with it("should write no queue outside the chats folder"):
            expect((CHATS_FOLDER.path.parent / "escape-chat").exists()).to(equal(False))

    # Exploratory testing, sparky-09: a mistyped chat id made a new queue nobody reads, and the call answered success.
    with context("that an agent queues work on a chat the server has never seen"):
        with before.all:
            _, self.unknown_refusal = self.chat.call("prompt-queue.add", chat="some-other-chat", text="Report the defect")

        with it("should refuse the call, naming the chat"):
            expect(self.unknown_refusal).to(contain("no chat 'some-other-chat' is known"))

        with it("should make no folder for that chat"):
            expect((CHATS_FOLDER.path / "some-other-chat").exists()).to(equal(False))

    with context("that an agent splits a goal that gathered the person's interruptions"):
        with before.all:
            self.split_chat = SpecChat(self.server, self.project)
            goal = self.split_chat.answer("prompt-queue.add_all", chat="", texts=["Write the scenarios", "Run the unit tier"])["prompts"][0]["id"]
            self.split_chat.answer("prompt-queue.add_interruption", chat="", prompt=goal, text="Fix the Files app")
            self.split = self.split_chat.answer("prompt-queue.split", chat="", prompt=goal)

        with it("should put the interruption on a card of its own right after the goal"):
            expect(texts(self.split)).to(equal(["Write the scenarios", "[interruption] Fix the Files app", "Run the unit tier"]))

        with it("should leave the goal no step from it"):
            expect(self.split["prompts"][0]["steps"]).to(equal([]))

    with context("that an agent gives a step a state a step does not have"):
        with before.all:
            self.steps_chat = SpecChat(self.server, self.project)
            self.goal = self.steps_chat.answer("prompt-queue.add", chat="", text="Write the scenarios")["prompts"][0]["id"]
            _, self.refusal = self.steps_chat.call("prompt-queue.set_steps", chat="", prompt=self.goal, steps=[{"text": "Read the epic", "state": "completed"}])

        with it("should refuse the call, naming the state and the three a step has"):
            expect(self.refusal).to(contain("'completed' is not a step's state, which is one of pending, in_progress, done"))

        with it("should leave the prompt without steps"):
            expect(self.steps_chat.answer("prompt-queue.show", chat="")["prompts"][0]["steps"]).to(equal([]))
