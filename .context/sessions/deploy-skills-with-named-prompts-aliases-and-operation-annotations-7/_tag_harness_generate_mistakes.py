"""Tag introducing/fix commits with git notes for Harness generate mistakes."""
from __future__ import annotations

import uuid
from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "deploy-skills-with-named-prompts-aliases-and-operation-annotations-7"
PATH = "primitives/harness"
WORKSPACE = r"c:\dev\abd-context-driven-delivery"
INTRODUCING = "d739a33d5e958f1972e6d5401f065da1a11442d9"
FIX = "0069d09a405628cc803638b4b50e191a02dc9b4f"
ARTIFACT = "primitives/harness/harness.py"

ORIGINAL = """\
_COMPANIONS = ("echo", "handoff", "backlog", "start", "finish")
_HOST_ACTIONS = (
    "partition",
    "grill",
    "sketch",
    "generate",
    ...
    @agent_tool
    def walk(self, name_filter: str = "") -> str:
    ...
    @agent_tool
    def write_deploy(self, source: str = "", name_filter: str = "") -> str:
    ...
        self.walk()
        self.write_deploy()
"""

WRONG = (
    "Harness generate listed walk and write_deploy as two @agent_tool calls "
    "(two model round-trips for one deploy) and shipped hardcoded catalogs for "
    "host actions, CDD stages, tool fidelities, and companions/backlog instead "
    "of iterating walked sources. Only formats should be hardcoded."
)


def _bdd() -> Bdd:
    return Bdd(
        fidelity="engineering",
        path=PATH,
        session=SESSION,
        workspace=WORKSPACE,
    )


def main() -> None:
    improved = Path(WORKSPACE, ARTIFACT).read_text(encoding="utf-8")
    bdd = _bdd()
    session = bdd.workspace.open(bdd)
    turn = bdd.turn.open(bdd, action="mistake")
    entry_id = uuid.uuid4().hex[:8]
    turn.record_mistake(
        entry_id=entry_id,
        artifact=ARTIFACT,
        rule="reuse-existing-not-invent-parallel",
        wrong=WRONG,
        original=ORIGINAL,
        tool="bdd",
        fidelity="engineering",
        introducing_commit=INTRODUCING,
    )
    session.open_turn = None
    session.save()

    bdd = _bdd()
    session = bdd.workspace.open(bdd)
    turn = bdd.turn.open(bdd, action="correction")
    turn.record_correction(
        entry_ids=[entry_id],
        improved=improved,
        how=(
            "write_deploy walks internally so generate has one agent tool. "
            "Fidelities come from each walked context tool; action prompts come "
            "from walked packages and their @agent_instructions. Catalogs for "
            "host actions, stages, fidelities, and companions are gone. "
            "a1e71ca merged the tools; 0069d09 is the completing fix."
        ),
        status="fixed",
    )
    if turn.correction is None:
        raise RuntimeError("record_correction did not attach a correction")
    turn.correction.link(session.git, FIX)
    session.open_turn = None
    session.save()
    print(f"entry_id={entry_id}")
    print(f"introducing={INTRODUCING}")
    print(f"fix={FIX}")


if __name__ == "__main__":
    main()
