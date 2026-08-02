# =============================================================================
# Agent BDD Template - mamba spec driving an agent through the agent() harness
# =============================================================================
# Fill placeholders (delete this block before committing):
#
#   {ToolsetPath}     e.g. context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle
#   {ActionName}      generate | validate | satisfy | repair | <custom>
#   {SessionName}     stem for .agent_bdd_sessions/<name>.json
#   {Description}     top-level describe label (e.g. "a CarChronicle generator")
#   {ScenarioLabel}   context label (e.g. "with agent and generate action")
#   {SetupPath}       workspace-relative path the agent should read first
#   {ExpectedKeyword} substring the response.instructions must contain
#   {JudgeRubric}     one sentence describing PASS criteria
# =============================================================================

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_instructions_contain,
    expect_ok_action,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=4)
_SESSIONS = sessions_dir(__file__)

with description("{Description}"):
    with context("{ScenarioLabel}"):
        with it("drives {ActionName} and asserts inline"):
            with agent(_REPO_ROOT, _SESSIONS / "{SessionName}.json"):
                read_workspace("{SetupPath}")

                response = run_toolset(
                    toolset="{ToolsetPath}",
                    action="{ActionName}",
                    timeout_seconds=180,
                )
                expect_ok_action(response, "{ActionName}")
                expect_instructions_contain(response, "{ExpectedKeyword}")

                artifact = follow_instructions(
                    "Follow the {ActionName} instructions and produce the artifact.",
                    timeout_seconds=300,
                ).text
                expect(len(artifact) > 0).to(be_true)
                ai_judge(artifact, "{JudgeRubric}")
