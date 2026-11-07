"""The chats the cdd-board mod connects, and the commands a person sends them, kept as a folder per chat."""
import json
import os
import sys
import tempfile
from pathlib import Path
from threading import Barrier, Thread

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _root in (_REPO_ROOT, _REPO_ROOT / "tools"):
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from expects import be_empty, equal, expect, have_keys, raise_error
from mamba import after, before, context, description, it

from tools.chat.chat import Chat, ChatNotConnectedError
from harness.installation.destination import data_of

CHAT = "ad6c04ab-chat"
CLOCK = [1000.0]
CONCURRENT_CHECK_INS = 200
MANY_COMMANDS = 40


def _said(commands: list) -> list[tuple[str, str]]:
    return [(command.kind, command.text) for command in commands]


def _states() -> list[str]:
    return [message.state for message in Chat.load(CHAT).messages()]


def _check_in_repeatedly(name: str, failures: list[Exception]) -> None:
    try:
        for _ in range(CONCURRENT_CHECK_INS):
            Chat.load(CHAT).check_in(is_busy=True, name=name)
    except Exception as failure:
        failures.append(failure)


def _titled(title: str) -> str:
    return json.dumps({"type": "custom-title", "customTitle": title, "sessionId": CHAT})


with description("a chat") as self:
    with before.each:
        self.chats = Path(tempfile.mkdtemp(prefix="cdd-chats-"))
        self.claude_config = Path(tempfile.mkdtemp(prefix="claude-config-"))
        self.projects = self.claude_config / "projects"
        self.projects.mkdir()
        os.environ["CDD_CHATS_FOLDER"] = str(self.chats)
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.claude_config)
        CLOCK[0] = 1000.0
        Chat.clock = staticmethod(lambda: CLOCK[0])

    with after.each:
        os.environ.pop("CDD_CHATS_FOLDER", None)
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    with context("with no chat checked in"):
        with it("should list no chats"):
            expect(Chat.list()).to(be_empty)

        with it("should refuse a command for a chat that is not connected"):
            expect(lambda: Chat.load(CHAT).send("command", "/actions-validate")).to(raise_error(ChatNotConnectedError))

    # Two check-ins written over each other left state files that no longer read, beside chats still checking in.
    with context("with a state file that does not read beside a chat that has checked in"):
        with before.each:
            Chat.load(CHAT).check_in(is_busy=False, name="repo · first words")
            damaged = self.chats / "damaged-chat"
            damaged.mkdir()
            (damaged / "chat.json").write_text('{"name": "old", "seen": 1000.0}}', encoding="utf-8")

        with it("should list the chat that reads"):
            expect([chat.id for chat in Chat.list()]).to(equal([CHAT]))

        with context("that has checked in again"):
            with before.each:
                Chat.load("damaged-chat").check_in(is_busy=False, name="repo · second words")

            with it("should list the chat again"):
                expect([chat.id for chat in Chat.list()]).to(equal([CHAT, "damaged-chat"]))

    # (S) Chat --> Check In With Board
    with context("that has checked in"):
        with before.each:
            Chat.load(CHAT).check_in(is_busy=True, name="repo · first words")

        with it("should be listed by its id"):
            expect([chat.id for chat in Chat.list()]).to(equal([CHAT]))

        with it("should say a turn is running"):
            expect(Chat.list()[0].is_busy).to(equal(True))

        with it("should go by the name its mod sent while the app has given it no title"):
            expect(Chat.list()[0].name).to(equal("repo · first words"))

        with it("should name no folder while its mod has sent none"):
            expect(Chat.list()[0].folder).to(equal(""))

        # The board finds a ticket's chat by the worktree the chat works in.
        with context("from the folder it works in"):
            with before.each:
                Chat.load(CHAT).check_in(is_busy=False, name="repo · first words", folder="C:/dev/repo-checkout-flow")

            with it("should name that folder"):
                expect(Chat.list()[0].folder).to(equal("C:/dev/repo-checkout-flow"))

        with context("with a title the app wrote into its transcript, read at a later check-in"):
            with before.each:
                folder = self.projects / "C--dev-repo"
                folder.mkdir()
                (folder / f"{CHAT}.jsonl").write_text("\n".join([_titled("Board review"), '{"type":"user"}', _titled("Session board handoff review")]) + "\n", encoding="utf-8")
                CLOCK[0] += 31
                Chat.load(CHAT).check_in(is_busy=False, name="repo · first words")

            with it("should go by the latest title"):
                expect(Chat.list()[0].name).to(equal("Session board handoff review"))

        # A mod that reloads can check in twice at once, and a state file written over itself cannot be read.
        with context("that checks in from two places at once"):
            with before.each:
                self.failures = []
                names = ("repo · first words", "repo · a much longer name than the first one")
                checking_in = [Thread(target=_check_in_repeatedly, args=(name, self.failures)) for name in names]
                for thread in checking_in:
                    thread.start()
                for thread in checking_in:
                    thread.join()

            with it("should take every check-in"):
                expect(self.failures).to(be_empty)

            with it("should still be listed"):
                expect([chat.id for chat in Chat.list()]).to(equal([CHAT]))

        with context("that has gone quiet"):
            with before.each:
                CLOCK[0] += 6

            with it("should not be listed"):
                expect(Chat.list()).to(be_empty)

        # (S) Person --> Send Command To Chat
        with context("that has been sent a command"):
            with before.each:
                Chat.load(CHAT).send("command", "/actions-validate stories-story-map")

            with it("should get the command at its next check-in"):
                expect(_said(Chat.load(CHAT).check_in(is_busy=True))).to(equal([("command", "/actions-validate stories-story-map")]))

            with it("should get it only once"):
                Chat.load(CHAT).check_in(is_busy=True)
                expect(Chat.load(CHAT).check_in(is_busy=True)).to(be_empty)

            # A mod that reloads checks in twice at once, and one cdd server answers both.
            with context("among many, at two check-ins at once"):
                with before.each:
                    for number in range(MANY_COMMANDS):
                        Chat.load(CHAT).send("command", f"/actions-validate {number}")
                    self.failures, self.taken = [], []
                    together = Barrier(2)

                    def check_in() -> None:
                        together.wait(timeout=5)
                        try:
                            self.taken.extend(Chat.load(CHAT).check_in(is_busy=True))
                        except Exception as failure:
                            self.failures.append(failure)

                    both = [Thread(target=check_in) for _ in range(2)]
                    for thread in both:
                        thread.start()
                    for thread in both:
                        thread.join()

                with it("should take both check-ins"):
                    expect(self.failures).to(be_empty)

                with it("should hand each command to only one of them"):
                    expect(len(self.taken)).to(equal(MANY_COMMANDS + 1))

            # (S) Person --> View Chat Messages
            with it("should show the command waiting among its messages"):
                expect(data_of(Chat.load(CHAT).messages()[0])).to(have_keys({"kind": "command", "text": "/actions-validate stories-story-map", "sent_at": 1000.0, "state": "waiting", "reason": ""}))

            # (S) Person --> Remove Chat Message
            with context("that a person has removed"):
                with before.each:
                    Chat.load(CHAT).remove(Chat.load(CHAT).messages()[0].message)

                with it("should no longer show it"):
                    expect(Chat.load(CHAT).messages()).to(be_empty)

                with it("should give the chat nothing at its next check-in"):
                    expect(Chat.load(CHAT).check_in(is_busy=True)).to(be_empty)

            with context("that the chat has taken"):
                with before.each:
                    self.taken = Chat.load(CHAT).check_in(is_busy=True)[0]

                with it("should show the command as taken, not yet shown"):
                    expect(_states()).to(equal(["taken"]))

                with context("that the chat has shown"):
                    with before.each:
                        Chat.load(CHAT).confirm(self.taken.message, is_shown=True)

                    with it("should show the command as shown in the chat"):
                        expect(_states()).to(equal(["shown"]))

                    # (S) Chat --> Finish Chat Command
                    with context("that has finished running"):
                        with before.each:
                            Chat.load(CHAT).finish(self.taken.message)

                        with it("should show the command as done"):
                            expect(_states()).to(equal(["done"]))

                    # A mod that reloads mid-turn forgets the commands it was running, so the chat's own check-ins finish them.
                    with context("that the chat has worked on through a turn"):
                        with before.each:
                            Chat.load(CHAT).check_in(is_busy=True)

                        with context("that has ended"):
                            with before.each:
                                Chat.load(CHAT).check_in(is_busy=False)

                            with it("should show the command as done"):
                                expect(_states()).to(equal(["done"]))

                    with context("that the chat has not yet started a turn for"):
                        with before.each:
                            Chat.load(CHAT).check_in(is_busy=False)

                        with it("should still show the command as shown"):
                            expect(_states()).to(equal(["shown"]))

                with context("that the chat could not show"):
                    with before.each:
                        Chat.load(CHAT).confirm(self.taken.message, is_shown=False, reason="a Stop stands")

                    with it("should show the command as failed"):
                        expect(_states()).to(equal(["failed"]))

                    with it("should say why"):
                        expect(Chat.load(CHAT).messages()[0].reason).to(equal("a Stop stands"))

                    # (S) Person --> Resend Chat Message
                    with context("that a person has resent"):
                        with before.each:
                            Chat.load(CHAT).resend(self.taken.message)

                        with it("should show the command waiting again"):
                            expect(_states()).to(equal(["waiting"]))

                        with it("should let go of why it failed"):
                            expect(Chat.load(CHAT).messages()[0].reason).to(equal(""))

                        with it("should give the command to the chat at its next check-in"):
                            expect(_said(Chat.load(CHAT).check_in(is_busy=True))).to(equal([("command", "/actions-validate stories-story-map")]))

            with context("that is followed by more messages than the chat keeps"):
                with before.each:
                    for number in range(30):
                        Chat.load(CHAT).send("submit", f"message {number}")
                    Chat.load(CHAT).check_in(is_busy=False)

                with it("should keep only the latest, newest first"):
                    expect([message.text for message in Chat.load(CHAT).messages()][:2]).to(equal(["message 29", "message 28"]))

                with it("should keep no more than it shows"):
                    expect(len(Chat.load(CHAT).messages())).to(equal(20))

        with context("that has been sent a fill during a turn"):
            with before.each:
                Chat.load(CHAT).send("fill", "Write a handoff")

            with it("should hold the fill while the turn runs"):
                expect(Chat.load(CHAT).check_in(is_busy=True)).to(be_empty)

            with it("should hand the fill over once the turn has ended"):
                expect(_said(Chat.load(CHAT).check_in(is_busy=False))).to(equal([("fill", "Write a handoff")]))
