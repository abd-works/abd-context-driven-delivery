import json

import os
from types import SimpleNamespace
from unittest.mock import patch

from mamba import after, context, describe, it, before
from expects import contain, expect, equal, raise_error

from harness.chat.chat import CHATS_FOLDER
from harness.installation.json_file import JsonFile, JsonFileBusy
from tools.prompt_queue.prompt_queue import ChatIdNotAnId, PromptNotQueued, PromptQueue, QueueFileUnreadable, StepStateUnknown, handoff_steps

HANDOFF = """# Handoff

## Approach for Next Agent

1. Read this handoff
2) Run the unit tier
   in the background
3. Fix what it finds

## Outstanding

1. Not a step
"""


with describe(PromptQueue):
    with before.each:
        import tempfile
        from pathlib import Path

        self.folder = Path(tempfile.mkdtemp())
        self.queue = PromptQueue("chat-1", self.folder / "prompt-queue.json")
        self.queue.add_all(["Write the scenarios", "  ", "Run the unit tier"])

    with it("queues each text in order, leaving out texts that are only spaces"):
        expect([prompt["text"] for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

    with it("keeps a prompt the agent marks done in its place, marked done, so the person sees it finish"):
        first = self.queue.prompts[0]
        self.queue.done(first["id"])
        expect([(prompt["text"], prompt.get("is_done", False)) for prompt in self.queue.prompts]).to(equal([("Write the scenarios", True), ("Run the unit tier", False)]))

    with it("clears the finished prompts first, leaving the work still to do"):
        self.queue.done(self.queue.prompts[0]["id"])
        expect([prompt["text"] for prompt in self.queue.clear().prompts]).to(equal(["Run the unit tier"]))

    with it("clears every prompt when none is finished"):
        expect(self.queue.clear().prompts).to(equal([]))

    with it("keeps the robot a prompt is assigned to on the queue, so its robot's queue comes back after a reload"):
        self.queue.assign(self.queue.prompts[0]["id"], "Bolt")
        expect([prompt.get("robot", "") for prompt in self.queue.prompts]).to(equal(["Bolt", ""]))

    with it("takes a prompt off its robot when it is assigned to no robot"):
        first = self.queue.prompts[0]["id"]
        self.queue.assign(first, "Bolt")
        self.queue.assign(first, "")
        expect("robot" in self.queue.prompts[0]).to(equal(False))

    with it("reopens a done prompt so it runs again, its steps not started"):
        first = self.queue.prompts[0]["id"]
        self.queue.set_steps(first, [{"text": "Write them", "state": "done"}])
        self.queue.done(first)
        self.queue.reopen(first)
        expect((self.queue.prompts[0].get("is_done", False), self.queue.prompts[0]["steps"])).to(equal((False, [{"text": "Write them", "state": "pending"}])))

    with it("refuses to mark done a prompt the queue does not hold"):
        expect(lambda: self.queue.done("gone")).to(raise_error(PromptNotQueued))

    with it("names the chat whose queue it read and the prompts that queue holds, when it refuses one it does not hold"):
        held = ", ".join(prompt["id"] for prompt in self.queue.prompts)
        expect(lambda: self.queue.done("gone")).to(raise_error(PromptNotQueued, f"no prompt 'gone' is on the queue of chat chat-1, which holds {held}"))

    with it("says when a prompt was taken off the queue, when it refuses one the archive holds"):
        removed = self.queue.prompts[0]["id"]
        self.queue.remove(removed)
        expect(lambda: self.queue.done(removed)).to(raise_error(PromptNotQueued, contain(f"{removed} was taken off the queue at ")))

    with it("keeps a copy of the prompts clear takes off, as JSON in the chat's queue archive"):
        self.queue.clear()
        archived = [json.loads(saved.read_text(encoding="utf-8")) for saved in (self.folder / "queue-archive").glob("*.json")]
        expect([[prompt["text"] for prompt in copy["prompts"]] for copy in archived]).to(equal([["Write the scenarios", "Run the unit tier"]]))

    with it("keeps a copy of a prompt remove takes off, as JSON in the chat's queue archive"):
        self.queue.remove(self.queue.prompts[1]["id"])
        archived = [json.loads(saved.read_text(encoding="utf-8")) for saved in (self.folder / "queue-archive").glob("*.json")]
        expect([[prompt["text"] for prompt in copy["prompts"]] for copy in archived]).to(equal([["Run the unit tier"]]))

    with it("keeps its archive in the folder it is given, such as its session's folder"):
        session_archive = self.folder / ".sessions" / "simple-queue" / "queue-archive"
        queue = PromptQueue("chat-1", self.folder / "prompt-queue.json", session_archive)
        queue.clear()
        expect(len(list(session_archive.glob("*.json")))).to(equal(1))

    with it("archives into its session's work folder, in the ticket's worktree"):
        from types import SimpleNamespace
        worktree = self.folder / "worktree"
        call = SimpleNamespace(chat_id="chat-1", project=worktree, session=SimpleNamespace(work_folder=worktree / ".sessions" / "simple-queue"))
        queue = PromptQueue.load("chat-1", call=call)
        queue.add("Write the scenarios")
        queue.clear()
        expect(len(list((worktree / ".sessions" / "simple-queue" / "queue-archive").glob("*.json")))).to(equal(1))

    with it("files a message under a goal as a step not started, marked as the person's interruption"):
        goal = self.queue.prompts[0]["id"]
        self.queue.add_interruption(goal, "cut the text with an ellipsis")
        expect(self.queue.prompts[0]["steps"]).to(equal([{"text": "[interruption] cut the text with an ellipsis", "state": "pending"}]))

    with it("reopens a done goal a message is filed under, since it has work again"):
        goal = self.queue.prompts[0]["id"]
        self.queue.done(goal)
        self.queue.add_interruption(goal, "cut the text with an ellipsis")
        expect(self.queue.prompts[0].get("is_done", False)).to(equal(False))

    with it("refuses to file a message under a goal the queue does not hold"):
        expect(lambda: self.queue.add_interruption("gone", "cut the text")).to(raise_error(PromptNotQueued))

    with it("queues a handoff's steps once, however often the chat switches to its session"):
        handoff = self.folder / "handoff-1.md"
        handoff.write_text(HANDOFF, encoding="utf-8")
        expect([self.queue.queue_handoff(handoff), self.queue.queue_handoff(handoff)]).to(equal([3, 0]))

    with it("keeps a card's text when it is edited to only spaces"):
        self.queue.edit(self.queue.prompts[1]["id"], "   ")
        expect([prompt["text"] for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

    with it("files nothing under a goal for a message of only spaces"):
        self.queue.add_interruption(self.queue.prompts[0]["id"], "   ")
        expect("steps" in self.queue.prompts[0]).to(equal(False))

    with it("leaves a done goal done for a message of only spaces"):
        goal = self.queue.prompts[0]["id"]
        self.queue.done(goal)
        self.queue.add_interruption(goal, "   ")
        expect(self.queue.prompts[0].get("is_done", False)).to(equal(True))

    with it("leaves out a step whose text is only spaces"):
        goal = self.queue.prompts[0]["id"]
        self.queue.set_steps(goal, [{"text": "Read the epic", "state": "done"}, {"text": "  ", "state": "pending"}])
        expect(self.queue.prompts[0]["steps"]).to(equal([{"text": "Read the epic", "state": "done"}]))

    with it("refuses a step whose state is not pending, in_progress or done, naming the state and the three it takes"):
        goal = self.queue.prompts[0]["id"]
        expect(lambda: self.queue.set_steps(goal, [{"text": "Read the epic", "state": "completed"}])).to(raise_error(StepStateUnknown, contain("'completed'", "pending, in_progress, done")))

    with it("keeps the steps a prompt had when it refuses a step state"):
        goal = self.queue.prompts[0]["id"]
        self.queue.set_steps(goal, [{"text": "Read the epic", "state": "done"}])
        try:
            self.queue.set_steps(goal, [{"text": "Read the epic", "state": "completed"}])
        except StepStateUnknown:
            pass
        expect(self.queue.prompts[0]["steps"]).to(equal([{"text": "Read the epic", "state": "done"}]))

    with context("whose file another caller holds for a change"):
        with it("refuses a change it waited for in vain, saying the file is held"):
            another_caller = JsonFile(self.folder / "prompt-queue.json").held()
            with another_caller:
                with patch("harness.installation.json_file._HOLD_SECONDS", 0):
                    expect(lambda: self.queue.add("Run the heavy tier")).to(raise_error(JsonFileBusy, contain("prompt-queue.json is held for a change")))

    with context("whose file a person saved with a byte-order mark"):
        with before.each:
            file = self.folder / "prompt-queue.json"
            file.write_text(file.read_text(encoding="utf-8"), encoding="utf-8-sig")

        with it("holds the prompts the file holds"):
            expect([prompt["text"] for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

        with it("queues a new prompt after the prompts the file holds"):
            expect([prompt["text"] for prompt in self.queue.add("Run the heavy tier").prompts]).to(equal(["Write the scenarios", "Run the unit tier", "Run the heavy tier"]))

    with context("whose file is cut off half way"):
        with before.each:
            self.file = self.folder / "prompt-queue.json"
            self.damaged = self.file.read_text(encoding="utf-8")[:40]
            self.file.write_text(self.damaged, encoding="utf-8")

        with it("refuses to show the queue, naming the file"):
            expect(lambda: self.queue.prompts).to(raise_error(QueueFileUnreadable, contain(str(self.file))))

        with it("refuses to queue a prompt"):
            expect(lambda: self.queue.add("Run the heavy tier")).to(raise_error(QueueFileUnreadable))

        with it("writes nothing over the file, so what it holds stays for a person to repair"):
            try:
                self.queue.add("Run the heavy tier")
            except QueueFileUnreadable:
                pass
            expect(self.file.read_text(encoding="utf-8")).to(equal(self.damaged))

    with context("whose file is empty"):
        with it("refuses to show the queue"):
            (self.folder / "prompt-queue.json").write_text("", encoding="utf-8")
            expect(lambda: self.queue.prompts).to(raise_error(QueueFileUnreadable))

    with context("whose file holds a list in place of a queue"):
        with it("refuses to show the queue"):
            (self.folder / "prompt-queue.json").write_text("[1, 2]", encoding="utf-8")
            expect(lambda: self.queue.prompts).to(raise_error(QueueFileUnreadable))

    with context("whose file holds prompts that are not a list of cards"):
        with it("refuses to show the queue, naming the file and what its prompts are"):
            file = self.folder / "prompt-queue.json"
            file.write_text('{"prompts": null}', encoding="utf-8")
            expect(lambda: self.queue.prompts).to(raise_error(QueueFileUnreadable, contain(str(file), "its prompts are NoneType, not a list of cards")))

        with it("refuses to queue a prompt after the letters of a text"):
            (self.folder / "prompt-queue.json").write_text('{"prompts": "abc"}', encoding="utf-8")
            expect(lambda: self.queue.add("Run the heavy tier")).to(raise_error(QueueFileUnreadable, contain("its prompts are str, not a list of cards")))

    with context("whose file holds a card with no id"):
        with it("refuses a change to another card, naming the file and the card"):
            file = self.folder / "prompt-queue.json"
            file.write_text('{"prompts": [{"id": "a", "text": "Write the scenarios"}, {"text": "Run the unit tier"}]}', encoding="utf-8")
            expect(lambda: self.queue.done("a")).to(raise_error(QueueFileUnreadable, contain(str(file), "card 2 has no id", "Run the unit tier")))

    with context("whose file holds two cards with one id"):
        with it("refuses a change to that id, naming the file and the id the cards share"):
            file = self.folder / "prompt-queue.json"
            file.write_text('{"prompts": [{"id": "a", "text": "Write the scenarios"}, {"id": "a", "text": "Run the unit tier"}]}', encoding="utf-8")
            expect(lambda: self.queue.done("a")).to(raise_error(QueueFileUnreadable, contain(str(file), "cards 1 and 2 share the id 'a'")))

    with context("that is asked for by a chat id"):
        with before.each:
            self.prior_chats = os.environ.get("CDD_CHATS_FOLDER")
            os.environ["CDD_CHATS_FOLDER"] = str(self.folder / "chats")

        with after.each:
            if self.prior_chats is None:
                os.environ.pop("CDD_CHATS_FOLDER", None)
            else:
                os.environ["CDD_CHATS_FOLDER"] = self.prior_chats

        with it("is kept in that chat's own folder"):
            PromptQueue.of_chat("chat-2").add("Write the scenarios")
            expect((CHATS_FOLDER.path / "chat-2" / "prompt-queue.json").is_file()).to(equal(True))

        with it("refuses a chat id that climbs out of the chats folder, naming it"):
            expect(lambda: PromptQueue.of_chat("..\\escape-chat")).to(raise_error(ChatIdNotAnId, contain("escape-chat' is not a chat id")))

        with it("refuses a chat id that holds a folder separator"):
            expect(lambda: PromptQueue.of_chat("chats/chat-2")).to(raise_error(ChatIdNotAnId))

        with it("refuses a chat id that names a drive"):
            expect(lambda: PromptQueue.of_chat("C:chat-2")).to(raise_error(ChatIdNotAnId))

        with it("refuses a chat id of two dots"):
            expect(lambda: PromptQueue.of_chat("..")).to(raise_error(ChatIdNotAnId))

        with it("refuses an empty chat id from a call that came from no chat"):
            expect(lambda: PromptQueue.load(" ", call=SimpleNamespace(chat_id="", session=None))).to(raise_error(ChatIdNotAnId))

        with it("writes no queue outside the chats folder for a chat id it refuses"):
            try:
                PromptQueue.of_chat("..\\escape-chat").add("Write the scenarios")
            except ChatIdNotAnId:
                pass
            expect((self.folder / "escape-chat").exists()).to(equal(False))


with describe(handoff_steps):
    with it("reads the numbered steps of Approach for Next Agent, each with the lines that continue it"):
        expect(handoff_steps(HANDOFF)).to(equal(["Read this handoff", "Run the unit tier in the background", "Fix what it finds"]))
