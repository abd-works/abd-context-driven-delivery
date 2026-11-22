# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Record Module Measures As Node Facts, run on the domain objects: the shop project's module node, the reader that
# keeps a module's measures on it, and the metrics group the explorer tree shows under it. No outside tool takes a
# module's measures: the practice's own reader counts them from the graph.

from __future__ import annotations

from expects import be_false, equal, expect

from cdd_guidance.practices.clean_engineering.measures.code_measures import IMPORT_LOOPS, MODULES_IMPORTED, ChosenTools
from cdd_guidance.practices.clean_engineering.measures.examples.code_measures_examples import (
    CART_FILE,
    checked_graph_file,
    code_files,
    kept_on,
    metrics_under,
    node_of,
    shop_project,
)
from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#ssystem-knowledge-graph----record-module-measures-as-node-facts
# Scenarios: record_module_measures_as_node_facts_story.test.md

with story("Record Module Measures As Node Facts"):
    with scenario("Keep a module's measures on its node"):
        with given("the shop project's config has a `code_measures` section"):
            self.shop = shop_project()
        with when("Claude Code validates clean-engineering-code on `shop/cart.py`"):
            # Validate -> GraphReads.refreshed -> GraphReading.read_working_copy -> CheckedCodeMeasures.take
            self.shop.practice.reading.graph.reads.refreshed([CART_FILE], checked_graph_file())
        with then("the node of the module shop holds modules_importing 0, counted by the practice's own reader"):
            expect(kept_on(self.shop, "Package", "shop", ["modules_importing"])).to(equal({"modules_importing": 0}))
    with scenario("Read the measures the graph already holds from the graph"):
        with given("the shop project's config has a `code_measures` section, which names no tool for a module's import loops or the modules it imports"):
            self.shop = shop_project()
            self.asked_of_a_tool = [ChosenTools({}).supplied_by_a_tool(measure) for measure in (IMPORT_LOOPS, MODULES_IMPORTED)]
        with when("the code measures of `shop/cart.py` are taken"):
            self.shop.practice.reading.keep_code_measures(code_files(self.shop))
        with then("its import loops are counted from its import_cycles fact and the modules it imports from its dependsOn edges, which every read records, and no tool is asked"):
            shop = node_of(self.shop, "Package", "shop")
            expect([IMPORT_LOOPS.value_on(shop), MODULES_IMPORTED.value_on(shop), *self.asked_of_a_tool]).to(equal([0, 0, False, False]))
        with and_("the node keeps no second fact for either"):
            expect([node_of(self.shop, "Package", "shop").has_fact(name) for name in ("import_loops", "modules_imported")]).to(equal([False, False]))
    with scenario("Show a module's three measures in its metrics group"):
        with given("the shop project's config has a `code_measures` section"):
            self.shop = shop_project()
        with when("the code measures of `shop/cart.py` are taken and the explorer tree is built again"):
            self.shop.practice.reading.keep_code_measures(code_files(self.shop))
            # Graph.explorer_branch -> GraphReading.metrics_of
            self.shown = metrics_under(self.shop, "Package", "shop")
        with then("the metrics group under the module shop shows its import loops with the limit 0, then the modules it imports and the modules that import it with their value and no limit"):
            expect(self.shown).to(equal([
                "loops of modules importing one another that a module is part of: 0, limit 0",
                "modules a module imports (outgoing coupling): 0",
                "modules that import a module (incoming coupling): 0",
            ]))
        with and_("neither of the two measures with no limit is marked as past a limit"):
            unlimited = [metric for metric in self.shop.practice.reading.metrics_of(node_of(self.shop, "Package", "shop")) if metric.limit is None]
            expect(any(metric.is_past_limit for metric in unlimited)).to(be_false)
