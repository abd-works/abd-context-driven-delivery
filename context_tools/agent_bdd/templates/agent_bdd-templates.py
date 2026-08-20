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
#   {PassFixturePath}  pass-file fixture (repairedAsset / examples/evals/.../pass.md)
#   {JudgeRubric}     one sentence describing PASS criteria
# =============================================================================

from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_instructions_contain,
    expect_ok_action,
    generate_and_judge,
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

                generate_and_judge("{PassFixturePath}", "{JudgeRubric}")
