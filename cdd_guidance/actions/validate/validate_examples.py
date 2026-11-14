"""Spec support: the sample working copy every graph practice reads, and the sessions a validate checks it in."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from cdd_guidance.actions.validate.validate import Validate
from harness.agent_tools.tool_call import ToolCall
from space.session import Session, Sessions
from space.session.throwaway_project import ThrowawayProject

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO_ROOT / "harness" / "graph" / "_examples" / "input"
_STORY_FOLDER = "tests/onboard-a-customer/authenticate-user"
ENTITY_ROOT_FILE = "src/account-credentials/account-credentials.ts"
STORY_FILE = f"{_STORY_FOLDER}/authenticate_user.story.shared.ts"
SPEC_FILE = f"{_STORY_FOLDER}/authenticate_user.story.server.spec.ts"


def working_in(throwaway: ThrowawayProject, project: Path, root: Path) -> Session:
    """The main session of the spec's own project, where its logs and reports go, made to work in root, a folder of the
    project checked out at project."""
    kept_in = ToolCall(project=throwaway.root).session.session_path
    session = Sessions(Path(project).resolve()).load(kept_in)
    session.workpath = Path(root).resolve()
    return session


class SampleWorkingCopy:
    """A copy of the sample in a folder of its own, so it is a project of its own as a checked-out one is, and the
    validate that checks it in the throwaway project's session."""

    def __init__(self, throwaway: ThrowawayProject) -> None:
        folder = Path(tempfile.mkdtemp()) / "input"
        shutil.copytree(_SAMPLE, folder)
        self.action = Validate(session=working_in(throwaway, folder, folder))
        self.session = Path(self.action.session.session_path)
