"""BDD behavior — markdown collection annotation. Signatures only."""
from mamba import description, context, it


with description("a markdown collection"):
    with context("that has been built from a Guidance member"):
        with context("with the member annotated as a markdown collection for shared rules"):
            # @markdownCollection("shared rules")
            # def rules(self) -> RulesCollection:
            with it("should expose the original extract on rules.markdown"):
                # BDD: SIGNATURE
                pass

            with it("should keep parsed rules on rules"):
                # BDD: SIGNATURE
                pass

        with context("with one file"):
            with it("should expose that file's extract on markdown"):
                # BDD: SIGNATURE
                pass

        with context("with a list return type"):
            # @markdownCollection("examples")
            # def examples(self) -> list:
            with context("that has section bullets"):
                with it("should iterate one markdown per bullet"):
                    # BDD: SIGNATURE
                    pass

            with context("that has a folder of files"):
                with it("should iterate one markdown per file"):
                    # BDD: SIGNATURE
                    pass

        with context("with a map return type"):
            # @markdownCollection("shared rules")
            # def rules(self) -> RulesCollection:
            with context("that has section bullets"):
                with it("should key each entry by the bullet label"):
                    # BDD: SIGNATURE
                    pass

            with context("that has a folder of files"):
                with it("should key each entry by the file stem"):
                    # BDD: SIGNATURE
                    pass


with description("a guidance"):
    with context("that has been asked for rules markdown"):
        with it("should read rules.markdown"):
            # BDD: SIGNATURE
            pass

        with it("should not own a rules_markdown property"):
            # BDD: SIGNATURE
            pass

    with context("that injects rules"):
        with it("should inject rules.markdown"):
            # BDD: SIGNATURE
            pass

    with context("that assembles instructions"):
        with it("should include rules.markdown"):
            # BDD: SIGNATURE
            pass
