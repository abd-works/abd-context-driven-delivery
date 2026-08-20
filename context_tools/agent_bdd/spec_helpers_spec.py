"""Unit spec for agent_bdd.spec_helpers — no live agent."""
from pathlib import Path

from expects import equal, expect, raise_error
from mamba import context, description, it

from agent_bdd.spec_helpers import (
    dump_run_yaml,
    generate_similar_prompt,
    generate_similar_rubric,
    manifest_command_from_header,
    repo_root_from,
    sessions_dir,
    tools_run_prompt,
)


with description("spec_helpers"):
    with context("dump_run_yaml"):
        with it("should serialize an action request"):
            body = dump_run_yaml(
                toolset="pkg:Tool",
                action="generate",
                context={"format": "python"},
            )
            expect("toolset: pkg:Tool" in body).to(equal(True))
            expect("action: generate" in body).to(equal(True))
            expect("format: python" in body).to(equal(True))

        with it("should serialize a tool request with arguments"):
            body = dump_run_yaml(
                toolset="pkg:Tool",
                tool="scan",
                arguments={"paths": ["a.py"]},
            )
            expect("tool: scan" in body).to(equal(True))
            expect("paths" in body).to(equal(True))

        with it("should reject missing tool and action"):
            expect(lambda: dump_run_yaml(toolset="pkg:Tool")).to(raise_error(ValueError))

        with it("should reject both tool and action"):
            expect(
                lambda: dump_run_yaml(toolset="pkg:Tool", tool="scan", action="generate")
            ).to(raise_error(ValueError))

    with context("tools_run_prompt"):
        with it("should wrap YAML for stdin tools run"):
            prompt = tools_run_prompt("toolset: X\naction: generate\n")
            expect("python -m tools run -" in prompt).to(equal(True))
            expect("action: generate" in prompt).to(equal(True))
            expect("fenced YAML" in prompt).to(equal(True))

    with context("path helpers"):
        with it("should resolve sessions beside the spec file"):
            fake = Path(__file__).resolve()
            expect(sessions_dir(fake)).to(
                equal(fake.parent / ".context" / ".agent_bdd_sessions")
            )

        with it("should resolve repo root from this package"):
            root = repo_root_from(__file__, parents=2)
            expect((root / "context_tools" / "agent_bdd").is_dir()).to(equal(True))

    with context("manifest_command_from_header"):
        with it("should read the exact @toolset-manifest command from Bdd"):
            root = repo_root_from(__file__, parents=2)
            command = manifest_command_from_header(root / "context_tools" / "bdd" / "bdd.py")
            expect(command).to(
                equal("python -m tools manifest context_tools.bdd.bdd:Bdd")
            )

    with context("a pass fixture handed to generate"):
        with it("should ask the agent to generate something similar"):
            prompt = generate_similar_prompt(Path("repairedAsset.md"))
            expect("similar" in prompt.lower()).to(equal(True))
            expect("repairedAsset.md" in prompt.replace("\\", "/")).to(equal(True))

        with it("should judge the generate against that pass file"):
            rubric = generate_similar_rubric(Path("repairedAsset.md"))
            expect("repairedAsset.md" in rubric.replace("\\", "/")).to(equal(True))
            expect("similar" in rubric.lower()).to(equal(True))
