"""Attach a PracticeGuidance instance to a Workspace — not a host composer."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance


def attach_practice_workspace(
    practice: PracticeGuidance,
    *,
    path: str | None = None,
    session: str | None = None,
    workspace: str | None = None,
) -> None:
    from tools.workspace.workspace import Workspace

    if path is not None:
        practice.path = path
    if session is not None:
        practice.session = session
    root = workspace or practice.path or "."
    practice.workspace = Workspace(str(root))
    practice.workspace.load()
    if practice.session:
        practice.workspace.open(
            practice,
            name=practice.session,
            path=practice.path or "",
        )


def apply_fidelity_stages(
    practice: PracticeGuidance,
    stage_to_fidelity: dict[str, str],
) -> None:
    from harness.guidance.guidance import FidelityGuidance

    fidelity_to_stage = {fidelity: stage for stage, fidelity in stage_to_fidelity.items()}
    for name, child in practice.fidelities.entries.items():
        if isinstance(child, FidelityGuidance):
            child.stage = fidelity_to_stage.get(name, "")


def init_practice_guidance(
    practice: PracticeGuidance,
    *,
    format: str | None = None,
    path: str | None = None,
    session: str | None = None,
    workspace: str | None = None,
    fidelity: str | None = None,
    stage_to_fidelity: dict[str, str] | None = None,
) -> None:
    from harness.guidance.guidance import PracticeGuidance

    PracticeGuidance.__init__(
        practice,
        format=format,
        path=path,
        session=session or "",
    )
    attach_practice_workspace(
        practice,
        path=path,
        session=session,
        workspace=workspace,
    )
    if fidelity is not None:
        practice.fidelity = fidelity
    practice.load_fidelities_from_markdown()
    if stage_to_fidelity:
        apply_fidelity_stages(practice, stage_to_fidelity)
