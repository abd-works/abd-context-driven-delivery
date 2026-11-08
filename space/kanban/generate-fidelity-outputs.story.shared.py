"""Generate Fidelity Outputs: the shared scenarios the Python tiers replay.

Scenarios: move-work-forward-on-session-board/generate-fidelity-outputs/*/*_story.test.py.
Map: .context/story-map.md#e-generate-fidelity-outputs. Model: .context/kanban-model.md.

Steps reach the board and the session only through the World a tier hands them (`world.Ticket`, `world.Generate`,
`world.Sessions`), so the domain spec and the cdd tools spec replay the same steps.

Covered by the board app's TypeScript client specs in space/kanban/app, not here, because they have no Python
operation: Choose Action And Formats (all seven: the tile's action bar and its chips); Generate Fidelity Output "Send
the generate command from a tile" (the board app writes the generate command); Render Fidelity Format (both: the board
app writes the render command); Send Tile Action To Chat (both: the board app writes the sketch, iterate, and document
commands and picks the chat). The Thens of the scenarios below that only the page shows (a bar's picks) are left to
those specs too.

Generate Fidelity Output "Render the earlier fidelity into a new format first" belongs to the Generate action, which
renders the earlier fidelity before it generates, so its specs are in cdd_guidance/actions/generate.

The story_map fidelity declares its markdown at `.context/story-map.md` and its drawio at `.context/story-map.drawio`
(cdd_guidance/practices/stories/stories.md), so `FidelityGuidance.output_paths` puts them under `<root>/.context/`.
"""

from __future__ import annotations

from pathlib import Path

from expects import end_with, equal, expect

from space.kanban.session_board_examples import (
    ALPHA,
    ALPHA_WORKPATH,
    PET_VISITS,
    STORY_MAP,
)
from space.kanban.story_test import SharedStories, expect_action

shared_stories = SharedStories("Generate Fidelity Outputs")


def at_work(relative: str) -> str:
    """A path under alpha's workpath, as FidelityGuidance.output_paths writes it."""
    return (Path(ALPHA_WORKPATH) / relative).resolve().as_posix()


@shared_stories.scenario("Generate Fidelity Output", "Count a generate line as Generate done")
def _(s):
    @s.given("the session log of pet-visits has no generate line for story_map")
    def _(world):
        world.project.seed_session(PET_VISITS)
        # Claude Code generates in the session open on the project, which is pet-visits.
        world.project.seed_active(PET_VISITS)
        world.ticket = world.Ticket.load(PET_VISITS.name)

    @s.when("Claude Code finishes generating the story map")
    def _(world):
        world.Generate().generate(guidance=["stories-story-map"])

    @s.then("the session log ends with a generate line naming stories story_map markdown")
    def _(world):
        last = (world.project.sessions / PET_VISITS.name / "session.log").read_text(encoding="utf-8").splitlines()[-1]
        expect((last.split()[1], " stories story_map markdown " in last)).to(equal(("generate", True)))

    @s.and_("the story_map tile marks Generate ✓")
    def _(world):
        expect_action(world.data_of(world.ticket), STORY_MAP, "generate", "done")


@shared_stories.scenario("Resolve Fidelity Output Paths", "Put a fidelity's files under its practice's root")
def _(s):
    @s.given("the session alpha works in /work")
    def _(world):
        world.project.seed_session(ALPHA)

    @s.and_("the story_map fidelity declares markdown .context/story-map.md and drawio .context/story-map.drawio")
    def _(world):
        # A fidelity's outputs are declared in its practice's guidance, cdd_guidance/practices/stories/stories.md.
        pass

    @s.when("Claude Code asks where story_map's files go")
    def _(world):
        world.outputs = world.Sessions(world.project.root).load(world.project.sessions / ALPHA.name).practices["stories"].fidelities["story_map"].output_paths()

    @s.then("the markdown file is /work/.context/story-map.md")
    def _(world):
        expect(world.outputs["markdown"]).to(equal([at_work(".context/story-map.md")]))


@shared_stories.scenario("Resolve Fidelity Output Paths", "Use the practice's root named in session.json")
def _(s):
    @s.given("alpha's session.json names docs/stories as the stories root")
    def _(world):
        world.project.seed_session(ALPHA)
        world.project.seed_session_fields(ALPHA, outputs={"stories": {"root": "docs/stories"}})

    @s.when("Claude Code asks where story_map's files go")
    def _(world):
        world.outputs = world.Sessions(world.project.root).load(world.project.sessions / ALPHA.name).practices["stories"].fidelities["story_map"].output_paths()

    @s.then("the markdown file is /work/docs/stories/.context/story-map.md")
    def _(world):
        expect(world.outputs["markdown"]).to(equal([at_work("docs/stories/.context/story-map.md")]))


@shared_stories.scenario("Resolve Fidelity Output Paths", "Prefer the fidelity's own root")
def _(s):
    @s.given("alpha's session.json names docs/stories for stories and docs/map for story_map")
    def _(world):
        world.project.seed_session(ALPHA)
        world.project.seed_session_fields(ALPHA, outputs={"stories": {"root": "docs/stories", "story_map": {"root": "docs/map"}}})

    @s.when("Claude Code asks where story_map's files go")
    def _(world):
        world.outputs = world.Sessions(world.project.root).load(world.project.sessions / ALPHA.name).practices["stories"].fidelities["story_map"].output_paths()

    @s.then("the drawio file is /work/docs/map/.context/story-map.drawio")
    def _(world):
        expect(world.outputs["drawio"]).to(equal([at_work("docs/map/.context/story-map.drawio")]))


@shared_stories.scenario("Resolve Fidelity Output Paths", "Rename a single-file output and keep a pattern")
def _(s):
    @s.given("alpha's session.json names our-map.md for story_map's markdown and one-file.py for scenarios' python")
    def _(world):
        world.project.seed_session(ALPHA)
        world.project.seed_session_fields(ALPHA, outputs={"stories": {"story_map": {"markdown": "our-map.md"}, "scenarios": {"python": "one-file.py"}}})

    @s.when("Claude Code asks where story_map's and scenarios' files go")
    def _(world):
        world.outputs = world.Sessions(world.project.root).load(world.project.sessions / ALPHA.name).practices["stories"].fidelities["story_map"].output_paths()
        world.scenario_outputs = world.Sessions(world.project.root).load(world.project.sessions / ALPHA.name).practices["stories"].fidelities["scenarios"].output_paths()

    @s.then("story_map's markdown is /work/.context/our-map.md and its drawio stays /work/.context/story-map.drawio")
    def _(world):
        expect((world.outputs["markdown"], world.outputs["drawio"])).to(equal(([at_work(".context/our-map.md")], [at_work(".context/story-map.drawio")])))

    @s.and_("scenarios' python keeps its declared name, such as archive_ticket_story.test.py for the story Archive Ticket")
    def _(world):
        expect(world.scenario_outputs["python"][0]).to(end_with("/{story_snake}_story.test.py"))
