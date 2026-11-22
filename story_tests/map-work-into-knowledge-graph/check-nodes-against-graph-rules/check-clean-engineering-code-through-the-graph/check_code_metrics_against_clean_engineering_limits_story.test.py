# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Check Code Metrics Against Clean Engineering Limits, run on the domain objects: the shop project's nodes holding
# their measures, and the graph rules that read them. The outside tools are stood in for
# (measures/examples/code_measures_examples.py); code_measures_heavy_spec.py runs the real ones.

from __future__ import annotations

from expects import contain, equal, expect

from cdd_guidance.practices.clean_engineering.measures.examples.code_measures_examples import (
    NO_MEASURES_CHOSEN,
    PARCEL_FILE,
    PATHS_LIMIT_OF_20,
    READER_ALONE,
    SIX_PARAMETERS,
    checked_graph_file,
    code_files,
    example_pair,
    holding,
    metrics_under,
    node_of,
    shop_project,
)
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.rule_examples import MEASURES_CHOSEN
from harness.graph.saved_graph import SavedGraph
from story_test import and_, given, scenario, story, then, when

# Epic: Map Work Into Knowledge Graph
# Sub-epic: Check Clean Engineering Code Through The Graph
# Map: ../../../../.context/story-map.md#ssystem-validate----check-code-metrics-against-clean-engineering-limits
# Scenarios: check_code_metrics_against_clean_engineering_limits_story.test.md

# Outline: the node, the fact its measure is read from, a value one past the limit, the rule, and the rule's words.
_PAST_THE_LIMIT = (
    ("Operation", "total", "paths_through", 11, "limit-paths-through-a-function", "has 11 paths through it (cyclomatic complexity), over the limit of 10."),
    ("Operation", "total", "readability_score", 16, "keep-functions-readable", "a readability score of 16 (cognitive complexity; higher is harder to read), over the limit of 15."),
    ("Operation", "total", "line_count", 51, "limit-function-lines", "has 51 lines, over the limit of 50."),
    ("OoadClass", "Cart", "total_complexity", 101, "limit-class-complexity", "has a total complexity of 101 (the paths through all its methods, added up), over the limit of 100."),
    ("OoadClass", "Cart", "method_count", 31, "limit-class-methods", "has 31 methods, over the limit of 30."),
)
# Outline: the rules whose measure the practice's own reader takes, so their examples need no outside tool.
_READ_BY_THE_READER = ("limit-function-lines", "limit-class-methods", "keep-class-methods-sharing-data")

with story("Check Code Metrics Against Clean Engineering Limits"):
    with scenario("Report a node whose measure is past its limit"):
        with given("the node of <node> holds <measure> <value>"):
            self.shops = [holding(shop_project(), kind, name, fact, value) for kind, name, fact, value, _rule, _words in _PAST_THE_LIMIT]
        with when("the graph rules run"):
            # InGraph.check -> CodeMeasureLimit.check_production -> CodeMeasure.value_on, ChosenTools.limit
            self.reported = [shop.hits(BY_SLUG[case[4]]) for shop, case in zip(self.shops, _PAST_THE_LIMIT)]
        with then('<rule> reports it, saying "<words>"'):
            expect([any(case[5] in said for said in reported) for reported, case in zip(self.reported, _PAST_THE_LIMIT)]).to(equal([True] * len(_PAST_THE_LIMIT)))
    with scenario("Pass a node whose measure is at its limit"):
        with given("the node of the function total holds paths_through 10"):
            self.shop = holding(shop_project(), "Operation", "total", "paths_through", 10)
        with when("the graph rules run"):
            self.reported = self.shop.hits(BY_SLUG["limit-paths-through-a-function"])
        with then("limit-paths-through-a-function reports nothing"):
            expect(self.reported).to(equal([]))
    with scenario("Pass a node no read measured"):
        with given("the node of the function total holds no paths_through"):
            self.shop = shop_project()
        with when("the graph rules run"):
            self.reported = self.shop.hits(BY_SLUG["limit-paths-through-a-function"])
        with then("limit-paths-through-a-function reports nothing"):
            expect(self.reported).to(equal([]))
    with scenario("Hold a measure to the limit the project sets"):
        with given("the shop project's config sets the limit of paths_through to 20"):
            self.shop = shop_project(config=PATHS_LIMIT_OF_20)
        with and_("the node of the function total holds paths_through 14"):
            holding(self.shop, "Operation", "total", "paths_through", 14)
        with when("the graph rules run"):
            self.reported = self.shop.hits(BY_SLUG["limit-paths-through-a-function"])
        with then("limit-paths-through-a-function reports nothing"):
            expect(self.reported).to(equal([]))
    with scenario("Hold an operation's parameters to one limit of 3, in a project that measures its code or not"):
        with given("`src/parcels/parcel.py` holds the function send, which takes six parameters, in a project whose config has a `code_measures` section and in one whose config has none"):
            self.projects = [shop_project(config=config, files={PARCEL_FILE: SIX_PARAMETERS}) for config in (MEASURES_CHOSEN, NO_MEASURES_CHOSEN)]
        with when("the graph rules run"):
            # InGraph.check -> LimitOperationParameters.measure -> most_parameters
            self.reported = [project.hits(BY_SLUG["limit-operation-parameters"]) for project in self.projects]
        with then('limit-operation-parameters reports send in both, saying "takes 6 parameters (maximum 3, excluding self)"'):
            expect(self.reported).to(equal([["Operation 'send' takes 6 parameters (maximum 3, excluding self)."]] * 2))
        with and_("the metrics group under send shows its parameters with the limit 3, past the limit"):
            expect(metrics_under(self.projects[0], "Operation", "send")).to(contain("parameters a function takes: 6, limit 3, past the limit"))
    with scenario("Report a rule's failing example and pass its repaired example"):
        # The three rules whose measure lizard supplies are run with the real lizard by code_measures_heavy_spec.py.
        with given("the failing example and the repaired example of <rule>"):
            self.pairs = [example_pair(rule, READER_ALONE) for rule in _READ_BY_THE_READER]
        with when("the code measures of each are taken and the graph rules run"):
            for pair in self.pairs:
                for example in (pair.faulty, pair.repaired):
                    example.practice.reading.keep_code_measures(code_files(example))
        with then("<rule> reports the failing example"):
            expect([bool(pair.faulty.hits(pair.rule)) for pair in self.pairs]).to(equal([True] * len(self.pairs)))
        with and_("it reports nothing in the repaired example"):
            expect([pair.repaired.hits(pair.rule) for pair in self.pairs]).to(equal([[]] * len(self.pairs)))
    with scenario("Report a function past its limit in the validation report"):
        with given("the parcels project's config has a `code_measures` section"):
            pass
        with and_("`src/parcels/parcel.py` holds the function send, which takes six parameters"):
            self.parcels = shop_project(files={PARCEL_FILE: SIX_PARAMETERS})
        with when("Claude Code validates clean-engineering-code on `src/parcels/parcel.py`"):
            # Validate -> GraphReads.refreshed, which checks every rule on the file and saves what the report reads
            self.checked = checked_graph_file()
            self.parcels.practice.reading.graph.reads.refreshed([PARCEL_FILE], self.checked)
        with then('the report holds the limit-operation-parameters violation "takes 6 parameters (maximum 3, excluding self)" in `src/parcels/parcel.py`, beside the other rules'):
            found = [(violation.rule, violation.location) for violation in SavedGraph.from_file(self.checked).violations(["clean_engineering"]) if "takes 6 parameters (maximum 3, excluding self)" in str(violation.message)]
            expect([(rule, PARCEL_FILE in str(location).replace("\\", "/")) for rule, location in found]).to(equal([("limit-operation-parameters", True)]))
        with and_("the node of send is the one reported"):
            expect(node_of(self.parcels, "Operation", "send").failed_rules).to(contain("limit-operation-parameters"))
