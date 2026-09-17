"""Unit spec for agent_bdd.spec_helpers — no live agent."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, raise_error
from mamba import context, description, it

from agent_bdd.spec_helpers import (
    CAR,
    CAR_START,
    build_run_request,
    ensure_invoke_staged,
    generate_similar_prompt,
    generate_similar_rubric,
    invoke_request_for_path,
    invoke_toolset,
    repo_root_from,
    sessions_dir,
)


with description("spec_helpers"):
    with context("build_run_request"):
        with it("should serialize an action request"):
            payload = build_run_request(
                toolset="pkg:Tool",
                action="generate",
                context={"format": "python"},
            )
            expect(payload["toolset"]).to(equal("pkg:Tool"))
            expect(payload["action"]).to(equal("generate"))
            expect(payload["context"]["format"]).to(equal("python"))

        with it("should serialize a tool request with arguments"):
            payload = build_run_request(
                toolset="pkg:Tool",
                tool="scan",
                arguments={"paths": ["a.py"]},
            )
            expect(payload["tool"]).to(equal("scan"))
            expect(payload["arguments"]["paths"]).to(equal(["a.py"]))

        with it("should reject missing tool and action"):
            expect(lambda: build_run_request(toolset="pkg:Tool")).to(raise_error(ValueError))

        with it("should reject both tool and action"):
            expect(
                lambda: build_run_request(toolset="pkg:Tool", tool="scan", action="generate")
            ).to(raise_error(ValueError))

    with context("invoke_toolset"):
        with it("should invoke car-start in-process"):
            root = repo_root_from(__file__, parents=2)
            ensure_invoke_staged(root)
            request = invoke_request_for_path(CAR_START, repo_root=root)
            response = invoke_toolset(
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
            root = repo_root_from(__file__, parents=2)
            expect((root / "practices" / "agent_bdd").is_dir()).to(equal(True))

    with context("a pass fixture handed to generate"):
        with it("should ask the agent to generate something similar"):
            prompt = generate_similar_prompt(Path("repairedAsset.md"))
            expect("similar" in prompt.lower()).to(equal(True))
            expect("repairedAsset.md" in prompt.replace("\\", "/")).to(equal(True))

        with it("should judge the generate against that pass file"):
            rubric = generate_similar_rubric(Path("repairedAsset.md"))
            expect("repairedAsset.md" in rubric.replace("\\", "/")).to(equal(True))
            expect("similar" in rubric.lower()).to(equal(True))
