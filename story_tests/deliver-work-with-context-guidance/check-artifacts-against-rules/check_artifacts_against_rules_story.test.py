# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Check Artifacts Against Rules, as GWT structure only. Generated from the markdown beside it, which holds the domain
# terms, the evidence and the examples. Each scenario is proven by the specs its story's evidence names.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when


with story("Validate Artifact Against Rules"):
    with scenario("Check the one rule a call names"):
        with given('.context/story-map.md holds the story map'):
            pass
        with when('Claude Code validates stories-story-map on .context/story-map.md with rule verb-noun-format'):
            pass
        with then('the report hands the judge verb-noun-format'):
            pass
        with and_('the report leaves child-count-fits-layer out'):
            pass
    with scenario("Refuse a rule no listed guidance has"):
        with given('.context/story-map.md holds the story map'):
            pass
        with when('Claude Code validates stories-story-map on .context/story-map.md with rule no-such-rule'):
            pass
        with then('the call is refused, saying there is no rule no-such-rule'):
            pass
        with and_('the refusal lists verb-noun-format among the rules there are'):
            pass
    with scenario("Check the session's graph built from the written output"):
        with given('src/orders/order.ts holds class Order, whose place operation takes five parameters'):
            pass
        with and_('the session has no saved graph'):
            pass
        with when('Claude Code validates clean-engineering-code with graph true and no paths'):
            pass
        with then('the report holds the limit-operation-parameters violation in src/orders/order.ts'):
            pass
    with scenario("Refuse a graph file that is not there"):
        with given('no/such/graph.json is not in the project'):
            pass
        with when('Claude Code validates clean-engineering-code with graph no/such/graph.json'):
            pass
        with then("the call is refused, naming no/such/graph.json as not there, read from the project's root"):
            pass
    with scenario("Refuse an empty path as it refuses a missing one"):
        with given('.context/story-map.md holds the story map'):
            pass
        with when('Claude Code validates stories-story-map on .context/story-map.md and a path that is empty or only spaces'):
            pass
        with then('the call is refused, saying an empty path names no file or folder'):
            pass
        with and_('no validation report is saved'):
            pass
