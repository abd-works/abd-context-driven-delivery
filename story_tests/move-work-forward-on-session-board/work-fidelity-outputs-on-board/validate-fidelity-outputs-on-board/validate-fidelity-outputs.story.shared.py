"""Validate Fidelity Outputs: the shared scenarios the Python tiers replay.

Scenarios: story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md.
Map: .context/story-map.md#e-validate-fidelity-outputs. Model: .context/kanban-model.md.

Steps reach the board, the session, and the Validate action only through the namespace a tier hands them
(`world.Ticket`, `world.Validate`, `world.sessions`), so the domain spec and the cdd tools spec replay the same steps.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: Display Violations Band (both: board-page-view.tsx draws the band); Fix Report Violations (all four: the
board app writes the fix message, and reads an open report again after a tool call); Open Validation Report "Open a
violation's file at its line" (the files panel marks the line); Validate Fidelity "Send the fidelity to validate" (the
board app writes the command) and "Keep Validate off with nothing to check".
"""

from __future__ import annotations

import re

import json

from expects import contain, equal, expect, raise_error

from cdd_guidance.practices.stories.stories import Stories
from space.kanban.session_board_examples import (
    BILLING_REPORT,
    CHECKOUT_FLOW,
    ENTITY_ROOT_FILE,
    PET_VISITS,
    STORY_FILE,
    STORY_MAP,
    STORY_MAP_FILE,
    STORY_MAP_GRAPH,
    STORY_MAP_REPORT,
    STORY_MAP_TEXT,
    ReportSeed,
    generated,
    saved_graph,
    saved_practice,
    seed_checkout_flow_held_on_violations,
    seed_checkout_flow_open,
)
from space.kanban.story_test import SharedStories, expect_action, expect_held_on_violations, progress_in
from harness.graph.saved_graph import SavedGraph

shared_stories = SharedStories("Validate Fidelity Outputs")

REPORTS = f".sessions/{CHECKOUT_FLOW.name}/validation-reports"
REPORT_WITHOUT_GRAPH = ReportSeed(STORY_MAP_REPORT, text="### verb-noun-format: 1 violation(s)\n")
# A graph saved before the saved graph's shape had a version, as every report saved before shape 2 holds it.
REPORT_WITH_OUTDATED_GRAPH = ReportSeed(STORY_MAP_REPORT, graph={key: value for key, value in STORY_MAP_GRAPH.items() if key != "version"})
EARLIER_TACTICS_GRAPH =f"{REPORTS}/ddd-tactics-20200101T000000.json"
EARLIER_TACTICS_GRAPH_TEXT = "[]"
# Validate dates each report by the clock, so a report's name is matched, not spelled out.
TACTICS_REPORT_NAME = re.compile(r"^ddd-tactics-\d{8}T\d{6}\.md$")
ACCEPTED_FILE = ".context/violations-accepted.json"
# The one hit of checkout-flow's story map report, as the report panel shows it and sends it back to accept it.
STORY_MAP_HIT = {"rule": "verb-noun-format", "message": "Name the story with a verb", "location": STORY_MAP_FILE, "line": 6, "node_id": "node-1"}
# A later validate of the story map that finds the same rule on the same node, saying something else.
REWORDED_REPORT = ReportSeed(
    "stories-story-map-20261101T120000",
    graph=saved_graph(saved_practice("stories", "node-1", STORY_MAP_FILE, 6, ("verb-noun-format", "Name the story with a verb and a noun"))),
)
# The story map's report with no graph hit and the judgment the validating agent adds: one rule failed on line 7.
JUDGED_FINDING = {"rule": "do-not-invent-requirements", "message": "`Confirm Order`: no source names this story.", "location": STORY_MAP_FILE, "line": 7, "node_id": ""}
JUDGED_REPORT = ReportSeed(
    STORY_MAP_REPORT,
    text="# Graph rule validation\n\n## Judgment — `.context/story-map.md`\n\n### `do-not-invent-requirements` — Fail\n- story-map.md:7 `Confirm Order`: no source names this story.\n",
    graph=saved_graph(saved_practice("stories", "node-1", STORY_MAP_FILE, 6)),
)
UNREADABLE_ACCEPTED = "{ accepted: ["


def seed_checkout_flow_with_outdated_report(project) -> None:
    """checkout-flow held on violations, its latest story map report saved with a graph from before shape 2."""
    project.seed_file(STORY_MAP_FILE, STORY_MAP_TEXT)
    project.seed_session(CHECKOUT_FLOW)
    project.seed_report(CHECKOUT_FLOW, REPORT_WITH_OUTDATED_GRAPH)


@shared_stories.scenario("Validate Fidelity", "Count Validate done only with no graph-rule violations")
def _(s):
    @s.given("pet-visits' story map is generated")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map")))
        world.session = world.sessions.held.load(world.project.sessions / PET_VISITS.name)
        world.stories = world.session.practice("stories").fidelities["story_map"].session_output

    @s.when("Claude Code validates the story map and finds no graph-rule violation")
    def _(world):
        world.session.log.by(None).validation(world.stories, [])

    @s.then("the session log ends with validate Stories story_map")
    def _(world):
        last = (world.project.sessions / PET_VISITS.name / "session.log").read_text(encoding="utf-8").splitlines()[-1]
        expect((last.split()[1:4], "graph-rule" in last)).to(equal((["validate", "Stories", "story_map"], False)))

    # A ticket reads its session's log once per read, as the board reads it afresh each time it draws the tile.
    @s.and_("the story_map tile marks Validate ✓")
    def _(world):
        expect_action(world.data_of(world.Ticket.load(PET_VISITS.name)), STORY_MAP, "validate", "done")

    @s.when("Claude Code validates it again and finds actor-named-in-step on map.md line 12")
    def _(world):
        world.session.log.by(None).validation(world.stories, ["graph-rule actor-named-in-step map.md:12"])

    @s.then("the session log ends with validate Stories story_map graph-rule actor-named-in-step map.md:12")
    def _(world):
        last = (world.project.sessions / PET_VISITS.name / "session.log").read_text(encoding="utf-8").splitlines()[-1]
        expect(last).to(contain(" validate Stories story_map graph-rule actor-named-in-step map.md:12"))

    @s.and_("the story_map tile marks Validate as violations again")
    def _(world):
        expect_held_on_violations(world.data_of(world.Ticket.load(PET_VISITS.name)), STORY_MAP)


@shared_stories.scenario("Validate Fidelity", "Allow Validate again on the same output")
def _(s):
    @s.given("checkout-flow's story map has violations")
    def _(world):
        seed_checkout_flow_held_on_violations(world.project)

    @s.when("the session board reads checkout-flow")
    def _(world):
        world.read = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name))

    @s.then("validate is on for story_map")
    def _(world):
        expect(progress_in(world.read, STORY_MAP)["allowed_actions"]).to(contain("validate"))


@shared_stories.scenario("Save Validation Report", "Save the report and the graph it checked")
def _(s):
    @s.given("the session checkout-flow has an entity root with a private-method-naming violation")
    def _(world):
        world.project.seed_graph_example(ENTITY_ROOT_FILE)
        seed_checkout_flow_open(world.project)

    @s.when("Claude Code validates ddd-tactics on that file")
    def _(world):
        world.reply = world.Validate().validate(guidance=["ddd-tactics"], paths=[ENTITY_ROOT_FILE])
        world.reports = sorted((world.project.root / REPORTS).glob("ddd-tactics-*.md"))

    @s.then("the validation report is saved as validation-reports/ddd-tactics-20261101T100000.md naming private-method-naming")
    def _(world):
        saved = [(bool(TACTICS_REPORT_NAME.match(path.name)), "private-method-naming" in path.read_text(encoding="utf-8")) for path in world.reports]
        expect(saved).to(equal([(True, True)]))

    @s.and_("the graph it checked is saved beside it as ddd-tactics-20261101T100000.json, with the rule hits on its nodes")
    def _(world):
        hits = [hit.rule for hit in SavedGraph.from_file(world.reports[0].with_suffix(".json")).violations(["ddd"])]
        expect(hits).to(contain("private-method-naming"))

    @s.and_("Claude Code's reply says where the report is saved")
    def _(world):
        expect(str(world.reply)).to(contain(str(world.reports[0])))


@shared_stories.scenario("Save Validation Report", "Save one report for each listed guidance")
def _(s):
    @s.given("the session checkout-flow has edited files for ddd-tactics and stories-scenarios")
    def _(world):
        world.project.seed_graph_example(ENTITY_ROOT_FILE)
        world.project.seed_graph_example(STORY_FILE)
        seed_checkout_flow_open(world.project)

    @s.when("Claude Code validates ddd-tactics and stories-scenarios together")
    def _(world):
        world.Validate().validate(guidance=["ddd-tactics", "stories-scenarios"], paths=[ENTITY_ROOT_FILE, STORY_FILE])

    @s.then("validation-reports holds one stories-scenarios report and one ddd-tactics report")
    def _(world):
        reports = world.project.root / REPORTS
        expect((len(list(reports.glob("stories-scenarios-*.md"))), len(list(reports.glob("ddd-tactics-*.md"))))).to(equal((1, 1)))


@shared_stories.scenario("Save Validation Report", "Leave an earlier report's graph as it was")
def _(s):
    @s.given("validation-reports holds ddd-tactics-20200101T000000.json")
    def _(world):
        world.project.seed_graph_example(ENTITY_ROOT_FILE)
        seed_checkout_flow_open(world.project)
        world.project.seed_file(EARLIER_TACTICS_GRAPH, EARLIER_TACTICS_GRAPH_TEXT)

    @s.when("Claude Code validates ddd-tactics again")
    def _(world):
        world.Validate().validate(guidance=["ddd-tactics"], paths=[ENTITY_ROOT_FILE])

    @s.then("ddd-tactics-20200101T000000.json is unchanged")
    def _(world):
        expect((world.project.root / EARLIER_TACTICS_GRAPH).read_text(encoding="utf-8")).to(equal(EARLIER_TACTICS_GRAPH_TEXT))


@shared_stories.scenario("Open Validation Report", "Open a fidelity's latest report")
def _(s):
    @s.given("checkout-flow's story map has the validation report stories-story-map-20261101T100000.md with its saved graph")
    def _(world):
        seed_checkout_flow_held_on_violations(world.project)

    @s.and_("the graph names verb-noun-format on .context/story-map.md line 6")
    def _(world):
        # The graph saved with the report above, STORY_MAP_GRAPH, holds that one hit.
        pass

    @s.when("the Person opens checkout-flow's story_map report")
    def _(world):
        world.report = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).report())

    @s.then("the report panel shows .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md")
    def _(world):
        expect(world.report["path"]).to(equal(f"{REPORTS}/{STORY_MAP_REPORT}.md"))

    @s.and_("it lists verb-noun-format with one violation at .context/story-map.md line 6 and the source lines around it")
    def _(world):
        listed = [(rule["rule"]["slug"], [(violation["location"], violation["line"], {"number": 6, "text": "- Handle Payment"} in violation["source"]) for violation in rule["violations"]]) for rule in world.report["rules"]]
        expect(listed).to(equal([("verb-noun-format", [(STORY_MAP_FILE, 6, True)])]))


@shared_stories.scenario("Open Validation Report", "Show every fidelity's violations at once")
def _(s):
    @s.given("checkout-flow has violations")
    def _(world):
        seed_checkout_flow_held_on_violations(world.project)

    @s.when("the Person opens checkout-flow's violations from its card")
    def _(world):
        world.report = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).violations())

    @s.then("the report panel shows .sessions/checkout-flow/validation-reports with every rule broken, each naming its fidelity")
    def _(world):
        expect((world.report["path"], [(rule["fidelity"]["slug"], rule["rule"]["slug"]) for rule in world.report["rules"]])).to(equal((REPORTS, [(STORY_MAP, "verb-noun-format")])))


@shared_stories.scenario("Open Validation Report", "Say a report has no saved graph")
def _(s):
    @s.given("the ticket's latest story_map report has no graph saved beside it")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_report(CHECKOUT_FLOW, REPORT_WITHOUT_GRAPH)

    @s.when("the Person opens the story_map report")
    def _(world):
        world.report = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).report())

    @s.then("the report panel shows the report's text")
    def _(world):
        expect(world.report["text"]).to(equal(REPORT_WITHOUT_GRAPH.text))

    @s.and_("it says the report has no saved graph in place of saying it has no violations")
    def _(world):
        expect((world.report["has_saved_graph"], world.report["rules"])).to(equal((False, [])))


@shared_stories.scenario("Open Validation Report", "Say a report's saved graph is out of date")
def _(s):
    @s.given("checkout-flow's latest story_map report has a graph saved in a shape the graph no longer writes")
    def _(world):
        seed_checkout_flow_with_outdated_report(world.project)

    @s.when("the Person opens the story_map report")
    def _(world):
        world.report = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).report())

    @s.then("the report panel shows the report's text")
    def _(world):
        expect(world.report["text"]).to(equal(REPORT_WITH_OUTDATED_GRAPH.text))

    @s.and_("it says the report's saved graph is out of date in place of its graph's rules")
    def _(world):
        expect((world.report["is_out_of_date"], world.report["rules"])).to(equal((True, [])))


@shared_stories.scenario("Open Validation Report", "Read the board with an out-of-date report")
def _(s):
    @s.given("checkout-flow's latest story_map report has a graph saved in a shape the graph no longer writes")
    def _(world):
        seed_checkout_flow_with_outdated_report(world.project)

    @s.when("the session board reads checkout-flow")
    def _(world):
        world.read = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name))

    @s.then("the story_map bar links that report")
    def _(world):
        expect(progress_in(world.read, STORY_MAP)["report_file"]).to(equal(f"{REPORTS}/{STORY_MAP_REPORT}.md"))


@shared_stories.scenario("Open Validation Report", "Say there is no report")
def _(s):
    @s.given("billing-report has no validation report")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the session board reads billing-report")
    def _(world):
        world.read = world.data_of(world.Ticket.load(BILLING_REPORT.name))

    @s.then("the story_map bar shows no report link")
    def _(world):
        expect(progress_in(world.read, STORY_MAP)["report_file"]).to(equal(""))


def accepted_in(project) -> list[dict]:
    """Each acceptance the project's violations-accepted.json keeps."""
    return json.loads((project.root / ACCEPTED_FILE).read_text(encoding="utf-8"))["accepted"]


def story_map_report(world) -> dict:
    """checkout-flow's story_map report as the report panel reads it."""
    return world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).report())


def listed_in(report: dict, kind: str = "rules") -> list[tuple[str, int]]:
    """Each rule of report's open rules, or of its accepted ones, with how many violations it lists."""
    return [(rule["rule"]["slug"], len(rule["violations"])) for rule in report[kind]]


def seed_story_map_hit_accepted(world) -> None:
    """checkout-flow held on its story map's one violation, which the Person accepted on the report."""
    seed_checkout_flow_held_on_violations(world.project)
    world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).accept_violation(**STORY_MAP_HIT)


@shared_stories.scenario("Accept Report Violation", "Accept a violation as it is")
def _(s):
    @s.given("checkout-flow's story_map report lists verb-noun-format at .context/story-map.md line 6, on the story node-1, saying Name the story with a verb")
    def _(world):
        seed_checkout_flow_held_on_violations(world.project)

    @s.when("the Person accepts that violation")
    def _(world):
        world.report = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).accept_violation(**STORY_MAP_HIT))

    @s.then(".context/violations-accepted.json keeps verb-noun-format on node-1 with the message Name the story with a verb")
    def _(world):
        kept = [(entry["rule"], entry["node_id"], entry["message"]) for entry in accepted_in(world.project)]
        expect(kept).to(equal([("verb-noun-format", "node-1", "Name the story with a verb")]))

    @s.and_("the story_map report lists no rules and says it leaves out 1 accepted violation")
    def _(world):
        report = story_map_report(world)
        expect((world.report["rules"], report["rules"], report["violation_count"], report["accepted_count"], listed_in(report, "accepted"))).to(
            equal(([], [], 0, 1, [("verb-noun-format", 1)]))
        )

    @s.and_("the story_map tile marks Validate ✓ with no violations")
    def _(world):
        progress = progress_in(world.data_of(world.Ticket.load(CHECKOUT_FLOW.name)), STORY_MAP)
        expect((progress["actions"]["validate"], progress["state"], progress["has_violations"], progress["violation_count"])).to(equal(("done", "done", False, 0)))


@shared_stories.scenario("Accept Report Violation", "Leave an accepted violation out of the next validation")
def _(s):
    @s.given("the session checkout-flow has an entity root with a private-method-naming violation")
    def _(world):
        world.project.seed_graph_example(ENTITY_ROOT_FILE)
        seed_checkout_flow_open(world.project)

    @s.and_("Claude Code validated ddd-tactics on that file")
    def _(world):
        world.first = str(world.Validate().validate(guidance=["ddd-tactics"], paths=[ENTITY_ROOT_FILE]))

    @s.and_("the Person accepted every private-method-naming violation of the ddd-tactics report")
    def _(world):
        progress = world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of("ddd-tactics")
        rule = next(rule for rule in world.data_of(progress.report())["rules"] if rule["rule"]["slug"] == "private-method-naming")
        world.accepted = rule["violations"]
        for violation in world.accepted:
            progress.accept_violation(**{name: violation[name] for name in ("rule", "message", "location", "line", "node_id")})

    @s.when("Claude Code validates ddd-tactics on that file again")
    def _(world):
        world.again = str(world.Validate().validate(guidance=["ddd-tactics"], paths=[ENTITY_ROOT_FILE]))
        world.saved = sorted((world.project.root / REPORTS).glob("ddd-tactics-*.md"))[-1].read_text(encoding="utf-8")

    @s.then("the validation report names no private-method-naming violation")
    def _(world):
        named = [any(violation["message"] in text for violation in world.accepted) for text in (world.first, world.again, world.saved)]
        expect(named).to(equal([True, False, False]))

    @s.and_("it says how many accepted violations it leaves out, kept in .context/violations-accepted.json")
    def _(world):
        expect(world.saved).to(contain(f"**Accepted violations left out:** {len(world.accepted)}"))
        expect(world.saved).to(contain(ACCEPTED_FILE))

    @s.and_("the session log's validate line names no private-method-naming violation")
    def _(world):
        last = [line for line in (world.project.sessions / CHECKOUT_FLOW.name / "session.log").read_text(encoding="utf-8").splitlines() if " validate " in line][-1]
        expect("graph-rule private-method-naming" in last).to(equal(False))


@shared_stories.scenario("Accept Report Violation", "Show an accepted violation again once its finding changes")
def _(s):
    @s.given("the Person accepted verb-noun-format on node-1 saying Name the story with a verb")
    def _(world):
        seed_story_map_hit_accepted(world)

    @s.when("Claude Code validates the story map again and finds verb-noun-format on node-1 saying Name the story with a verb and a noun")
    def _(world):
        world.project.seed_report(CHECKOUT_FLOW, REWORDED_REPORT)

    @s.then("the story_map report lists verb-noun-format with one violation again")
    def _(world):
        report = story_map_report(world)
        expect((listed_in(report), report["accepted_count"])).to(equal(([("verb-noun-format", 1)], 0)))

    @s.and_("the story_map tile marks Validate as violations")
    def _(world):
        expect_held_on_violations(world.data_of(world.Ticket.load(CHECKOUT_FLOW.name)), STORY_MAP)


@shared_stories.scenario("Accept Report Violation", "Accept a judged finding on a line of a file")
def _(s):
    @s.given("checkout-flow's story_map report's judgment fails do-not-invent-requirements at story-map.md line 7, which reads - Confirm Order")
    def _(world):
        world.project.seed_file(STORY_MAP_FILE, STORY_MAP_TEXT)
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_report(CHECKOUT_FLOW, JUDGED_REPORT)

    @s.when("the Person accepts that finding")
    def _(world):
        world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).accept_violation(**JUDGED_FINDING)

    @s.then(".context/violations-accepted.json keeps do-not-invent-requirements on .context/story-map.md with the judged content - Confirm Order and no line number")
    def _(world):
        kept = [(entry["rule"], entry["file"], entry["content"], "line" in entry) for entry in accepted_in(world.project)]
        expect(kept).to(equal([("do-not-invent-requirements", STORY_MAP_FILE, "- Confirm Order", False)]))

    @s.and_("the story_map report lists no rules")
    def _(world):
        report = story_map_report(world)
        expect((report["rules"], report["accepted_count"])).to(equal(([], 1)))


@shared_stories.scenario("Accept Report Violation", "Take an acceptance back")
def _(s):
    @s.given("the Person accepted verb-noun-format on node-1 saying Name the story with a verb")
    def _(world):
        seed_story_map_hit_accepted(world)

    @s.and_("the story_map report lists that violation among the accepted ones")
    def _(world):
        world.accepted = story_map_report(world)["accepted"][0]["violations"][0]

    @s.when("the Person takes that acceptance back")
    def _(world):
        asked = {name: world.accepted[name] for name in ("rule", "message", "location", "line", "node_id")}
        world.report = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).work.progress_of(STORY_MAP).reopen_violation(**asked))

    @s.then("the story_map report lists verb-noun-format with one violation again")
    def _(world):
        expect((listed_in(world.report), listed_in(story_map_report(world)), world.report["accepted_count"])).to(
            equal(([("verb-noun-format", 1)], [("verb-noun-format", 1)], 0))
        )

    @s.and_(".context/violations-accepted.json keeps no acceptance")
    def _(world):
        expect(accepted_in(world.project)).to(equal([]))


@shared_stories.scenario("Accept Report Violation", "Refuse accepted violations that are not readable JSON")
def _(s):
    @s.given("checkout-flow's story map has violations")
    def _(world):
        seed_checkout_flow_held_on_violations(world.project)

    @s.and_(".context/violations-accepted.json is not readable JSON")
    def _(world):
        world.project.seed_file(ACCEPTED_FILE, UNREADABLE_ACCEPTED)

    @s.when("the Person opens checkout-flow's story_map report")
    def _(world):
        world.opening = lambda: story_map_report(world)

    @s.then("the report is refused, naming .context/violations-accepted.json and how to repair it")
    def _(world):
        expect(world.opening).to(raise_error(Exception, contain("violations-accepted.json", "Repair it")))

    @s.and_("the file is left as it was")
    def _(world):
        expect((world.project.root / ACCEPTED_FILE).read_text(encoding="utf-8")).to(equal(UNREADABLE_ACCEPTED))
