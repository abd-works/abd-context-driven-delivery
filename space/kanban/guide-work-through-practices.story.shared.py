"""Guide Work Through Practices: the shared scenarios the Python tiers replay.

Scenarios: move-work-forward-on-session-board/guide-work-through-practices/*/*_story.test.py.
Map: .context/story-map.md#e-guide-work-through-practices. Model: .context/kanban-model.md.

Steps reach the board only through the World a tier hands them (`world.Ticket`, `world.Board`), so the domain spec
and the cdd tools spec replay the same steps. A fidelity's tile reads its Generate, Validate, and Review from the
ticket's `actions`, and its segment colour from the ticket's `progress`, so the Thens assert those.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: Open Practice Tile (all five); Send Action To Stage Practices (both); Add Active Ticket To System Prompt
(all three: the cdd-board mod composes the prompt); Choose Ticket Practices "Keep practice switches off on a locked
ticket"; Send Next Fidelity Action "Fill the prompt to validate" (the board app fills the prompt) and "Keep Run next
off where it cannot run". The Thens of the scenarios below that only the page shows (a toast, a tile that closes and
fades, an open tile) are left to those specs too.
"""

from __future__ import annotations

import json

from expects import be_false, equal, expect

from space.kanban.session_board_examples import (
    BILLING_REPORT,
    CHECKOUT_FLOW,
    DISCOVERY_FIDELITY_SLUGS,
    EVERY_DISCOVERY_FIDELITY_REVIEWED,
    GENERATED_STORY_MAP_IN_TWO_FOLDERS,
    MOVED_INTO_SPECIFICATION,
    PET_VISITS,
    READY_TO_MOVE,
    STORY_MAP,
    STORY_MAP_REPORT,
    STORY_MAP_REVIEWED,
    STORY_MAP_VALIDATED_CLEAN,
    generated,
    seed_checkout_flow_held_on_violations,
    validated,
)
from space.kanban.story_test import SharedStories, column_in, expect_action, expect_actions, expect_held_on_violations, expect_no_next, expect_placed, next_in, progress_in

shared_stories = SharedStories("Guide Work Through Practices")

FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"


@shared_stories.scenario("Display Fidelity Progress", "Show Generate done")
def _(s):
    @s.given("pet-visits' session log has generate /work, /work/docs stories story_map markdown stories")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(GENERATED_STORY_MAP_IN_TWO_FOLDERS))

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("the story_map tile marks Generate ✓ and Validate and Review ○")
    def _(world):
        expect_actions(world.read, STORY_MAP, generate="done", validate="to_do", review="to_do")


@shared_stories.scenario("Display Fidelity Progress", "Show violations held on Validate")
def _(s):
    @s.given("pet-visits' story_map is generated")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map")))

    @s.and_("its latest validate line is validate Stories story_map graph-rule actor-named-in-step map.md:12")
    def _(world):
        world.project.seed_log_line(PET_VISITS, validated("Stories", "story_map", "graph-rule actor-named-in-step map.md:12"))

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("the story_map tile marks Validate as violations and its segment shows in the violations colour")
    def _(world):
        expect_held_on_violations(world.read, STORY_MAP)

    @s.and_("Review stays to do")
    def _(world):
        expect_action(world.read, STORY_MAP, "review", "to_do")


@shared_stories.scenario("Display Fidelity Progress", "Show Validate done after a clean validate")
def _(s):
    @s.given("pet-visits' story_map is generated")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map")))

    @s.and_("its latest validate line is validate Stories story_map with no graph-rule")
    def _(world):
        world.project.seed_log_line(PET_VISITS, validated("Stories", "story_map"))

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("the story_map tile marks Generate ✓, Validate ✓, and Review ○")
    def _(world):
        expect_actions(world.read, STORY_MAP, generate="done", validate="done", review="to_do")


@shared_stories.scenario("Display Fidelity Progress", "Show each fidelity of the stage on the ticket")
def _(s):
    @s.given("billing-report has nothing recorded in its session log")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the session board reads billing-report")
    def _(world):
        world.read = world.data_of(world.Ticket.load(BILLING_REPORT.name))

    @s.then("each Discovery tile marks Generate, Validate, and Review ○, its segment dim")
    def _(world):
        tiles = {slug: (progress_in(world.read, slug)["actions"], progress_in(world.read, slug)["state"]) for slug in DISCOVERY_FIDELITY_SLUGS}
        expect(tiles).to(equal(dict.fromkeys(DISCOVERY_FIDELITY_SLUGS, ({"generate": "to_do", "validate": "to_do", "review": "to_do"}, "not_started"))))


@shared_stories.scenario("Choose Ticket Practices", "Turn a practice off for a ticket")
def _(s):
    @s.given("checkout-flow is the active ticket working on every practice")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("the Person turns DDD off for checkout-flow")
    def _(world):
        world.chosen = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).session.practice("ddd").enable(is_enabled=False))

    @s.then("a toast says DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json")
    def _(world):
        saved = json.loads((world.project.root / world.chosen["session_file"]).read_text(encoding="utf-8"))
        expect((world.chosen["session_file"], saved["practices"]["ddd"])).to(equal((".sessions/checkout-flow/session.json", {"enabled": False})))

    @s.and_("the card shows no DDD segment")
    def _(world):
        expect(world.data_of(world.Ticket.load(CHECKOUT_FLOW.name))["session"]["practices"]["ddd"]["enabled"]).to(be_false)


@shared_stories.scenario("Choose Ticket Practices", "Finish a stage on the practices left on")
def _(s):
    @s.given("pet-visits has generated, validated, and reviewed the story_map fidelity")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(*STORY_MAP_REVIEWED))

    @s.and_("every practice but Stories is turned off for pet-visits")
    def _(world):
        turned_off = {"enabled": False}
        world.project.seed_session_fields(PET_VISITS, practices={name: turned_off for name in ("ddd", "ux", "clean_engineering", "bdd")})

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("pet-visits shows in Discovery's Done")
    def _(world):
        expect_placed(world.read, "Discovery", is_done=True)


@shared_stories.scenario("Mark Ticket Done In Stage", "Mark a ticket done in its stage")
def _(s):
    @s.given("the ticket pet-visits is In progress in Discovery with only its story map generated")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map")))

    @s.when("the Person marks pet-visits done in Discovery")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(PET_VISITS.name).move_next())

    @s.then("pet-visits shows in Discovery's Done")
    def _(world):
        expect_placed(world.moved, "Discovery", is_done=True)

    @s.and_("it has no next step")
    def _(world):
        expect_no_next(world.moved)


@shared_stories.scenario("Mark Ticket Done In Stage", "Mark a ticket back in progress")
def _(s):
    @s.given("the ticket ready-to-move is in Discovery's Done")
    def _(world):
        world.project.seed_session(READY_TO_MOVE)

    @s.when("the Person moves ready-to-move back into Discovery's In progress")
    def _(world):
        world.moved = world.data_of(world.Ticket.load(READY_TO_MOVE.name).move_to(stage="Discovery"))

    @s.then("ready-to-move shows In progress in Discovery")
    def _(world):
        expect_placed(world.moved, "Discovery", is_done=False)


@shared_stories.scenario("Open Help", "Open a fidelity's help")
def _(s):
    @s.given("billing-report's story_map tile is shown")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person opens help on the story_map fidelity")
    def _(world):
        world.help = world.data_of(world.Ticket.load(BILLING_REPORT.name).work.progress_of(STORY_MAP).help())

    @s.then("a side panel shows story_map's overview, guidance, and rules such as verb-noun-format")
    def _(world):
        fidelity = world.help["fidelity"]
        slugs = [rule["slug"] for rule in fidelity["rules"]]
        expect((bool(fidelity["overview"]), bool(fidelity["guidance"]), "verb-noun-format" in slugs)).to(equal((True, True, True)))

    @s.and_("it names the stage Discovery")
    def _(world):
        expect(world.help["stage"]["name"]).to(equal("Discovery"))

    @s.and_("its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html")
    def _(world):
        expect(world.help["href"]).to(equal(f"{FORGE}/fidelities/stories-story_map.html"))


@shared_stories.scenario("Open Help", "Open a practice's help")
def _(s):
    @s.given("billing-report's practices are shown in the details")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person opens help on the Stories practice")
    def _(world):
        world.help = world.data_of(world.Board.load().help(practice="stories"))

    @s.then("a side panel shows Practice overview and SHARED RULES such as do-not-invent-requirements")
    def _(world):
        practice = world.help["practice"]
        slugs = [rule["slug"] for rule in practice["rules"]]
        expect((bool(practice["overview"]), "do-not-invent-requirements" in slugs)).to(equal((True, True)))

    @s.and_("it names no fidelity")
    def _(world):
        expect((world.help["fidelity"], world.help["stage"])).to(equal((None, None)))

    @s.and_("its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/context-tools/stories.html")
    def _(world):
        expect(world.help["href"]).to(equal(f"{FORGE}/context-tools/stories.html"))


@shared_stories.scenario("Open Help", "Link the ddd model fidelity to its own page")
def _(s):
    @s.given("the catalog has a page for the ddd model fidelity")
    def _(world):
        world.project.seed_session(BILLING_REPORT)

    @s.when("the Person opens help on the ddd model fidelity")
    def _(world):
        world.help = world.data_of(world.Ticket.load(BILLING_REPORT.name).work.progress_of("ddd-model").help())

    @s.then("its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/ddd-model.html")
    def _(world):
        expect(world.help["href"]).to(equal(f"{FORGE}/fidelities/ddd-model.html"))


@shared_stories.scenario("Send Next Fidelity Action", "Generate the next fidelity in its default format")
def _(s):
    @s.given("billing-report is the active ticket with nothing recorded and a chat is connected")
    def _(world):
        world.project.seed_session(BILLING_REPORT)
        world.project.seed_active(BILLING_REPORT)

    @s.when("the Person runs billing-report's next step")
    def _(world):
        world.before = world.data_of(world.Ticket.load(BILLING_REPORT.name))
        world.discovery = column_in(world.data_of(world.Board.load().show()), "Discovery")
        world.next_fidelity = next(fidelity for fidelity in world.discovery["work_required"] if fidelity["slug"] == world.before["next"]["fidelity"]["slug"])

    @s.then("Run next read Run next: generate before it ran")
    def _(world):
        expect((next_in(world.before)["next_action"], world.before["next"]["fidelity"]["slug"])).to(equal(("generate", STORY_MAP)))

    # The board app writes the command from the stage's default format; the command itself is left to its specs.
    @s.and_("the chat receives the command /actions-generate stories-story-map format=markdown")
    def _(world):
        expect(world.next_fidelity["default_format"]).to(equal("markdown"))


@shared_stories.scenario("Send Next Fidelity Action", "Open the report while violations hold the ticket")
def _(s):
    @s.given("checkout-flow's story map has a verb-noun-format violation on .context/story-map.md line 6")
    def _(world):
        seed_checkout_flow_held_on_violations(world.project)

    @s.but_("no chat is connected")
    def _(world):
        # No chat checks in on a throwaway project; opening the report needs none.
        pass

    @s.when("the Person runs checkout-flow's next step")
    def _(world):
        ticket = world.Ticket.load(CHECKOUT_FLOW.name)
        world.before = world.data_of(ticket)
        world.report = world.data_of(ticket.work.progress_of(world.before["next"]["fidelity"]["slug"]).report())

    @s.then("Run next read Run next: review violations")
    def _(world):
        expect(next_in(world.before)["next_action"]).to(equal("review"))

    @s.and_("the report panel opens on stories-story-map")
    def _(world):
        expect(world.report["path"]).to(equal(f".sessions/{CHECKOUT_FLOW.name}/validation-reports/{STORY_MAP_REPORT}.md"))


@shared_stories.scenario("Send Next Fidelity Action", "Record a review with no chat")
def _(s):
    @s.given("billing-report's story map is generated and validated with no violations")
    def _(world):
        world.project.seed_session(BILLING_REPORT.with_log(*STORY_MAP_VALIDATED_CLEAN))

    @s.but_("no chat is connected")
    def _(world):
        # No chat checks in on a throwaway project; a review is the person's own approval and needs none.
        pass

    @s.when("the Person runs billing-report's next step")
    def _(world):
        ticket = world.Ticket.load(BILLING_REPORT.name)
        world.reviewed = world.data_of(ticket.work.progress_of(world.data_of(ticket)["next"]["fidelity"]["slug"]).finish_review())

    @s.then("billing-report's story_map marks Review ✓")
    def _(world):
        expect((world.reviewed["fidelity"]["slug"], world.reviewed["actions"]["review"])).to(equal((STORY_MAP, "done")))


@shared_stories.scenario("Send Next Fidelity Action", "Go back to an earlier stage's fidelity still to review")
def _(s):
    @s.given("pet-visits' story map is generated and validated with no violations")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(*STORY_MAP_VALIDATED_CLEAN))

    @s.and_("a person has moved pet-visits into Specification")
    def _(world):
        world.project.seed_log_line(PET_VISITS, MOVED_INTO_SPECIFICATION)

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("Run next reads Run next: review on stories-story-map")
    def _(world):
        expect((next_in(world.read)["next_action"], world.read["next"]["fidelity"]["slug"])).to(equal(("review", STORY_MAP)))


@shared_stories.scenario("Send Next Fidelity Action", "Name nothing to run on a ticket done in its stage")
def _(s):
    @s.given("every Discovery fidelity of pet-visits is reviewed")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(*EVERY_DISCOVERY_FIDELITY_REVIEWED))

    @s.when("the session board reads pet-visits")
    def _(world):
        world.read = world.data_of(world.Ticket.load(PET_VISITS.name))

    @s.then("Run next says Nothing to run next")
    def _(world):
        expect_no_next(world.read)
