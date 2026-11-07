"""Unit spec for agent_bdd.spec_helpers — no live agent."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, raise_error
from mamba import after, before, context, description, it
from space.session.throwaway_project import ThrowawayProject

from cdd_guidance.practices.agent_bdd.spec_helpers import (
    CAR,
    CAR_START,

    ensure_invoke_staged,
    generate_similar_prompt,
    generate_similar_rubric,
    invoke_request_for_path,
    invoke_toolset,
    repo_root_from,
    sessions_dir,
)


with description("spec_helpers"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        self.project = ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("a toolset run built from its arguments"):
        with it("should reject missing tool and action"):
            expect(lambda: invoke_toolset(project=self.project.root, toolset="pkg:Tool")).to(raise_error(ValueError))

        with it("should reject both tool and action"):
            expect(
                lambda: invoke_toolset(project=self.project.root, toolset="pkg:Tool", tool="scan", action="generate")
            ).to(raise_error(ValueError))

    with context("invoke_toolset"):
        with it("should invoke car-start in-process"):
            root = repo_root_from(__file__, parents=3)
            ensure_invoke_staged(root)
            request = invoke_request_for_path(CAR_START, repo_root=root)
            response = invoke_toolset(
                project=self.project.root,
                toolset=request["toolset"],
                tool=request["tool"],
                context=request.get("context"),
            )
            expect(response.ok).to(equal(True))
            expect(response.tool).to(equal("start"))
            expect(response.toolset).to(equal(CAR))

    with context("path helpers"):
        with it("should resolve sessions beside the spec file"):
            fake = Path(__file__).resolve()
            expect(sessions_dir(fake)).to(
                equal(fake.parent / ".context" / ".agent_bdd_sessions")
            )

        with it("should resolve repo root from this package"):
            root = repo_root_from(__file__, parents=3)
            expect((root / "cdd_guidance" / "practices" / "agent_bdd").is_dir()).to(equal(True))

    with context("a pass fixture handed to generate"):
        with it("should ask the agent to generate something similar"):
            prompt = generate_similar_prompt(Path("repairedAsset.md"))
            expect("similar" in prompt.lower()).to(equal(True))
            expect("repairedAsset.md" in prompt.replace("\\", "/")).to(equal(True))

        with it("should judge the generate against that pass file"):
            rubric = generate_similar_rubric(Path("repairedAsset.md"))
            expect("repairedAsset.md" in rubric.replace("\\", "/")).to(equal(True))
            expect("similar" in rubric.lower()).to(equal(True))
