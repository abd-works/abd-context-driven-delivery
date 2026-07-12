"""BDD spec for agent_bdd manifest and runbook extraction."""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import context, description, it

from agent_bdd import agent
from agent_bdd.agent_bdd_common import (
    build_runbook,
    cli_output_matches_prompt,
    read_manifest,
    yaml_from_prompt,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TOOLS_SPEC = _REPO_ROOT / "tools" / "tools_agent_spec.py"


with description("an agent spec file"):
    with context("with @agent-spec-manifest header"):
        with it("should declare in_chat harness and session path"):
            manifest = read_manifest(_TOOLS_SPEC)
            expect(manifest.in_chat).to(be_true)
            expect(manifest.session).to(equal("tools/.sessions/general-lee.json"))
            expect("agent-spec" in manifest.command).to(be_true)

        with it("should build a runbook with instruct steps and judge rubric"):
            runbook = build_runbook(_TOOLS_SPEC)
            expect(runbook.harness).to(equal("in_chat"))
            expect(len(runbook.scenarios) > 0).to(be_true)
            scenario = runbook.scenarios[0]
            kinds = [step.kind for step in scenario.setup]
            expect("instruct" in kinds).to(be_true)
            expect("instruct_use_tool" in kinds).to(be_true)
            expect(len(scenario.judges) > 0).to(be_true)
            expect("rebellious" in scenario.judges[0].rubric.lower()).to(be_true)

        with it("should extract f-string instruct_use_tool prompts with module constants"):
            runbook = build_runbook(_REPO_ROOT / "agents" / "agents_agent_spec.py")
            setup = runbook.scenarios[0].setup
            expect(len(setup)).to(equal(4))
            travel_step = setup[2]
            expect(travel_step.kind).to(equal("instruct_use_tool"))
            expect("travelTo" in (travel_step.prompt or "")).to(be_true)
            expect(travel_step.save_as).to(equal("self.travel_response"))

        with it("should build a generator runbook with generate and repair steps"):
            manifest = read_manifest(_REPO_ROOT / "generator" / "generator_agent_spec.py")
            expect(manifest.in_chat).to(be_true)
            expect(manifest.session).to(equal("generator/.sessions/car-chronicle.json"))
            runbook = build_runbook(_REPO_ROOT / "generator" / "generator_agent_spec.py")
            setup = [step for scenario in runbook.scenarios for step in scenario.setup]
            prompts = " ".join(step.prompt or "" for step in setup)
            expect("CarChronicle" in prompts).to(be_true)
            expect("action: repair" in prompts).to(be_true)
            assertions = " ".join(
                item.expression for scenario in runbook.scenarios for item in scenario.assertions
            )
            expect("self.repair_response" in assertions).to(be_true)
            expect("self.generate_response" in assertions).to(be_true)
            judges = [judge for scenario in runbook.scenarios for judge in scenario.judges]
            expect(len(judges)).to(equal(1))

    with context("with agent context manager"):
        with it("should enter and exit via __enter__ for in-chat harness"):
            session_file = _REPO_ROOT / "agent_bdd" / ".sessions" / "context-manager-spec.json"
            cm = agent(_REPO_ROOT, session_file, in_chat=True)
            block = cm.__enter__()
            try:
                expect(hasattr(block, "instruct")).to(be_true)
                expect(hasattr(block, "instruct_use_tool")).to(be_true)
            finally:
                cm.__exit__(None, None, None)

        with it("should strip prose after embedded stdin YAML in instruct_use_tool prompts"):
            prompt = (
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                "toolset: generator.examples.car_chronicle.car_chronicle:CarChronicle\n"
                "action: repair\n"
                "Return the complete fenced YAML stdout from the CLI.\n"
                "\nIMPORTANT: Invoke python -m tools run via shell."
            )
            body = yaml_from_prompt(prompt)
            expect(body).to(equal("toolset: generator.examples.car_chronicle.car_chronicle:CarChronicle\naction: repair"))

        with it("should reject captured CLI output when action does not match prompt YAML"):
            prompt = (
                "Pipe this YAML on stdin:\n"
                "toolset: generator.examples.car_chronicle.car_chronicle:CarChronicle\n"
                "action: repair\n"
            )
            wrong = "```yaml\nok: true\naction: generate\ninstructions: test\n```"
            expect(cli_output_matches_prompt(wrong, prompt)).to(equal(False))
            right = "```yaml\nok: true\naction: repair\ninstructions: test\n```"
            expect(cli_output_matches_prompt(right, prompt)).to(be_true)
