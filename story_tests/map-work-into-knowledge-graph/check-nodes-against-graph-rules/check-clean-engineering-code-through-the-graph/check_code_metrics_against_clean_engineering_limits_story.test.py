# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Check Code Metrics Against Clean Engineering Limits, as GWT structure only. Generated from the markdown beside it, which holds the domain terms, the evidence and
# the examples. Each scenario is proven by the specs its story's evidence names.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#ssystem-validate----check-code-metrics-against-clean-engineering-limits

with story("Check Code Metrics Against Clean Engineering Limits"):
    with scenario("Report a node whose measure is past its limit"):
        with given('the node of <node> holds <measure> <value>'):
            pass
        with when('the graph rules run'):
            pass
        with then('<rule> reports it, saying "<words>"'):
            pass
    with scenario("Pass a node whose measure is at its limit"):
        with given('the node of the function total holds paths_through 10'):
            pass
        with when('the graph rules run'):
            pass
        with then('limit-paths-through-a-function reports nothing'):
            pass
    with scenario("Pass a node no read measured"):
        with given('the node of the function total holds no paths_through'):
            pass
        with when('the graph rules run'):
            pass
        with then('limit-paths-through-a-function reports nothing'):
            pass
    with scenario("Hold a measure to the limit the project sets"):
        with given('the shop project\'s config sets the limit of paths_through to 20'):
            pass
        with and_('the node of the function total holds paths_through 14'):
            pass
        with when('the graph rules run'):
            pass
        with then('limit-paths-through-a-function reports nothing'):
            pass
    with scenario("Report a rule's failing example and pass its repaired example"):
        with given('the failing example and the repaired example of <rule>'):
            pass
        with when('the code measures of each are taken with the real tools and the graph rules run'):
            pass
        with then('<rule> reports the failing example'):
            pass
        with and_('it reports nothing in the repaired example'):
            pass
    with scenario("Report a function past its limit in the validation report"):
        with given('the parcels project\'s config has a `code_measures` section'):
            pass
        with and_('`src/parcels/parcel.py` holds the function send, which takes six parameters'):
            pass
        with when('Claude Code validates clean-engineering-code on `src/parcels/parcel.py`'):
            pass
        with then('the report holds the limit-function-parameters violation "has 6 parameters, over the limit of 5" in `src/parcels/parcel.py`, beside the other rules'):
            pass
