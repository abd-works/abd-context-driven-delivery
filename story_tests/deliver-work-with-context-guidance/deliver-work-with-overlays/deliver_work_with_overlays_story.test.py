# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Deliver Work With Overlays, as GWT structure only: the acceptance tests fill each step.
# Generated from the markdown beside it, which holds the domain terms, the evidence, the examples,
# and which scenarios are Observed and which Intended.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when


with story("Select Pattern Overlays For Session"):
    with scenario("Choose the overlays a command names"):
        with given("checkout-flow's session overlays none"):
            pass
        with when("Claude Code generates stories-acceptance-tests with overlays=lern_domain_driven,mern_domain_driven"):
            pass
        with then("checkout-flow's session overlays lern_domain_driven and mern_domain_driven"):
            pass
        with and_("checkout-flow's session.json keeps both among its overlays"):
            pass
    with scenario("Keep the session's overlays when a command names none"):
        with given("checkout-flow's session overlays lern_domain_driven"):
            pass
        with when("Claude Code generates stories-acceptance-tests with no overlays word"):
            pass
        with then("checkout-flow's session still overlays lern_domain_driven"):
            pass
    with scenario("Clear the overlays with an empty overlays word"):
        with given("checkout-flow's session overlays lern_domain_driven"):
            pass
        with when("Claude Code generates stories-acceptance-tests with overlays="):
            pass
        with then("checkout-flow's session overlays none"):
            pass
    with scenario("Choose a guidance overlay beside a stack pattern"):
        with given("checkout-flow's session overlays none"):
            pass
        with when("Claude Code generates bdd-development with overlays=lern_domain_driven,tdd"):
            pass
        with then("checkout-flow's session overlays lern_domain_driven and tdd"):
            pass

with story("Decorate Practice Fidelity With Overlay Guidance"):
    with scenario("Decorate each fidelity the overlay names"):
        with given("the tdd overlay names clean-engineering-code, stories-acceptance-tests and bdd-development as its decorated fidelities"):
            pass
        with when("the cdd server registers the tdd overlay"):
            pass
        with then("clean-engineering-code, stories-acceptance-tests and bdd-development each list tdd among their overlays"):
            pass
        with and_("the Agent goes on to Inject Overlay Guidance Into Fidelity Instructions"):
            pass
    with scenario("Leave a fidelity the overlay does not name undecorated"):
        with given("the tdd overlay names clean-engineering-code, stories-acceptance-tests and bdd-development as its decorated fidelities"):
            pass
        with when("the cdd server registers the tdd overlay"):
            pass
        with then("stories-story-map lists no overlay"):
            pass

with story("Inject Overlay Guidance Into Fidelity Instructions"):
    with scenario("Add a decorating overlay's guidance to the fidelity instructions"):
        with given("checkout-flow's session overlays tdd"):
            pass
        with when("the Agent loads the stories-acceptance-tests instructions"):
            pass
        with then("the instructions hold the tdd overlay's guidance after the practice's rules"):
            pass
        with and_("they name tdd as the overlay it comes from"):
            pass
    with scenario("Leave out an overlay that does not decorate the fidelity"):
        with given("checkout-flow's session overlays tdd"):
            pass
        with when("the Agent loads the stories-story-map instructions"):
            pass
        with then("the instructions hold no tdd guidance"):
            pass
    with scenario("Load the practice's words alone with no overlay chosen"):
        with given("checkout-flow's session overlays none"):
            pass
        with when("the Agent loads the bdd-development instructions"):
            pass
        with then("the instructions hold BDD's guidance and rules and name no overlay"):
            pass

with story("Generate With Overlay Rules"):
    with scenario("Add each chosen overlay's shared rules when generating"):
        with given("checkout-flow's session overlays lern_domain_driven and mern_domain_driven"):
            pass
        with when("the Agent generates stories-acceptance-tests"):
            pass
        with then("the instructions hold a Pattern overlay: lern_domain_driven section with its overlay shared rules"):
            pass
        with and_("they hold a Pattern overlay: mern_domain_driven section with its shared rules"):
            pass
    with scenario("Generate with no overlay chosen"):
        with given("checkout-flow's session overlays none"):
            pass
        with when("the Agent generates stories-acceptance-tests"):
            pass
        with then("the instructions name no pattern overlay"):
            pass
    with scenario("Add an overlay's rules only to a fidelity it decorates"):
        with given("checkout-flow's session overlays tdd"):
            pass
        with when("the Agent generates stories-story-map"):
            pass
        with then("the instructions hold no tdd rules"):
            pass
        with when("the Agent generates bdd-development"):
            pass
        with then("the instructions hold the tdd overlay's rules"):
            pass

with story("Validate With Overlay Rules"):
    with scenario("Judge the work against the overlays it was generated with"):
        with given("checkout-flow's acceptance tests were generated with lern_domain_driven"):
            pass
        with when("the Agent validates stories-acceptance-tests on those tests"):
            pass
        with then("the report asks to judge the work against the lern_domain_driven shared rules too"):
            pass
    with scenario("Validate with no overlay chosen"):
        with given("checkout-flow's session overlays none"):
            pass
        with when("the Agent validates stories-acceptance-tests"):
            pass
        with then("the report names no pattern overlay"):
            pass
    with scenario("Judge an overlay's rules only on a fidelity it decorates"):
        with given("checkout-flow's session overlays tdd"):
            pass
        with when("the Agent validates stories-story-map"):
            pass
        with then("the report judges no tdd rules"):
            pass
        with when("the Agent validates bdd-development"):
            pass
        with then("the report judges the work against the tdd overlay's rules too"):
            pass
