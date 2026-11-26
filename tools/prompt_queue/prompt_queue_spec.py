import json

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mamba import after, context, describe, it, before
from expects import contain, expect, equal, match, raise_error

from harness.chat.chat import CHATS_FOLDER
from harness.installation.json_file import JsonFile, JsonFileBusy
from tools.prompt_queue.prompt_queue import ChatIdNotAnId, ChatNotKnown, PromptNotQueued, PromptQueue, QueueFileUnreadable, StepNotPlanned, StepStateUnknown



# The state the Claude app puts before a message sent while a board viewer is open: the viewer's live state, not
# anything the person typed.
VIEWER_STATE = (
    '<artifact-view-context artifact="c9a2df8e-628d-4905-9380-d29f23b38f13">\n'
    '{"context":{"mode":"board","dirty":false,"selected":[],"viewport":{"x":-4,"y":-11,"w":468,"h":1475}}}\n'
    "(The JSON line above is this viewer's live state in the artifact, not typed by the user.)\n"
    "<artifact-content-authored-by-others/>\n"
    "</artifact-view-context>"
)

with describe(PromptQueue):
    with before.each:
        import tempfile
        from pathlib import Path

        self.folder = Path(tempfile.mkdtemp())
        self.queue = PromptQueue("chat-1", self.folder / "prompt-queue.json")
        self.queue.add_all(["Write the scenarios", "  ", "Run the unit tier"])

    with it("queues each text in order, leaving out texts that are only spaces"):
        expect([prompt.text for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

    with it("keeps a prompt the agent marks done in its place, marked done, so the person sees it finish"):
        first = self.queue.prompts[0]
        self.queue.done(first.id)
        expect([(prompt.text, prompt.is_done) for prompt in self.queue.prompts]).to(equal([("Write the scenarios", True), ("Run the unit tier", False)]))

    with it("clears the finished prompts first, leaving the work still to do"):
        self.queue.done(self.queue.prompts[0].id)
        expect([prompt.text for prompt in self.queue.clear().prompts]).to(equal(["Run the unit tier"]))

    with it("takes nothing off when no prompt is done, so a second clear never throws away the work still to do"):
        expect([prompt.text for prompt in self.queue.clear().prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

    with it("keeps no copy in the queue archive when clear takes nothing off"):
        self.queue.clear()
        expect((self.folder / "queue-archive").exists()).to(equal(False))

    with it("keeps the robot a prompt is assigned to on the queue, so its robot's queue comes back after a reload"):
        self.queue.assign(self.queue.prompts[0].id, "Bolt")
        expect([prompt.robot for prompt in self.queue.prompts]).to(equal(["Bolt", ""]))

    with it("takes a prompt off its robot when it is assigned to no robot"):
        first = self.queue.prompts[0].id
        self.queue.assign(first, "Bolt")
        self.queue.assign(first, "")
        expect("robot" in self.queue.prompts[0].record).to(equal(False))

    with it("gives a card a robot already on the queue by its first spelling, matching the name with no regard to case or outer spaces"):
        first, second = (prompt.id for prompt in self.queue.prompts)
        self.queue.assign(first, "Bolt")
        self.queue.assign(second, "  bOLT ")
        expect([prompt.robot for prompt in self.queue.prompts]).to(equal(["Bolt", "Bolt"]))

    with context("that the lead gives a robot its theme"):
        with before.each:
            self.queue.assign(self.queue.prompts[0].id, "Bolt")
            self.queue.set_theme("Bolt", "  Whiteboard class diagram arrows  ")

        with it("keeps the robot's theme on the queue, one sentence beside the robot's name"):
            expect(self.queue.themes).to(equal({"Bolt": "Whiteboard class diagram arrows"}))

        with it("keeps the theme after a reload, so the robot's theme comes back with its cards"):
            expect(PromptQueue("chat-1", self.folder / "prompt-queue.json").themes).to(equal({"Bolt": "Whiteboard class diagram arrows"}))

        with it("gives the theme to the robot as the queue first spelled it, matching the name with no regard to case or outer spaces"):
            self.queue.set_theme(" bOLT", "Arrow routing")
            expect(self.queue.themes).to(equal({"Bolt": "Arrow routing"}))

        with it("takes the robot's theme off when it is set to only spaces"):
            self.queue.set_theme("Bolt", "  ")
            expect(self.queue.themes).to(equal({}))

    with it("holds no theme for a robot nobody gave one"):
        expect(self.queue.themes).to(equal({}))

    with it("reopens a done prompt so it runs again, its steps not started"):
        first = self.queue.prompts[0].id
        self.queue.set_steps(first, [{"text": "Write them", "state": "done"}])
        self.queue.done(first)
        self.queue.reopen(first)
        expect((self.queue.prompts[0].is_done, self.queue.prompts[0].listed_steps)).to(equal((False, [{"text": "Write them", "state": "pending"}])))

    with it("refuses to mark done a prompt the queue does not hold"):
        expect(lambda: self.queue.done("gone")).to(raise_error(PromptNotQueued))

    with it("names the chat whose queue it read and the prompts that queue holds, when it refuses one it does not hold"):
        held = ", ".join(prompt.id for prompt in self.queue.prompts)
        expect(lambda: self.queue.done("gone")).to(raise_error(PromptNotQueued, f"no prompt 'gone' is on the queue of chat chat-1, which holds {held}"))

    with it("says when a prompt was taken off the queue, when it refuses one the archive holds"):
        removed = self.queue.prompts[0].id
        self.queue.remove(removed)
        expect(lambda: self.queue.done(removed)).to(raise_error(PromptNotQueued, contain(f"{removed} was taken off the queue at ")))

    with it("keeps a copy of the prompts clear takes off, as JSON in the chat's queue archive"):
        self.queue.done(self.queue.prompts[0].id)
        self.queue.clear()
        archived = [json.loads(saved.read_text(encoding="utf-8")) for saved in (self.folder / "queue-archive").glob("*.json")]
        expect([[prompt["text"] for prompt in copy["prompts"]] for copy in archived]).to(equal([["Write the scenarios"]]))

    with context("that the person flushes the queue"):
        with before.each:
            self.queue.done(self.queue.prompts[0].id)
            self.before_flush = json.loads((self.folder / "prompt-queue.json").read_text(encoding="utf-8"))
            self.flushed = self.queue.flush()
            self.copies = sorted((self.folder / "queue-archive").glob("prompt-queue-*.json"))

        with it("keeps a copy of the whole queue file as it stood, named for when, in the chat's queue archive"):
            expect([json.loads(saved.read_text(encoding="utf-8")) for saved in self.copies]).to(equal([self.before_flush]))

        with it("names the copy prompt-queue and the time it was flushed"):
            expect(self.copies[0].name).to(match(r"^prompt-queue-\d{8}T\d{6}Z\.json$"))

        with it("takes the finished prompts off, leaving the work still to do in order"):
            expect([prompt.text for prompt in self.flushed.prompts]).to(equal(["Run the unit tier"]))

        with it("still says when a flushed prompt was taken off, when it refuses it"):
            flushed = self.before_flush["prompts"][0]["id"]
            expect(lambda: self.queue.done(flushed)).to(raise_error(PromptNotQueued, contain(f"{flushed} was taken off the queue at ")))

    with context("that the person flushes a queue with nothing finished"):
        with before.each:
            self.flushed = self.queue.flush()

        with it("still keeps a copy of the whole queue file"):
            expect(len(list((self.folder / "queue-archive").glob("prompt-queue-*.json")))).to(equal(1))

        with it("takes nothing off"):
            expect([prompt.text for prompt in self.flushed.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

    with it("keeps a copy of a prompt remove takes off, as JSON in the chat's queue archive"):
        self.queue.remove(self.queue.prompts[1].id)
        archived = [json.loads(saved.read_text(encoding="utf-8")) for saved in (self.folder / "queue-archive").glob("*.json")]
        expect([[prompt["text"] for prompt in copy["prompts"]] for copy in archived]).to(equal([["Run the unit tier"]]))

    with it("keeps its archive in the folder it is given, such as its session's folder"):
        session_archive = self.folder / ".sessions" / "simple-queue" / "queue-archive"
        queue = PromptQueue("chat-1", self.folder / "prompt-queue.json", session_archive)
        queue.done(queue.prompts[0].id)
        queue.clear()
        expect(len(list(session_archive.glob("*.json")))).to(equal(1))

    with it("archives into its session's work folder, in the ticket's worktree"):
        from types import SimpleNamespace
        worktree = self.folder / "worktree"
        call = SimpleNamespace(chat_id="chat-1", project=worktree, session=SimpleNamespace(work_folder=worktree / ".sessions" / "simple-queue"))
        queue = PromptQueue.load("chat-1", call=call)
        queue.add("Write the scenarios")
        queue.done(queue.prompts[0].id)
        queue.clear()
        expect(len(list((worktree / ".sessions" / "simple-queue" / "queue-archive").glob("*.json")))).to(equal(1))

    with it("files a message under a goal as a step not started, marked as the person's interruption"):
        goal = self.queue.prompts[0].id
        self.queue.add_interruption(goal, "cut the text with an ellipsis")
        expect(self.queue.prompts[0].listed_steps).to(equal([{"text": "[interruption] cut the text with an ellipsis", "state": "pending"}]))

    with it("reopens a done goal a message is filed under, since it has work again"):
        goal = self.queue.prompts[0].id
        self.queue.done(goal)
        self.queue.add_interruption(goal, "cut the text with an ellipsis")
        expect(self.queue.prompts[0].is_done).to(equal(False))

    with it("refuses to file a message under a goal the queue does not hold"):
        expect(lambda: self.queue.add_interruption("gone", "cut the text")).to(raise_error(PromptNotQueued))

    with it("queues a handoff's steps once, however often the chat switches to its session"):
        steps = ["Read this handoff", "Run the unit tier", "Fix what it finds"]
        expect([self.queue.queue_once("handoff-1.md", steps), self.queue.queue_once("handoff-1.md", steps)]).to(equal([3, 0]))

    with it("keeps a card's text when it is edited to only spaces"):
        self.queue.edit(self.queue.prompts[1].id, "   ")
        expect([prompt.text for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

    with it("files nothing under a goal for a message of only spaces"):
        self.queue.add_interruption(self.queue.prompts[0].id, "   ")
        expect("steps" in self.queue.prompts[0].record).to(equal(False))

    with it("files only the person's words of a message sent from a board viewer, leaving out the viewer's state"):
        goal = self.queue.prompts[0].id
        self.queue.add_interruption(goal, f"{VIEWER_STATE}\n\nwhy do the first 2 epics have no sub epics")
        expect(self.queue.prompts[0].listed_steps).to(equal([{"text": "[interruption] why do the first 2 epics have no sub epics", "state": "pending"}]))

    with it("files nothing under a goal for a message that holds only a board viewer's state"):
        self.queue.add_interruption(self.queue.prompts[0].id, VIEWER_STATE)
        expect("steps" in self.queue.prompts[0].record).to(equal(False))

    with it("queues only the person's words of a card sent from a board viewer"):
        self.queue.add(f"[interruption] {VIEWER_STATE}\n\nrepin to dev lane")
        expect(self.queue.prompts[-1].text).to(equal("[interruption] repin to dev lane"))

    with it("leaves a done goal done for a message of only spaces"):
        goal = self.queue.prompts[0].id
        self.queue.done(goal)
        self.queue.add_interruption(goal, "   ")
        expect(self.queue.prompts[0].is_done).to(equal(True))

    with it("leaves out a step whose text is only spaces"):
        goal = self.queue.prompts[0].id
        self.queue.set_steps(goal, [{"text": "Read the epic", "state": "done"}, {"text": "  ", "state": "pending"}])
        expect(self.queue.prompts[0].listed_steps).to(equal([{"text": "Read the epic", "state": "done"}]))

    with it("refuses a step whose state is not pending, in_progress or done, naming the state and the three it takes"):
        goal = self.queue.prompts[0].id
        expect(lambda: self.queue.set_steps(goal, [{"text": "Read the epic", "state": "completed"}])).to(raise_error(StepStateUnknown, contain("'completed'", "pending, in_progress, done")))

    with it("keeps the steps a prompt had when it refuses a step state"):
        goal = self.queue.prompts[0].id
        self.queue.set_steps(goal, [{"text": "Read the epic", "state": "done"}])
        try:
            self.queue.set_steps(goal, [{"text": "Read the epic", "state": "completed"}])
        except StepStateUnknown:
            pass
        expect(self.queue.prompts[0].listed_steps).to(equal([{"text": "Read the epic", "state": "done"}]))

    with context("whose first prompt has three steps planned, the first done"):
        with before.each:
            self.goal = self.queue.prompts[0].id
            self.queue.set_steps(self.goal, [{"text": "Read the epic", "state": "done"}, {"text": "Write them", "state": "in_progress"}, {"text": "Check them", "state": "pending"}])

        def steps(self) -> list[tuple[str, str]]:
            return [(step["text"], step["state"]) for step in self.queue.prompt(self.goal).listed_steps]

        with it("points its steps at the first step not done"):
            expect(self.queue.prompt(self.goal).step_pointer).to(equal(1))

        with it("moves a step to another place, counted from 1"):
            self.queue.move_step(self.goal, 3, 1)
            expect([text for text, _ in self.steps()]).to(equal(["Check them", "Read the epic", "Write them"]))

        with it("moves nothing for a place past the last step"):
            self.queue.move_step(self.goal, 1, 4)
            expect([text for text, _ in self.steps()]).to(equal(["Read the epic", "Write them", "Check them"]))

        with it("takes a step off"):
            self.queue.remove_step(self.goal, 2)
            expect([text for text, _ in self.steps()]).to(equal(["Read the epic", "Check them"]))

        with it("refuses a step the prompt does not have"):
            expect(lambda: self.queue.remove_step(self.goal, 4)).to(raise_error(StepNotPlanned))

        with it("moves the pointer on: its step done, the next worked"):
            self.queue.step_on(self.goal)
            expect([state for _, state in self.steps()]).to(equal(["done", "done", "in_progress"]))

        with it("moves the pointer back: the done step above worked again, every later step not started"):
            self.queue.step_back(self.goal)
            expect([state for _, state in self.steps()]).to(equal(["in_progress", "pending", "pending"]))

    with context("whose first goal gathered the person's interruptions, one of them done"):
        with before.each:
            self.goal = self.queue.prompts[0].id
            self.queue.assign(self.goal, "Bolt")
            self.queue.set_steps(self.goal, [
                {"text": "Read the epic", "state": "done"},
                {"text": "[interruption] cut the text with an ellipsis", "state": "done"},
                {"text": "[interruption] Fix the Files app", "state": "pending"},
                {"text": "Write the stories", "state": "in_progress"},
                {"text": "[interruption] Run the heavy tier", "state": "pending"},
            ])

        with context("that the goal is split"):
            with before.each:
                self.queue.split(self.goal)

            with it("puts each interruption not done on a card of its own, in order, right after the goal"):
                expect([prompt.text for prompt in self.queue.prompts]).to(equal([
                    "Write the scenarios", "[interruption] Fix the Files app", "[interruption] Run the heavy tier", "Run the unit tier"]))

            with it("leaves the goal its own steps and the interruptions already done"):
                expect([step["text"] for step in self.queue.prompt(self.goal).listed_steps]).to(equal([
                    "Read the epic", "[interruption] cut the text with an ellipsis", "Write the stories"]))

            with it("gives each card split off the goal's robot, so it stays in that robot's queue"):
                expect([prompt.robot for prompt in self.queue.prompts[1:3]]).to(equal(["Bolt", "Bolt"]))

        with it("changes nothing when the goal holds no interruption still to do"):
            other = self.queue.prompts[1].id
            self.queue.split(other)
            expect([prompt.text for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

        with it("refuses to split a goal the queue does not hold"):
            expect(lambda: self.queue.split("gone")).to(raise_error(PromptNotQueued))

    with context("whose first prompt has a file attached"):
        with before.each:
            self.goal = self.queue.prompts[0].id
            self.attached = Path(self.queue.attach(self.goal, "screenshot.png", "image/png", "aGk=").prompts[0].attachments[0])

        def archived_card(self) -> dict:
            return json.loads(next((self.folder / "queue-archive").glob("*.json")).read_text(encoding="utf-8"))["prompts"][0]

        with it("deletes the file with its card when the card is removed"):
            self.queue.remove(self.goal)
            expect(self.attached.exists()).to(equal(False))

        with it("deletes the file with its card when the card is cleared"):
            self.queue.done(self.goal)
            self.queue.clear()
            expect(self.attached.exists()).to(equal(False))

        with it("keeps the file of a card clear leaves on the queue"):
            self.queue.done(self.queue.prompts[1].id)
            self.queue.clear()
            expect(self.attached.exists()).to(equal(True))

        with it("names the file in the archived copy as deleted, no longer as attached"):
            self.queue.remove(self.goal)
            expect({key: self.archived_card().get(key) for key in ("attachments", "deleted_attachments")}).to(equal({"attachments": None, "deleted_attachments": [str(self.attached)]}))

        with it("leaves a file the card names outside the chat's attachments folder"):
            outside = self.folder / "notes.txt"
            outside.write_text("keep me", encoding="utf-8")
            record = json.loads((self.folder / "prompt-queue.json").read_text(encoding="utf-8"))
            record["prompts"][0]["attachments"].append(str(outside))
            (self.folder / "prompt-queue.json").write_text(json.dumps(record), encoding="utf-8")
            self.queue.remove(self.goal)
            expect(outside.exists()).to(equal(True))

    with context("whose first prompt is done and second asks a decision"):
        with before.each:
            self.queue.done(self.queue.prompts[0].id)
            self.queue.edit(self.queue.prompts[1].id, "[decision required] Keep the old name?")
            self.queue.add("Run the heavy tier")

        with it("has the first prompt that waits next, passing over the one asking a decision"):
            expect(self.queue.next.text).to(equal("Run the heavy tier"))

        with it("has none next once no prompt waits"):
            self.queue.done(self.queue.next.id)
            expect(self.queue.next).to(equal(None))

    # The stable and dev lanes' servers read one queue file, so a prompt is written in the keys both read.
    with it("writes a prompt in the keys the queue's file has always held, an optional one only when it has it"):
        self.queue.assign(self.queue.prompts[0].id, "Bolt")
        held = json.loads((self.folder / "prompt-queue.json").read_text(encoding="utf-8"))["prompts"]
        expect([sorted(card) for card in held]).to(equal([["id", "robot", "text"], ["id", "text"]]))

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
            expect([prompt.text for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

        with it("queues a new prompt after the prompts the file holds"):
            expect([prompt.text for prompt in self.queue.add("Run the heavy tier").prompts]).to(equal(["Write the scenarios", "Run the unit tier", "Run the heavy tier"]))

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

        with it("refuses a chat no chat folder is kept for, when the call came from another chat, naming it"):
            call = SimpleNamespace(chat_id="chat-1", session=None)
            expect(lambda: PromptQueue.load("chat-9", call=call)).to(raise_error(ChatNotKnown, contain("no chat 'chat-9' is known")))

        with it("makes no folder for a chat it does not know"):
            try:
                PromptQueue.load("chat-9", call=SimpleNamespace(chat_id="chat-1", session=None)).add("Report the defect")
            except ChatNotKnown:
                pass
            expect((CHATS_FOLDER.path / "chat-9").exists()).to(equal(False))

        with it("queues on another chat whose folder is kept"):
            (CHATS_FOLDER.path / "chat-2").mkdir(parents=True)
            PromptQueue.load("chat-2", call=SimpleNamespace(chat_id="chat-1", session=None)).add("Report the defect")
            expect([prompt.text for prompt in PromptQueue.of_chat("chat-2").prompts]).to(equal(["Report the defect"]))

        with it("queues on the calling chat's own queue the first time, before its folder is there"):
            PromptQueue.load("chat-1", call=SimpleNamespace(chat_id="chat-1", session=None)).add("Write the scenarios")
            expect((CHATS_FOLDER.path / "chat-1" / "prompt-queue.json").is_file()).to(equal(True))

        with it("writes no queue outside the chats folder for a chat id it refuses"):
            try:
                PromptQueue.of_chat("..\\escape-chat").add("Write the scenarios")
            except ChatIdNotAnId:
                pass
            expect((self.folder / "escape-chat").exists()).to(equal(False))

    with context("that the person sent a message to the chat"):
        with it("reads a question that asks for no work as only talk"):
            expect(self.queue.is_only_talk("why is there no flush button?")).to(equal({"is_only_talk": True}))

        with it("reads a question without its question mark as only talk"):
            expect(self.queue.is_only_talk("where is the flush button")).to(equal({"is_only_talk": True}))

        with it("reads an answer as only talk"):
            expect(self.queue.is_only_talk("yes")).to(equal({"is_only_talk": True}))

        with it("reads an acknowledgement as only talk"):
            expect(self.queue.is_only_talk("ok")).to(equal({"is_only_talk": True}))

        with it("reads a message of only marks as only talk"):
            expect(self.queue.is_only_talk("???")).to(equal({"is_only_talk": True}))

        with it("reads a question sent from a board viewer by the person's words alone, as only talk"):
            expect(self.queue.is_only_talk(f"{VIEWER_STATE}\n\n?")).to(equal({"is_only_talk": True}))

        with it("reads a request for work as work"):
            expect(self.queue.is_only_talk("Fix the Files app")).to(equal({"is_only_talk": False}))

        with it("reads a question that also asks for work as work"):
            expect(self.queue.is_only_talk("why is there no flush button? please add one")).to(equal({"is_only_talk": False}))

        with it("reads a long question as work, since it is likely to ask for something"):
            question = "why does the board show every epic twice when I open it from the chat bar after a repin of the lane?"
            expect(self.queue.is_only_talk(question)).to(equal({"is_only_talk": False}))

        with it("reads a message holding a paste as work, since a paste is the person's material for work"):
            expect(self.queue.is_only_talk('<pasted_content id="1">notes</pasted_content> ok?')).to(equal({"is_only_talk": False}))

        with it("reads a request for work sent from a board viewer as work"):
            expect(self.queue.is_only_talk(f"{VIEWER_STATE}\n\nPlease add a flush button")).to(equal({"is_only_talk": False}))

    with context("of a chat whose queue was never switched on"):
        with it("is off, so the chat's messages, hand-outs and robots stay out of the way"):
            expect(self.queue.is_on).to(equal(False))

        with context("that the person switches the queue on"):
            with before.each:
                self.queue.switch_on()

            with it("is on"):
                expect(self.queue.is_on).to(equal(True))

            with it("remembers it is on for the chat, read again from its file"):
                expect(PromptQueue("chat-1", self.folder / "prompt-queue.json").is_on).to(equal(True))

            with it("keeps the prompts queued"):
                expect([prompt.text for prompt in self.queue.prompts]).to(equal(["Write the scenarios", "Run the unit tier"]))

            with it("stays on when a prompt is queued after"):
                self.queue.add("Fix the Files app")
                expect(self.queue.is_on).to(equal(True))

            with context("that the person then switches it off"):
                with before.each:
                    self.queue.switch_off()

                with it("is off"):
                    expect(self.queue.is_on).to(equal(False))
