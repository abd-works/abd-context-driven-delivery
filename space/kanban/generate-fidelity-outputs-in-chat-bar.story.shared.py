"""Generate Fidelity Outputs In Chat Bar: the shared scenarios the Python tiers replay for an action run with the
session's pattern overlays.

Scenarios: harness/.context/stories/move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar/
generate_fidelity_outputs_in_chat_bar_story.test.md (Run Fidelity Action With Overlays).
Map: harness/.context/stories/story-map.md#e-generate-fidelity-outputs-in-chat-bar.

Steps reach the session and Generate only through the namespace a tier hands them, so the domain spec and the cdd tools
spec replay the same steps. "Name the chosen overlays in the command" is the chat bar's TypeScript, whose story tests
were removed (commit 8c56ab052), so it is not replayed here.
"""

from __future__ import annotations

import json

from expects import contain, equal, expect

from cdd_guidance.actions.generate.generate import Generate
from space.kanban.session_board_examples import CHECKOUT_FLOW
from space.kanban.story_test import SharedStories

shared_stories = SharedStories("Generate Fidelity Outputs In Chat Bar")

# Seed: the overlays a session has chosen, each with how its shared rules open.
OVERLAYS = {
    "lern_domain_driven": "Whenever you create, alter, or delete a LERN domain module under `src/`",
    "mern_domain_driven": "Whenever you create, alter, or delete a domain-module feature package",
}
LERN = "lern_domain_driven"
# Interaction: the fidelity Claude Code generates.
ACCEPTANCE_TESTS = "stories-acceptance-tests"


def instructions_generated(world, guidance: str) -> str:
    """The instructions Generate gives Claude Code for guidance: the recipe expanded in process on the domain tier, the
    generate prompt as the cdd server answers it on the server tier."""
    action = world.Generate()
    if isinstance(action, Generate):
        return action.instructions["generate"].expand({"guidance": guidance}).instructions
    return str(action.generate(guidance=guidance))


def overlays_kept_by(world) -> list[str]:
    return json.loads((world.project.sessions / CHECKOUT_FLOW.name / "session.json").read_text(encoding="utf-8")).get("overlays", [])


@shared_stories.scenario("Run Fidelity Action With Overlays", "Choose the overlays a command names")
def _(s):
    @s.given("checkout-flow's session overlays none")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("Claude Code generates stories-acceptance-tests with overlays=lern_domain_driven")
    def _(world):
        world.Generate().generate(guidance=f"{ACCEPTANCE_TESTS} overlays={LERN}")

    @s.then("checkout-flow's session overlays lern_domain_driven")
    def _(world):
        expect(overlays_kept_by(world)).to(equal([LERN]))


@shared_stories.scenario("Run Fidelity Action With Overlays", "Follow each overlay's shared rules when generating")
def _(s):
    @s.given("checkout-flow's session overlays lern_domain_driven and mern_domain_driven")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_fields(CHECKOUT_FLOW, overlays=list(OVERLAYS))
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("Claude Code generates stories-acceptance-tests")
    def _(world):
        world.instructions = instructions_generated(world, ACCEPTANCE_TESTS)

    @s.then("the instructions name each overlay as a pattern overlay")
    def _(world):
        expect([f"## Pattern overlay: {name}" in world.instructions for name in OVERLAYS]).to(equal([True, True]))

    @s.and_("they hold each overlay's shared rules")
    def _(world):
        expect([opening in world.instructions for opening in OVERLAYS.values()]).to(equal([True, True]))


@shared_stories.scenario("Run Fidelity Action With Overlays", "Generate with no overlay chosen")
def _(s):
    @s.given("checkout-flow's session overlays none")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("Claude Code generates stories-acceptance-tests")
    def _(world):
        world.instructions = instructions_generated(world, ACCEPTANCE_TESTS)

    @s.then("the instructions name no pattern overlay")
    def _(world):
        expect(world.instructions).not_to(contain("Pattern overlay:"))


@shared_stories.scenario("Run Fidelity Action With Overlays", "Judge each overlay's shared rules when validating")
def _(s):
    @s.given("checkout-flow's session overlays lern_domain_driven and mern_domain_driven")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_session_fields(CHECKOUT_FLOW, overlays=list(OVERLAYS))
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("Claude Code validates stories-acceptance-tests")
    def _(world):
        world.report = str(world.Validate().validate(guidance=ACCEPTANCE_TESTS))

    @s.then("the report names each overlay as a pattern overlay")
    def _(world):
        expect([f"## Pattern overlay: {name}" in world.report for name in OVERLAYS]).to(equal([True, True]))

    @s.and_("it holds each overlay's shared rules")
    def _(world):
        expect([opening in world.report for opening in OVERLAYS.values()]).to(equal([True, True]))


@shared_stories.scenario("Run Fidelity Action With Overlays", "Validate with no overlay chosen")
def _(s):
    @s.given("checkout-flow's session overlays none")
    def _(world):
        world.project.seed_session(CHECKOUT_FLOW)
        world.project.seed_active(CHECKOUT_FLOW)

    @s.when("Claude Code validates stories-acceptance-tests")
    def _(world):
        world.report = str(world.Validate().validate(guidance=ACCEPTANCE_TESTS))

    @s.then("the report names no pattern overlay")
    def _(world):
        expect(world.report).not_to(contain("Pattern overlay:"))
