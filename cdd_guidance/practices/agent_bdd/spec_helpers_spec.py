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

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.agent_bdd.spec_helpers import (
    generate_similar_prompt,
    generate_similar_rubric,
    repo_root_from,
    sessions_dir,
)


with description("spec_helpers"):
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
