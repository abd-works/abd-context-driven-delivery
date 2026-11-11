"""Guide Work Through Practices In Chat Bar: the shared scenarios the Python tiers replay for the pattern overlays a
session chooses from the chat bar.

Scenarios: harness/.context/stories/move-work-forward-from-chat-bar/guide-work-through-practices/
guide_work_through_practices_story.test.md (List Available Patterns, Choose Graph Overlays, Display Overlay Icons).
Map: harness/.context/stories/story-map.md#e-guide-work-through-practices-in-chat-bar.

Steps reach the ticket only through the World a tier hands them (`world.Ticket`), so the domain spec and the cdd tools
spec replay the same steps. Display Overlay Icons is drawn by the chat bar's TypeScript, whose story tests were removed
(commit 8c56ab052); its icons come from the overlay choices the Thens here assert.
"""

from __future__ import annotations

import json

from expects import contain, equal, expect

from space.kanban.session_board_examples import CHECKOUT_FLOW
from space.kanban.story_test import SharedStories, refusal_of

shared_stories = SharedStories("Guide Work Through Practices In Chat Bar")

# Seed: the patterns cdd_guidance/patterns registers, each with the icon the chat bar shows for it.
PATTERNS = {"cdd_claude_mod": "CD", "cdd_web_domain_access": "CS", "lern_domain_driven": "LN", "mern_domain_driven": "MN"}
# Interaction: the patterns a person chooses, and a name that is no pattern.
LERN = "lern_domain_driven"
WEB_DOMAIN_ACCESS = "cdd_web_domain_access"
NO_PATTERN = "astrology"


def chosen_in(choices: list[dict]) -> list[str]:
    return [choice["pattern"] for choice in choices if choice["is_chosen"]]


def overlays_kept_by(world, seed) -> list[str]:
    return json.loads((world.project.sessions / seed.name / "session.json").read_text(encoding="utf-8")).get("overlays", [])


@shared_stories.scenario("List Available Patterns", "Offer every pattern the patterns folder holds")
def _(s):
    @s.given("checkout-flow's session has chosen no overlays")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the chat bar asks checkout-flow for its overlay choices")
    def _(world):
        world.choices = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).overlay_choices())

    @s.then("it receives one choice per pattern in name order, each with its overlay icon")
    def _(world):
        expect([(choice["pattern"], choice["icon"]) for choice in world.choices]).to(equal(list(PATTERNS.items())))

    @s.and_("none of them is chosen")
    def _(world):
        expect(chosen_in(world.choices)).to(equal([]))


@shared_stories.scenario("List Available Patterns", "Leave out a folder that defines no pattern")
def _(s):
    @s.given("the patterns folder also holds domain_driven_stack, which defines no pattern of its own")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the chat bar asks checkout-flow for its overlay choices")
    def _(world):
        world.choices = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).overlay_choices())

    @s.then("domain_driven_stack is not among them")
    def _(world):
        expect([choice["pattern"] for choice in world.choices]).not_to(contain("domain_driven_stack"))


@shared_stories.scenario("Choose Graph Overlays", "Choose a pattern as the session's overlay")
def _(s):
    @s.given("checkout-flow's session has chosen no overlays")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the Person chooses lern_domain_driven as an overlay of checkout-flow")
    def _(world):
        world.choices = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).choose_overlays(overlays=[LERN]))

    @s.then("checkout-flow's overlay choices show lern_domain_driven chosen")
    def _(world):
        expect(chosen_in(world.choices)).to(equal([LERN]))

    @s.and_("checkout-flow's session.json keeps lern_domain_driven among its overlays")
    def _(world):
        expect(overlays_kept_by(world, CHECKOUT_FLOW)).to(equal([LERN]))


@shared_stories.scenario("Choose Graph Overlays", "Choose a second pattern beside the first")
def _(s):
    @s.given("checkout-flow's session has chosen lern_domain_driven")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_fields(CHECKOUT_FLOW, overlays=[LERN])

    @s.when("the Person also chooses cdd_web_domain_access")
    def _(world):
        world.choices = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).choose_overlays(overlays=[LERN, WEB_DOMAIN_ACCESS]))

    @s.then("checkout-flow's overlay choices show lern_domain_driven and cdd_web_domain_access chosen")
    def _(world):
        expect(chosen_in(world.choices)).to(equal([WEB_DOMAIN_ACCESS, LERN]))


@shared_stories.scenario("Choose Graph Overlays", "Take a chosen pattern out")
def _(s):
    @s.given("checkout-flow's session has chosen lern_domain_driven and cdd_web_domain_access")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_fields(CHECKOUT_FLOW, overlays=[LERN, WEB_DOMAIN_ACCESS])

    @s.when("the Person takes lern_domain_driven out of checkout-flow's overlays")
    def _(world):
        world.choices = world.data_of(world.Ticket.load(CHECKOUT_FLOW.name).choose_overlays(overlays=[WEB_DOMAIN_ACCESS]))

    @s.then("checkout-flow's overlay choices show only cdd_web_domain_access chosen")
    def _(world):
        expect(chosen_in(world.choices)).to(equal([WEB_DOMAIN_ACCESS]))


@shared_stories.scenario("Choose Graph Overlays", "Apply the chosen overlays to the session's graph")
def _(s):
    @s.given("checkout-flow's session has its graph open with no overlays")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.ticket = world.Ticket.load(CHECKOUT_FLOW.name)
        world.graph = world.ticket.session.graph

    @s.when("the Person chooses lern_domain_driven as an overlay of checkout-flow")
    def _(world):
        world.ticket.choose_overlays(overlays=[LERN])

    @s.then("checkout-flow's graph applies lern_domain_driven")
    def _(world):
        expect([pattern.pattern for pattern in world.graph.applied_patterns.patterns]).to(equal([LERN]))


@shared_stories.scenario("Choose Graph Overlays", "Refuse a name that is no pattern")
def _(s):
    @s.given("checkout-flow's session has chosen no overlays")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)

    @s.when("the Person chooses astrology as an overlay of checkout-flow")
    def _(world):
        world.refused = refusal_of(lambda: world.Ticket.load(CHECKOUT_FLOW.name).choose_overlays(overlays=[NO_PATTERN]))

    @s.then("the choice is refused, naming astrology as no pattern")
    def _(world):
        expect(str(world.refused)).to(contain(f"{NO_PATTERN} is no pattern"))

    @s.but_("checkout-flow's overlays are not changed")
    def _(world):
        expect(overlays_kept_by(world, CHECKOUT_FLOW)).to(equal([]))
