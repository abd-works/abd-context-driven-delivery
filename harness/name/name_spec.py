from mamba import description, it
from expects import equal, expect

from harness.name.name import Name


with description("a Name") as self:
    with description("written in camel case"):
        with it("should give its words split at each capital"):
            expect(Name("PreToolUse").words).to(equal(["pre", "tool", "use"]))

        with it("should keep a run of capitals as one word"):
            expect(Name("MCPServer").snake).to(equal("mcpserver"))

        with it("should become snake case"):
            expect(Name("GrillContext").snake).to(equal("grill_context"))

        with it("should become kebab case"):
            expect(Name("CleanEngineering").kebab).to(equal("clean-engineering"))

    with description("written in snake case"):
        with it("should become camel case"):
            expect(Name("set_wip_limit").camel).to(equal("setWipLimit"))

        with it("should become kebab case"):
            expect(Name("story_map").kebab).to(equal("story-map"))

    with description("written in kebab case"):
        with it("should become snake case"):
            expect(Name("pre-tool-use").snake).to(equal("pre_tool_use"))

        with it("should become camel case"):
            expect(Name("verify-ported-number").camel).to(equal("verifyPortedNumber"))

    with description("that is a title"):
        with it("should become a slug of its lower-case words"):
            expect(Name("Pet visits: phase 2!").title_slug).to(equal("pet-visits-phase-2"))

        with it("should not split a word at a capital"):
            expect(Name("iPhone notes").title_slug).to(equal("iphone-notes"))

        with it("should become a Python name of its lower-case words"):
            expect(Name("Show the API keys").title_snake).to(equal("show_the_api_keys"))

        with it("should become a class name of its capitalised words"):
            expect(Name("show the API keys").title_pascal).to(equal("ShowTheApiKeys"))

        with it("should become a member name with its first word in lower case"):
            expect(Name("Show the API keys").title_camel).to(equal("showTheApiKeys"))

    with description("that is empty"):
        with it("should have no words"):
            expect(Name("").kebab).to(equal(""))
