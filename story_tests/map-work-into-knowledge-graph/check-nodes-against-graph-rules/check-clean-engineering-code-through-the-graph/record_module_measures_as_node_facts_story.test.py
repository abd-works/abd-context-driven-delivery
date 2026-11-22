# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Record Module Measures As Node Facts, as GWT structure only. Generated from the markdown beside it, which holds the domain terms, the evidence and
# the examples. Each scenario is proven by the specs its story's evidence names.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#ssystem-knowledge-graph----record-module-measures-as-node-facts

with story("Record Module Measures As Node Facts"):
    with scenario("Keep a module's measures on its node"):
        with given('the shop project\'s config has a `code_measures` section'):
            pass
        with and_('radon answers a maintainability score of 62.5 for every file'):
            pass
        with when('Claude Code validates clean-engineering-code on `shop/cart.py`'):
            pass
        with then('the node of the module shop holds modules_importing 0 and maintainability_score 62.5'):
            pass
    with scenario("Read the measures the graph already holds from the graph"):
        with given('the shop project\'s config has a `code_measures` section, which names no tool for a module\'s import loops or the modules it imports'):
            pass
        with when('the code measures of `shop/cart.py` are taken'):
            pass
        with then('its import loops are counted from its import_cycles fact and the modules it imports from its dependsOn edges, which every read records, and no tool is asked'):
            pass
    with scenario("Keep a module's maintainability score from its hardest checked file"):
        with given('the shop project\'s config chooses radon for a Python module\'s maintainability score'):
            pass
        with when('the code measures of `catalogue/catalogue.py` are taken with the real tools'):
            pass
        with then('the node of the module catalogue holds a maintainability_score above 0'):
            pass
