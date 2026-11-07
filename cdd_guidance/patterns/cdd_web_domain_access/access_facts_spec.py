"""What a marked toolset's file says about the operations TypeScript reads."""

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.patterns.cdd_web_domain_access.access_facts import marked_toolset_facts


def _toolset(*decorators: str) -> str:
    marks = "".join(f"    {decorator}\n" for decorator in decorators)
    return (
        "from typing import Any\n"
        "\n"
        "@language_adapter()\n"
        "class Board:\n"
        f"{marks}"
        "    def show(self) -> dict[str, Any]:\n"
        "        return {}\n"
    )


with description("a marked toolset whose operation answers an open dict"):
    with context("that publishes the operation with @mcp"):
        with it("should report the operation as an open result TypeScript reads"):
            expect(marked_toolset_facts(_toolset("@mcp"))["open_results"]).to(equal([[6, "show"]]))

    with context("that publishes the operation with @Mcp"):
        with it("should report the operation as an open result TypeScript reads"):
            expect(marked_toolset_facts(_toolset("@Mcp"))["open_results"]).to(equal([[6, "show"]]))

    with context("that publishes the operation under four other marks"):
        with it("should report the operation as an open result TypeScript reads"):
            facts = marked_toolset_facts(_toolset("@Mcp", "@subAgent", "@Skill", "@agent_tool", "@noSessionLog"))
            expect(facts["open_results"]).to(equal([[10, "show"]]))

    with context("that does not publish the operation"):
        with it("should report no open result"):
            expect(marked_toolset_facts(_toolset("@agent_tool"))["open_results"]).to(equal([]))
