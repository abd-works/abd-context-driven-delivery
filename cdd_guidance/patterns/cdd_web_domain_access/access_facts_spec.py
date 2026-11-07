"""What an annotated toolset's file says about the operations TypeScript reads."""

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.patterns.cdd_web_domain_access.access_facts import annotated_toolset_facts


def _toolset(*decorators: str) -> str:
    annotations = "".join(f"    {decorator}\n" for decorator in decorators)
    return (
        "from typing import Any\n"
        "\n"
        "@language_adapter()\n"
        "class Board:\n"
        f"{annotations}"
        "    def show(self) -> dict[str, Any]:\n"
        "        return {}\n"
    )


with description("an annotated toolset whose operation answers an open dict"):
    with context("that publishes the operation with @mcp"):
        with it("should report the operation as an open result TypeScript reads"):
            expect(annotated_toolset_facts(_toolset("@mcp"))["open_results"]).to(equal([[6, "show"]]))

    with context("that publishes the operation with @Mcp"):
        with it("should report the operation as an open result TypeScript reads"):
            expect(annotated_toolset_facts(_toolset("@Mcp"))["open_results"]).to(equal([[6, "show"]]))

    with context("that publishes the operation under four other annotations"):
        with it("should report the operation as an open result TypeScript reads"):
            facts = annotated_toolset_facts(_toolset("@Mcp", "@subAgent", "@Skill", "@agent_tool", "@noSessionLog"))
            expect(facts["open_results"]).to(equal([[10, "show"]]))

    with context("that does not publish the operation"):
        with it("should report no open result"):
            expect(annotated_toolset_facts(_toolset("@agent_tool"))["open_results"]).to(equal([]))
