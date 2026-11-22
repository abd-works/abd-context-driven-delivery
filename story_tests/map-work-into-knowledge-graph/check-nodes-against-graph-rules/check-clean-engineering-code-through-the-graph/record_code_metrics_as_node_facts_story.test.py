# ---
# fidelity: [specification]
# artifact: [story-scenarios]
# format: py
# ---
#
# Record Code Metrics As Node Facts, as GWT structure only. Generated from the markdown beside it, which holds the domain terms, the evidence and
# the examples. Each scenario is proven by the specs its story's evidence names.

from __future__ import annotations

from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#ssystem-knowledge-graph----record-code-metrics-as-node-facts

with story("Record Code Metrics As Node Facts"):
    with scenario("Keep a function's measures on its node"):
        with given('the shop project\'s config has a `code_measures` section'):
            pass
        with and_('lizard answers 14 paths and a readability score of 3 for every function'):
            pass
        with when('Claude Code validates clean-engineering-code on `shop/cart.py`'):
            pass
        with then('the node of the function total holds paths_through 14 and readability_score 3, and its lines and its parameters are read from line_count and its parameter nodes, which every read keeps'):
            pass
    with scenario("Keep a class's measures on its node"):
        with given('the shop project\'s config has a `code_measures` section'):
            pass
        with and_('lizard answers a total complexity of 40 for every class'):
            pass
        with when('Claude Code validates clean-engineering-code on `shop/cart.py`'):
            pass
        with then('the node of the class Cart holds total_complexity 40, method_count 4, classes_depended_on 0 and unshared_method_groups 2'):
            pass
    with scenario("Take a measure with the tool chosen for its language"):
        with given('the shop project\'s config has a `code_measures` section'):
            pass
        with and_('the Catalogue class\'s priceOf, in `catalogue/catalogue.<extension>`, has eleven branches'):
            pass
        with when('the code measures of that file are taken'):
            pass
        with then('the node of the function holds paths_through 12, as lizard counts them'):
            pass
    with scenario("Report code in a language nobody chose a tool for"):
        with given('the shop project\'s config has a `code_measures` section, which chooses no tool for JavaScript'):
            pass
        with when('Claude Code validates clean-engineering-code on `catalogue/catalogue.js`'):
            pass
        with then('limit-paths-through-a-function reports the file once, naming the measure paths_through, the language javascript, and the config file to choose a tool in'):
            pass
    with scenario("Report a chosen tool that is not installed"):
        with given('the shop project\'s config chooses lizard for a Python function\'s paths'):
            pass
        with and_('lizard is not installed'):
            pass
        with when('the code measures of `shop/cart.py` are taken'):
            pass
        with then('limit-paths-through-a-function reports the file once, naming the tool lizard, the measure, and the command that installs it'):
            pass
    with scenario("Leave out a measure the project says is not measured"):
        with given('the shop project\'s config writes `not measured` for copied code blocks in Python'):
            pass
        with when('the code measures of `shop/cart.py` are taken'):
            pass
        with then('the node of the module shop holds no copied_code_blocks'):
            pass
    with scenario("Measure only the files a read names"):
        with given('the shop project\'s config has a `code_measures` section'):
            pass
        with when('the whole working copy of the shop project is loaded into the graph'):
            pass
        with then('no node holds a code measure'):
            pass
    with scenario("Take no measure in a project that chose no tools"):
        with given('the shop project\'s config has no `code_measures` section'):
            pass
        with when('Claude Code validates clean-engineering-code on `shop/cart.py`'):
            pass
        with then('no node holds a code measure'):
            pass
        with and_('the validate reports the other rules as before'):
            pass
