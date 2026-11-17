import json

from mamba import describe, it, before
from expects import expect, equal, raise_error

from tools.prompt_queue.prompt_queue import PromptNotQueued, PromptQueue, handoff_steps

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

    with it("refuses to mark done a prompt the queue does not hold"):
        expect(lambda: self.queue.done("gone")).to(raise_error(PromptNotQueued))

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


with describe(handoff_steps):
    with it("reads the numbered steps of Approach for Next Agent, each with the lines that continue it"):
        expect(handoff_steps(HANDOFF)).to(equal(["Read this handoff", "Run the unit tier in the background", "Fix what it finds"]))
