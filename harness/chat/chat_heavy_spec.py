"""A chat checked in from two places at once: threads racing on the chat's folder on purpose. Heavy: hundreds of real
check-ins on disk, from two threads."""
import os
import sys
import tempfile
from pathlib import Path
from threading import Barrier, Thread

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _root in (_REPO_ROOT, _REPO_ROOT / "tools"):
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from expects import be_empty, equal, expect
from mamba import after, before, context, description, it

from harness.chat.chat import Chat

CHAT = "ad6c04ab-chat"
CLOCK = [1000.0]
CONCURRENT_CHECK_INS = 200
MANY_COMMANDS = 40


def _check_in_repeatedly(name: str, failures: list[Exception]) -> None:
    try:
        for _ in range(CONCURRENT_CHECK_INS):
            Chat.load(CHAT).check_in(is_busy=True, name=name)
    except Exception as failure:
        failures.append(failure)


with description("a chat") as self:
    with before.each:
        self.chats = Path(tempfile.mkdtemp(prefix="cdd-chats-"))
        self.claude_config = Path(tempfile.mkdtemp(prefix="claude-config-"))
        (self.claude_config / "projects").mkdir()
        os.environ["CDD_CHATS_FOLDER"] = str(self.chats)
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.claude_config)
        CLOCK[0] = 1000.0
        Chat.clock = staticmethod(lambda: CLOCK[0])

    with after.each:
        os.environ.pop("CDD_CHATS_FOLDER", None)
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    with context("that has checked in"):
        with before.each:
            Chat.load(CHAT).check_in(is_busy=True, name="repo · first words")

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

        with context("that has been sent a command"):
            with before.each:
                Chat.load(CHAT).send("command", "/actions-validate stories-story-map")

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
