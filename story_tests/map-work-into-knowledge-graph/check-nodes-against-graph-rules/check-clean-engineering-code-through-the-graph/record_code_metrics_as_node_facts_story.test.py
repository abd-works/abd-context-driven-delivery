# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Record Code Metrics As Node Facts, run on the domain objects: the shop project read into the graph, the reader that
# keeps each measure on its node, and the limit rules that report a measure nobody could take. The outside tools are
# stood in for (measures/examples/code_measures_examples.py); code_measures_heavy_spec.py runs the real ones.

from __future__ import annotations

from expects import be_false, contain, equal, expect, have_len

from cdd_guidance.practices.clean_engineering.measures.code_measures import CODE_LINES, PARAMETERS_TAKEN, NoToolChosen, ChosenTools, PATHS_THROUGH
from cdd_guidance.practices.clean_engineering.measures.examples.code_measures_examples import (
    CART,
    CART_FILE,
    CART_WITH_A_HELPER,
    CATALOGUE,
    NO_MEASURES_CHOSEN,
    READER_ALONE,
    SHOP_CARD,
    CountingLizard,
    LizardNotInstalled,
    any_measure_kept,
    checked_graph_file,
    code_files,
    kept_on,
    node_of,
    reports_of,
    shop_project,
)
from harness.graph.saved_graph import SavedGraph
from story_test import and_, given, scenario, story, then, when

# Seed: a config that writes `not measured` for copied code blocks in Python.
NOT_MEASURING_COPIES = {".context/config.json": '{"code_measures": {"tools": {"copied_code_blocks": {"python": "not measured"}}}}'}

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#ssystem-knowledge-graph----record-code-metrics-as-node-facts
# Scenarios: record_code_metrics_as_node_facts_story.test.md

with story("Record Code Metrics As Node Facts"):
    with scenario("Keep a function's measures on its node"):
        with given("the shop project's config has a `code_measures` section"):
            self.shop = shop_project()
        with and_("lizard answers 14 paths and a readability score of 3 for every function"):
            pass  # StandInLizard, which the shop project's reading asks in lizard's place.
        with when("Claude Code validates clean-engineering-code on `shop/cart.py`"):
            # Validate -> GraphReads.refreshed -> GraphReading.read_working_copy -> CheckedCodeMeasures.take
            self.shop.practice.reading.graph.reads.refreshed([CART_FILE], checked_graph_file())
        with then("the node of the function total holds paths_through 14 and readability_score 3, and its lines and its parameters are read from line_count and its parameter nodes, which every read keeps"):
            total = node_of(self.shop, "Operation", "total")
            expect(kept_on(self.shop, "Operation", "total", ["paths_through", "readability_score", "code_lines", "parameters_taken"])).to(equal({"paths_through": 14, "readability_score": 3}))
            expect((CODE_LINES.value_on(total), PARAMETERS_TAKEN.value_on(total))).to(equal((total.get_fact("line_count"), 1)))
    with scenario("Keep a class's measures on its node"):
        with given("the shop project's config has a `code_measures` section"):
            self.shop = shop_project()
        with and_("lizard answers a total complexity of 40 for every class"):
            pass  # StandInLizard, as above.
        with when("Claude Code validates clean-engineering-code on `shop/cart.py`"):
            self.shop.practice.reading.graph.reads.refreshed([CART_FILE], checked_graph_file())
        with then("the node of the class Cart holds total_complexity 40, method_count 4, classes_depended_on 0 and unshared_method_groups 2"):
            kept = kept_on(self.shop, "OoadClass", "Cart", ["total_complexity", "method_count", "classes_depended_on", "unshared_method_groups"])
            expect(kept).to(equal({"total_complexity": 40, "method_count": 4, "classes_depended_on": 0, "unshared_method_groups": 2}))
    with scenario("Leave a method that uses no field of its class out of the groups sharing no data"):
        with given("the shop project's Cart also has the function label, which uses no field of the cart"):
            self.shop = shop_project(files={CART_FILE: CART_WITH_A_HELPER}, tools=READER_ALONE)
        with when("the code measures of `shop/cart.py` are taken"):
            # CheckedCodeMeasures.take -> ReaderTool -> MethodGroups.count
            self.shop.practice.reading.keep_code_measures(code_files(self.shop))
        with then("the node of the class Cart still holds unshared_method_groups 2"):
            expect(kept_on(self.shop, "OoadClass", "Cart", ["unshared_method_groups"])).to(equal({"unshared_method_groups": 2}))
    with scenario("Measure only the files a read names"):
        with given("the shop project's config has a `code_measures` section"):
            pass
        with when("the whole working copy of the shop project is loaded into the graph"):
            self.shop = shop_project()
        with then("no node holds a code measure"):
            expect(any_measure_kept(self.shop)).to(be_false)


with story("Measure Code With The Project's Chosen Tools"):
    with scenario("Take a measure with the tool chosen for its language"):
        # Outline: one run for each language the shipped table chooses lizard in.
        with given("the shop project's config has a `code_measures` section"):
            self.extensions = ("py", "ts", "js")
        with and_("the Catalogue class's priceOf, in `catalogue/catalogue.<extension>`, has eleven branches"):
            self.shops = [shop_project(files={f"catalogue/catalogue.{extension}": CATALOGUE[extension]}, tools={"lizard": CountingLizard}) for extension in self.extensions]
        with when("the code measures of that file are taken"):
            # CheckedCodeMeasures.take -> ChosenTools.tool_name(measure, language) -> MeasuringTool.value
            for shop in self.shops:
                shop.practice.reading.keep_code_measures(code_files(shop))
        with then("the node of the function holds paths_through 12, as lizard counts them"):
            expect([kept_on(shop, "Operation", "priceOf", ["paths_through"]) for shop in self.shops]).to(equal([{"paths_through": 12}] * 3))
    with scenario("Refuse code in a language nobody chose a tool for"):
        with given("the shop project's config has a `code_measures` section, which chooses no tool for Go"):
            self.chosen = ChosenTools({})
        with when("the tool for a Go function's paths is asked for"):
            # CheckedCodeMeasures -> ChosenTools.tool_name -> NoToolChosen, kept on the node for the measure's rule
            try:
                self.chosen.tool_name(PATHS_THROUGH, "go")
                self.refused = ""
            except NoToolChosen as refusal:
                self.refused = str(refusal)
        with then("the refusal names the measure paths_through, the language go, and the config file"):
            expect(self.refused).to(contain("No tool is chosen to measure 'paths_through'", "in go", "config.json"))
        with and_("its fix says to choose a tool for that measure and language, record it in the config's code measures, and install it"):
            expect(self.refused).to(contain("Fix: choose a tool that takes 'paths_through' in go", '"code_measures": "tools": "paths_through": "go"', "and install it"))
    with scenario("Report a chosen tool that is not installed"):
        with given("the shop project's config chooses lizard for a Python function's paths"):
            pass  # the shipped table chooses it
        with and_("lizard is not installed"):
            self.shop = shop_project(tools={"lizard": LizardNotInstalled})
        with when("the code measures of `shop/cart.py` are taken"):
            self.shop.practice.reading.keep_code_measures(code_files(self.shop))
            self.reported = reports_of(self.shop, "limit-paths-through-a-function")
        with then("limit-paths-through-a-function reports the file once, naming the tool lizard and the measure"):
            expect(self.reported).to(have_len(1))
            expect(self.reported[0]).to(contain("'lizard'", "'paths_through'", "is not installed"))
        with and_("its fix says to install the tool the config names, with the command"):
            expect(self.reported[0]).to(contain("Fix: install lizard, the tool .context/config.json names for this measure, with: pip install", 'pip install -e ".[measures]"'))
    with scenario("Leave out a measure the project says is not measured"):
        with given("the shop project's config writes `not measured` for copied code blocks in Python"):
            self.shop = shop_project(config=NOT_MEASURING_COPIES, files={CART_FILE: CART, **SHOP_CARD})
        with when("the code measures of `shop/cart.py` are taken"):
            self.shop.practice.reading.keep_code_measures(code_files(self.shop))
        with then("the node of the module shop holds no copied_code_blocks"):
            expect(node_of(self.shop, "Module", "shop").has_fact("copied_code_blocks")).to(be_false)
        with and_("no rule reports the measure as not taken"):
            expect(node_of(self.shop, "Module", "shop").has_fact("copied_code_blocks_not_taken")).to(be_false)
    with scenario("Take no measure in a project that chose no tools"):
        with given("the shop project's config has no `code_measures` section"):
            self.shop = shop_project(config=NO_MEASURES_CHOSEN)
        with when("Claude Code validates clean-engineering-code on `shop/cart.py`"):
            self.checked = checked_graph_file()
            self.shop.practice.reading.graph.reads.refreshed([CART_FILE], self.checked)
        with then("no node holds a code measure"):
            expect(any_measure_kept(self.shop)).to(be_false)
        with and_("the validate reports the other rules as before"):
            expect([violation.rule for violation in SavedGraph.from_file(self.checked).violations(["clean_engineering"])]).to(contain("missing-module-context"))
