"""Heavy spec: several real processes change one session's session.json at the same moment, as two chats' cdd servers,
a render and the board do to one ticket's record."""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.json_file import JsonFileUnreadable
from space.session import Sessions

SESSION = "refund-order"
PROCESSES = 4
CHANGES_EACH = 12
# Seconds the processes are given to start, so every one makes its first change at the same moment.
START_TOGETHER_SECONDS = 3.0
# Seconds an update is given once the process that held the record is gone; the hold's own wait is 30.
PROMPT_SECONDS = 5.0

# One process: it waits for the shared moment, then records a test tier for each of its own modules in the one session,
# and prints the changes that were refused.
WRITER = """
import json, sys, time
from pathlib import Path
from space.session import Sessions
project, place, count, start = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
session = Sessions(project).named("refund-order")
while time.time() < start:
    pass
refused = []
for number in range(count):
    try:
        session.test_tiers.record(f"module-{place}-{number}", {"unit": "mamba"})
    except Exception as error:
        refused.append(f"{type(error).__name__}: {error}")
print(json.dumps({"refused": refused}))
"""

# One process that takes hold of the session's session.json for a change, says so, and never lets go.
HOLDER = """
import sys, time
from pathlib import Path
from space.session import Sessions
session = Sessions(Path(sys.argv[1])).named("refund-order")
with session.record.held():
    print("held", flush=True)
    time.sleep(600)
"""


def project_with_session() -> Path:
    """A plain folder holding the session refund-order, titled, with no test tier recorded."""
    project = Path(tempfile.mkdtemp(prefix="record-processes-"))
    folder = project / ".sessions" / SESSION
    folder.mkdir(parents=True)
    (folder / "session.json").write_text(json.dumps({"name": SESSION, "title": "Refund an order"}), encoding="utf-8")
    return project


def writers(project: Path) -> list[dict]:
    """Run PROCESSES processes, all starting their changes together; answers what each printed."""
    start = time.time() + START_TOGETHER_SECONDS
    started = [
        subprocess.Popen([sys.executable, "-c", WRITER, str(project), str(place), str(CHANGES_EACH), str(start)], cwd=_REPO_ROOT, stdout=subprocess.PIPE, text=True)
        for place in range(PROCESSES)
    ]
    return [json.loads(process.communicate()[0].strip().splitlines()[-1]) for process in started]


# (S:system) Session --> Keep Every Change To Session Record
with description("a session's session.json changed by several processes at once") as self:
    with context("that four processes each record twelve modules' test tiers in, all at the same moment"):
        with before.all:
            self.project = project_with_session()
            self.answers = writers(self.project)
            self.held = json.loads((self.project / ".sessions" / SESSION / "session.json").read_text(encoding="utf-8"))

        with it("should refuse no change"):
            expect([refusal for answer in self.answers for refusal in answer["refused"]]).to(equal([]))

        with it("should keep every module each process recorded"):
            expected = sorted(f"module-{place}-{number}" for place in range(PROCESSES) for number in range(CHANGES_EACH))
            expect(sorted(self.held.get("test_tiers", {}))).to(equal(expected))

        with it("should keep the fields the file held before"):
            expect(self.held["title"]).to(equal("Refund an order"))

    with context("that a process holding it for a change is killed, partway through its change"):
        with before.all:
            self.project = project_with_session()
            self.file = self.project / ".sessions" / SESSION / "session.json"
            self.before = self.file.read_text(encoding="utf-8")
            self.holder = subprocess.Popen([sys.executable, "-c", HOLDER, str(self.project)], cwd=_REPO_ROOT, stdout=subprocess.PIPE, text=True)
            self.holder.stdout.readline()
            self.left_as_it_was = self.file.read_text(encoding="utf-8") == self.before
            self.holder.kill()
            self.holder.wait()
            started = time.monotonic()
            Sessions(self.project).named(SESSION).test_tiers.record("space/kanban", {"unit": "mamba"})
            self.seconds = time.monotonic() - started

        with it("should hold what it held before the change, since the change wrote nothing"):
            expect(self.left_as_it_was).to(equal(True))

        with it("should take the next change at once, not after the hold's whole wait"):
            expect(self.seconds < PROMPT_SECONDS).to(equal(True))

        with it("should keep that next change"):
            expect(json.loads(self.file.read_text(encoding="utf-8"))["test_tiers"]).to(equal({"space/kanban": {"unit": "mamba"}}))

    with context("that a writer killed partway left half written"):
        with before.each:
            self.project = project_with_session()
            self.file = self.project / ".sessions" / SESSION / "session.json"
            self.half = '{"name": "refund-order", "title": "Refund an or'
            self.file.write_text(self.half, encoding="utf-8")
            self.change = lambda: Sessions(self.project).named(SESSION).test_tiers.record("space/kanban", {"unit": "mamba"})

        with it("should refuse the next change, naming the file"):
            expect(self.change).to(raise_error(JsonFileUnreadable, contain("session.json")))

        with it("should leave the file as it is for a person to repair, never written over as if it were empty"):
            try:
                self.change()
            except JsonFileUnreadable:
                pass
            expect(self.file.read_text(encoding="utf-8")).to(equal(self.half))
