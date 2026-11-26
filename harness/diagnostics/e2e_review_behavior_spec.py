"""BDD behavior — reviewing end-to-end screens step by step. Signatures only.

Story map: .context/story-map.md, epic Review End-To-End Screens. Ticket: .sessions/e2e-testing/e2e-testing.md.
"""
from mamba import description, context, it


with description("a walk of a scenario by hand"):
    with context("that has screenshotted each step"):
        with it("should record each step's screenshot under its story, scenario and step key"):
            # BDD: SIGNATURE
            pass

        with it("should record each step's Given, When or Then text beside its screenshot"):
            # BDD: SIGNATURE
            pass

        with it("should mark each step as walked by hand"):
            # BDD: SIGNATURE
            pass

    with context("that has judged each step against its step text"):
        with context("with a step whose screen shows what its step means"):
            with it("should record that the step meets the intent, with its reason"):
                # BDD: SIGNATURE
                pass

        with context("with a step whose screen does not show what its step means"):
            with it("should record that the step misses the intent, with what is wrong"):
                # BDD: SIGNATURE
                pass

    with context("that has written its report"):
        with it("should show each step's text, its one screenshot, and its verdict with the reason"):
            # BDD: SIGNATURE
            pass

        with it("should open each scenario that has a step that misses the intent"):
            # BDD: SIGNATURE
            pass

        with it("should open as one page with its screenshots inside it"):
            # BDD: SIGNATURE
            pass

    with context("that the person has accepted"):
        with context("with every step meeting the intent"):
            with it("should become the reference for its sub-epic's end-to-end tests"):
                # BDD: SIGNATURE
                pass

        with context("with a step that misses the intent"):
            with it("should refuse the acceptance, naming the step"):
                # BDD: SIGNATURE
                pass


with description("an end-to-end run"):
    with context("that has screenshotted each step after the page settled"):
        with it("should record one row per step with its key, step text, result and screenshot"):
            # BDD: SIGNATURE
            pass

        with it("should mark each step as run by a test"):
            # BDD: SIGNATURE
            pass

    with context("that is compared with the accepted walk of its scenarios"):
        with it("should pair each step with the same step of the walk"):
            # BDD: SIGNATURE
            pass

        with it("should list as changed only the pairs whose screens differ"):
            # BDD: SIGNATURE
            pass

    with context("that is compared with the last accepted run"):
        with it("should choose the last run the person accepted for the same sub-epic"):
            # BDD: SIGNATURE
            pass

        with it("should pair each step with the same step of that run"):
            # BDD: SIGNATURE
            pass

        with it("should list as changed only the pairs whose screens differ"):
            # BDD: SIGNATURE
            pass

        with context("with a step the accepted run does not have"):
            with it("should list the step as new, with no earlier screen"):
                # BDD: SIGNATURE
                pass

    with context("with a changed pair that has no verdict"):
        with it("should not count as reviewed"):
            # BDD: SIGNATURE
            pass

    with context("with every changed pair judged intended"):
        with it("should count as reviewed"):
            # BDD: SIGNATURE
            pass

        with context("that the person has accepted"):
            with it("should become the baseline the next run is compared with"):
                # BDD: SIGNATURE
                pass

    with context("with a changed pair judged regression caught, missed by the tests, or noise"):
        with it("should refuse the person's acceptance, naming the pair"):
            # BDD: SIGNATURE
            pass

        with it("should leave the baseline where it was"):
            # BDD: SIGNATURE
            pass


with description("a changed step pair"):
    with context("that is judged intended"):
        with it("should record the story or code change it cites"):
            # BDD: SIGNATURE
            pass

        with context("with no story or code change cited"):
            with it("should refuse the verdict"):
                # BDD: SIGNATURE
                pass

    with context("that is judged regression caught"):
        with it("should record the test that fails for it"):
            # BDD: SIGNATURE
            pass

    with context("that is judged missed by the tests"):
        with it("should record what the screen shows wrong"):
            # BDD: SIGNATURE
            pass

    with context("that is judged noise"):
        with it("should record what moved between the two screens"):
            # BDD: SIGNATURE
            pass


with description("the report of a compared run"):
    with it("should show each step's two screens side by side with its verdict and reason"):
        # BDD: SIGNATURE
        pass

    with it("should count passed, changed and missed steps for each story and sub-epic"):
        # BDD: SIGNATURE
        pass

    with context("with the filter set to changed or missed steps"):
        with it("should show only the steps that changed or missed"):
            # BDD: SIGNATURE
            pass

    with context("that has been written into the run history"):
        with it("should keep the run's page without its screenshots"):
            # BDD: SIGNATURE
            pass

        with it("should add the run's counts and missed steps to the history summary"):
            # BDD: SIGNATURE
            pass


with description("the daily end-to-end run"):
    with context("that has finished"):
        with it("should start the regression review in a background agent session"):
            # BDD: SIGNATURE
            pass

        with context("with a step judged missed by the tests"):
            with it("should raise a toast naming the step"):
                # BDD: SIGNATURE
                pass

    with context("that has been reviewed"):
        with it("should show its changed and missed counts in the server health report"):
            # BDD: SIGNATURE
            pass

        with it("should link the server health report to its story map report"):
            # BDD: SIGNATURE
            pass
