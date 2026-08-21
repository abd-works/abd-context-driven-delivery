# @agent-spec-manifest python -m tools agent-spec context_tools/actions/host_lifecycle/host_lifecycle_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/host_lifecycle/.context/.agent_bdd_sessions/host-lifecycle-generate-owns-tools.json
"""Agent BDD — lifecycle slash commands run HostLifecycle(tools=...) not host actions."""

from expects import contain, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_action,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)
_HOST_LIFECYCLE = "host_lifecycle.host_lifecycle:HostLifecycle"
_BDD = "context_tools.bdd.bdd:Bdd"


with description("a generate action"):
    with context("that is given one context tool"):
        with it("should run HostLifecycle.generate with that tool, not the host generate"):
            with agent(_REPO_ROOT, _SESSIONS / "host-lifecycle-generate-owns-tools.json"):
                read_workspace(".cursor/commands/generate.md")
                read_workspace("context_tools/actions/host_lifecycle/host_lifecycle.py")

                response = run_toolset(
                    toolset=_HOST_LIFECYCLE,
                    action="generate",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "generate")
                expect(response.toolset).to(equal(_HOST_LIFECYCLE))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /generate. Using the generate command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host generate on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if generate is owned by host_lifecycle.host_lifecycle:HostLifecycle "
                    "and the BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action generate.",
                )


with description("a validate action"):
    with context("that is given one context tool"):
        with it("should run HostLifecycle.validate with that tool, not the host validate"):
            with agent(_REPO_ROOT, _SESSIONS / "host-lifecycle-validate-owns-tools.json"):
                read_workspace(".cursor/commands/validate.md")
                read_workspace("context_tools/actions/host_lifecycle/host_lifecycle.py")

                response = run_toolset(
                    toolset=_HOST_LIFECYCLE,
                    action="validate",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "validate")
                expect(response.toolset).to(equal(_HOST_LIFECYCLE))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /validate. Using the validate command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host validate on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if validate is owned by host_lifecycle.host_lifecycle:HostLifecycle "
                    "and the BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action validate.",
                )


with description("a document action"):
    with context("that is given one context tool"):
        with it("should run HostLifecycle.document with that tool, not the host document"):
            with agent(_REPO_ROOT, _SESSIONS / "host-lifecycle-document-owns-tools.json"):
                read_workspace(".cursor/commands/document.md")
                read_workspace("context_tools/actions/host_lifecycle/host_lifecycle.py")

                response = run_toolset(
                    toolset=_HOST_LIFECYCLE,
                    action="document",
                    arguments={"tools": [_BDD], "paths": ["context_tools/bdd/bdd.py"]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "document")
                expect(response.toolset).to(equal(_HOST_LIFECYCLE))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /document. Using the document command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host document on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if document is owned by host_lifecycle.host_lifecycle:HostLifecycle "
                    "and the BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action document.",
                )


with description("a satisfy action"):
    with context("that is given one context tool"):
        with it("should run HostLifecycle.satisfy with that tool, not the host satisfy"):
            with agent(_REPO_ROOT, _SESSIONS / "host-lifecycle-satisfy-owns-tools.json"):
                read_workspace(".cursor/commands/satisfy.md")
                read_workspace("context_tools/actions/host_lifecycle/host_lifecycle.py")

                response = run_toolset(
                    toolset=_HOST_LIFECYCLE,
                    action="satisfy",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "satisfy")
                expect(response.toolset).to(equal(_HOST_LIFECYCLE))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /satisfy. Using the satisfy command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host satisfy on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if satisfy is owned by host_lifecycle.host_lifecycle:HostLifecycle "
                    "and the BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action satisfy.",
                )
