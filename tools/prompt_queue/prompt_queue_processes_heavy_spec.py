"""Heavy spec: several real processes change one chat's queue file at the same moment, as the stable lane's cdd server,
the dev lane's cdd server and each server's side-by-side calls do to one chat's queue."""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from tools.prompt_queue.prompt_queue import PromptQueue

CHAT = "chat-1"
QUEUED_BEFORE = 20
CALLS_EACH = 15
# Seconds the processes are given to start, so every one makes its first call at the same moment.
START_TOGETHER_SECONDS = 2.0
# How long a reading process keeps reading the queue, which covers the time the others take to make their changes.
READING_SECONDS = 1.0

# One process: it waits for the shared moment, then makes its calls on its own PromptQueue of the one file, a reader
# reading for READING_SECONDS, and prints the calls that were refused and each queue length it read.
CALLER = """
import json, sys, time
from pathlib import Path
from tools.prompt_queue.prompt_queue import PromptQueue
file, job, place, count, start = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
reading_seconds = float(sys.argv[6])
queue = PromptQueue("chat-1", file)
mine = [prompt["id"] for prompt in queue.prompts][place * count:(place + 1) * count]
while time.time() < start:
    pass
refused, lengths = [], set()
def call(number):
    try:
        if job == "add":
            queue.add(f"added-{place}-{number}")
        elif job == "done":
            queue.done(mine[number])
        else:
            lengths.add(len(queue.prompts))
    except Exception as error:
        refused.append(f"{type(error).__name__}: {error}")
if job == "read":
    while time.time() < start + reading_seconds:
        call(0)
else:
    for number in range(count):
        call(number)
print(json.dumps({"refused": refused, "lengths": sorted(lengths)}))
"""

# One process that takes hold of the queue's file for a change, says so, and never lets go.
HOLDER = """
import sys, time
from pathlib import Path
from harness.installation.json_file import JsonFile
with JsonFile(Path(sys.argv[1])).held():
    print("held", flush=True)
    time.sleep(600)
"""


def callers(file: Path, jobs: list[tuple[str, int]]) -> list[dict]:
    """Run one process for each job, all starting their calls together; answers what each printed."""
    start = time.time() + START_TOGETHER_SECONDS
    started = [
        subprocess.Popen([sys.executable, "-c", CALLER, str(file), job, str(place), str(CALLS_EACH), str(start), str(READING_SECONDS)], cwd=_REPO_ROOT, stdout=subprocess.PIPE, text=True)
        for job, place in jobs
    ]
    return [json.loads(process.communicate()[0].strip().splitlines()[-1]) for process in started]


# (S) Agent --> Queue Prompts Through The Cdd Server
with description("a chat's prompt queue changed by several processes at once") as self:
    with before.all:
        self.file = Path(tempfile.mkdtemp(prefix="queue-processes-")) / CHAT / "prompt-queue.json"
        PromptQueue(CHAT, self.file).add_all([f"queued-before-{number}" for number in range(QUEUED_BEFORE)])

    with context("that three processes add cards, one marks cards done and two read, all at the same moment"):
        with before.all:
            self.answers = callers(self.file, [("add", 0), ("add", 1), ("add", 2), ("done", 0), ("read", 0), ("read", 1)])
            self.held = PromptQueue(CHAT, self.file).prompts

        with it("should refuse no call"):
            expect([refusal for answer in self.answers for refusal in answer["refused"]]).to(equal([]))

        with it("should keep every card queued before, in order, at the front of the queue"):
            expect([prompt["text"] for prompt in self.held][:QUEUED_BEFORE]).to(equal([f"queued-before-{number}" for number in range(QUEUED_BEFORE)]))

        with it("should keep every card each process added"):
            added = sorted(prompt["text"] for prompt in self.held if prompt["text"].startswith("added-"))
            expect(added).to(equal(sorted(f"added-{place}-{number}" for place in range(3) for number in range(CALLS_EACH))))

        with it("should keep every card marked done as done"):
            expect([prompt.get("is_done", False) for prompt in self.held[:CALLS_EACH]]).to(equal([True] * CALLS_EACH))

        with it("should never show a reader fewer cards than were queued before"):
            expect([length for answer in self.answers for length in answer["lengths"] if length < QUEUED_BEFORE]).to(equal([]))

    with context("that a process holding the queue's file for a change is killed"):
        with before.all:
            self.holder = subprocess.Popen([sys.executable, "-c", HOLDER, str(self.file)], cwd=_REPO_ROOT, stdout=subprocess.PIPE, text=True)
            self.holder.stdout.readline()
            self.holder.kill()
            self.holder.wait()

        with it("should take the next change, since the hold ended with the process"):
            texts = [prompt["text"] for prompt in PromptQueue(CHAT, self.file).add("Run the heavy tier").prompts]
            expect(texts[-1]).to(equal("Run the heavy tier"))
