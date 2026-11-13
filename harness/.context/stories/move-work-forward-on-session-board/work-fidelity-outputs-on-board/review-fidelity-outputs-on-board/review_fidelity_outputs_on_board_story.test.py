# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenarios of the sub-epic Review Fidelity Outputs On Board, as GWT structure only: the acceptance tests fill each step.
# Generated from the markdown beside it, which holds the domain terms, the evidence and the examples.
# Realizations are in harness/.context/stories/review-work-in-board-files-scenario-realization.md.

from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when



with story("List Ticket Files"):
    with scenario("List a fidelity's files with whether each exists"):
        with given("checkout-flow's story map .context/story-map.md is there and .context/story-map.drawio is not"):
            pass
        with when("the Person lists checkout-flow's story_map files"):
            pass
        with then("the files panel shows a .context/story-map.md tab, as there"):
            pass
        with but_("no file of another fidelity shows"):
            pass
    with scenario("List every file of the fidelity, changed or not"):
        with given("the ticket pet-visits works on its own branch pet-visits"):
            pass
        with and_("its bdd behavior files are src/theirs_spec.py and src/mine_spec.py, and its branch added src/mine_spec.py"):
            pass
        with when("the Person lists pet-visits' bdd behavior files"):
            pass
        with then("the tabs show src/theirs_spec.py and src/mine_spec.py"):
            pass
    with scenario("Filter the tabs to the files the ticket's branch changed"):
        with given("the tabs show pet-visits' bdd behavior files src/theirs_spec.py and src/mine_spec.py"):
            pass
        with and_("pet-visits' branch added src/mine_spec.py"):
            pass
        with when("the Person filters the files to changed files only"):
            pass
        with then("the tabs show src/mine_spec.py"):
            pass
        with but_("no src/theirs_spec.py tab shows"):
            pass
    with scenario("Clear the changed-files filter"):
        with given("the tabs show only pet-visits' changed file src/mine_spec.py"):
            pass
        with when("the Person clears the changed-files filter"):
            pass
        with then("the tabs show src/theirs_spec.py and src/mine_spec.py again"):
            pass


with story("Browse Ticket Files By Practice"):
    with scenario("Show the practice filters and every file as a tab along the top"):
        with given("the session of ticket checkout-flow works on Stories and BDD"):
            pass
        with and_("its Stories files are stories/story-map.md and stories/checkout_story.test.md, and its BDD file is src/order_spec.py"):
            pass
        with when("the Person browses checkout-flow's files"):
            pass
        with then("the top of the files panel shows a Stories filter and a BDD filter, each by its short form"):
            pass
        with and_("the tabs below them show story-map.md and checkout_story.test.md together in Stories' color, then order_spec.py in BDD's color"):
            pass
    with scenario("Preset the practice filters from the chat bar's Files button"):
        with given("the chat bar shows ticket checkout-flow at Stories scenarios"):
            pass
        with when("the Person opens checkout-flow's files from the chat bar"):
            pass
        with then("the Stories filter is on, and the tabs show story-map.md and checkout_story.test.md"):
            pass
        with but_("the BDD filter is off, and no order_spec.py tab shows"):
            pass
    with scenario("Turn a practice filter on"):
        with given("checkout-flow's files show with only the Stories filter on"):
            pass
        with when("the Person turns the BDD filter on"):
            pass
        with then("an order_spec.py tab shows in BDD's color, after the Stories tabs"):
            pass
    with scenario("Select a tab to view its file"):
        with given("the tabs show story-map.md, checkout_story.test.md and order_spec.py"):
            pass
        with when("the Person selects the order_spec.py tab"):
            pass
        with then("the viewer shows src/order_spec.py"):
            pass


with story("View Fidelity Files"):
    with scenario("Open one tab per format, colored by its practice, generated or not"):
        with given("checkout-flow's story map is .context/story-map.md and .context/story-map.drawio is not there"):
            pass
        with when("the Person views checkout-flow's story_map files"):
            pass
        with then("the tabs along the top show .context/story-map.md and .context/story-map.drawio, both in Stories' color"):
            pass
        with and_("the .context/story-map.md tab shows # Check Out Order"):
            pass
        with and_("the drawio tab says it is not generated yet"):
            pass


with story("Open Session Files From Details"):
    with scenario("Open the session folder from the session button"):
        with given("the session button shows ticket checkout-flow's own session"):
            pass
        with but_("not main, and not expanded"):
            pass
        with when("the Person opens checkout-flow's session from its session button"):
            pass
        with then("the file view shows .sessions/checkout-flow"):
            pass
    with scenario("Open the workpath folder from the details"):
        with given("the session of ticket checkout-flow works in the workpath harness/.context"):
            pass
        with when("the Person opens checkout-flow's workpath from its details"):
            pass
        with then("the files panel lists the entries of harness/.context"):
            pass
        with but_("the root chooser does not open"):
            pass
