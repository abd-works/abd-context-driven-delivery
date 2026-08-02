# @agent-spec-manifest python -m tools agent-spec primitives/assets/assets_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: primitives/assets/.context/.agent_bdd_sessions/card-file.json
"""BDD agent spec for CardFile — AI discovers AssetLocator-backed tools."""

from expects import be_true, contain, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_tool,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_CARD_PY = "primitives/assets/examples/card_file/card_file.py"
_CARD_TOOLSET = "primitives.assets.examples.card_file.card_file:CardFile"

with description("a CardFile toolset"):
    with context("with agent reading AssetLocator-backed cards"):
        with it("reads quick-start then faq via tools run"):
            with agent(_REPO_ROOT, _SESSIONS / "card-file.json"):
                read_workspace(_CARD_PY)

                quick = run_toolset(
                    toolset=_CARD_TOOLSET,
                    tool="read_card",
                    arguments={"label": "quick-start"},
                    timeout_seconds=120,
                )
                expect_ok_tool(quick, "read_card")
                expect(str(quick.result).lower()).to(contain("quick start"))
                expect(str(quick.result).lower()).to(contain("assetlocator"))

                topic = run_toolset(
                    toolset=_CARD_TOOLSET,
                    tool="set_topic",
                    context={"topic": "quick-start"},
                    arguments={"label": "faq"},
                    timeout_seconds=120,
                )
                expect_ok_tool(topic, "set_topic")
                expect(str(topic.resources.get("topic", "")).lower()).to(contain("faq"))

                faq = run_toolset(
                    toolset=_CARD_TOOLSET,
                    tool="read_card",
                    context={"topic": "faq"},
                    arguments={"label": "faq"},
                    timeout_seconds=120,
                )
                expect_ok_tool(faq, "read_card")
                expect(str(faq.result).lower()).to(contain("what is assetlocator"))

                merged = run_toolset(
                    toolset=_CARD_TOOLSET,
                    tool="read_all",
                    timeout_seconds=120,
                )
                expect_ok_tool(merged, "read_all")
                expect(len(str(merged.result)) > 0).to(be_true)

                ai_judge(
                    str(merged.result),
                    "The merged cards include an intro welcome and mention the cards subfolder.",
                )
