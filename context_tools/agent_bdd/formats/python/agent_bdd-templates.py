# =============================================================================
# Agent BDD Template — mamba spec driving an agent through the agent() harness
# =============================================================================
# Fill placeholders (delete this block before committing):
#
#   {ToolsetPath}     e.g. context_tools.base.examples.car_chronicle.car_chronicle:CarChronicle
#   {ActionName}      generate | validate | satisfy | repair | <custom>
#   {SessionName}     stem for .agent_bdd_sessions/<name>.json
#   {Description}     top-level describe label (e.g. "a CarChronicle generator")
#   {ScenarioLabel}   context label (e.g. "with agent and generate action")
#   {SetupPrompt}     natural-language instruct to prime state
#   {ExpectedKeyword} substring the response.instructions must contain
#   {JudgeRubric}     one sentence describing PASS criteria
# =============================================================================

from pathlib import Path

from expects import be_true, equal, expect
from mamba import context, description, it

from agent_bdd import agent, ai_judge, instruct, instruct_use_tool

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SESSIONS = Path(__file__).resolve().parents[2] / ".agent_bdd_sessions"

_RUN_YAML = """\
toolset: {ToolsetPath}
action: {ActionName}
"""

with description("{Description}"):
    with context("{ScenarioLabel}"):
        with it("drives {ActionName} and asserts inline"):
            with agent(_REPO_ROOT, _SESSIONS / "{SessionName}.json"):
                instruct("{SetupPrompt}")

                response = instruct_use_tool(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_RUN_YAML}\n"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=180,
                )
                expect(response.ok).to(be_true)
                expect(response.action).to(equal("{ActionName}"))
                expect("{ExpectedKeyword}".lower() in str(response.instructions).lower()).to(be_true)

                ai_judge(str(response.instructions), "{JudgeRubric}")
