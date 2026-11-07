"""What an annotated toolset's file says about the operations TypeScript reads."""

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.patterns.cdd_web_domain_access.access_facts import AccessFile


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
            expect(AccessFile("board.py", _toolset("@mcp")).annotated_toolset_facts()["open_results"]).to(equal([[6, "show"]]))

    with context("that publishes the operation with @Mcp"):
        with it("should report the operation as an open result TypeScript reads"):
            expect(AccessFile("board.py", _toolset("@Mcp")).annotated_toolset_facts()["open_results"]).to(equal([[6, "show"]]))

    with context("that publishes the operation under four other annotations"):
        with it("should report the operation as an open result TypeScript reads"):
            facts = AccessFile("board.py", _toolset("@Mcp", "@subAgent", "@Skill", "@agent_tool", "@noSessionLog")).annotated_toolset_facts()
            expect(facts["open_results"]).to(equal([[10, "show"]]))

    with context("that does not publish the operation"):
        with it("should report no open result"):
            expect(AccessFile("board.py", _toolset("@agent_tool")).annotated_toolset_facts()["open_results"]).to(equal([]))


with description("a file that may reach the CDD domain"):
    with context("named as a route"):
        with it("should become an AccessRoute carrying its tool calls"):
            tier = AccessFile("board-routes.ts", "router.get('/x', () => tools.call('board.show'));\n").tier()
            expect(tier).to(equal(("AccessRoute", {"tool_calls": [[1, ".call("]]})))

    with context("that reaches nothing"):
        with it("should become no node"):
            expect(AccessFile("board.css", "body {}\n").tier()).to(equal(None))
