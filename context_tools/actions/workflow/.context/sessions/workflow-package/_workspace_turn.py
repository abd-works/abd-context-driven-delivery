"""Workspace turn logging — WorkSession + Turn, not EvalSession."""
from __future__ import annotations

import uuid

from context_tools.bdd.bdd import Bdd


def record_mistake_turn(
    *,
    path: str,
    session_name: str,
    artifact: str,
    rule: str,
    wrong: str,
    original: str,
    prompt: str,
    introducing_commit: str,
    fidelity: str = "behavior",
) -> tuple[str, str | None]:
    bdd = Bdd(fidelity=fidelity, path=path, session=session_name)
    session = bdd.workspace.open(bdd)
    turn = bdd.turn.open(bdd, action="mistake")
    entry_id = uuid.uuid4().hex[:8]
    turn.record_mistake(
        entry_id=entry_id,
        artifact=artifact.replace("\\", "/"),
        rule=rule,
        wrong=wrong,
        original=original,
        tool="bdd",
        fidelity=fidelity,
        introducing_commit=introducing_commit,
    )
    commit = turn.finish(
        prompt=prompt,
        result=f"entry_id={entry_id} introducing={introducing_commit}",
        context=session_name,
    )
    _ = session  # open + trail binding
    return entry_id, commit.sha if commit else None


def record_correction_turn(
    *,
    path: str,
    session_name: str,
    entry_id: str,
    improved: str,
    how: str,
    prompt: str,
    status: str = "fixed",
    fidelity: str = "behavior",
) -> str | None:
    bdd = Bdd(fidelity=fidelity, path=path, session=session_name)
    session = bdd.workspace.open(bdd)
    turn = bdd.turn.open(bdd, action="correction")
    turn.record_correction(
        entry_ids=[entry_id],
        improved=improved,
        how=how,
        status=status,
    )
    commit = turn.finish(
        prompt=prompt,
        result=f"entry_id={entry_id} fixed",
        context=session_name,
    )
    _ = session
    return commit.sha if commit else None
