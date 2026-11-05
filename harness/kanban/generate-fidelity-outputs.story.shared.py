"""Generate Fidelity Outputs: the shared scenarios the Python tiers replay.

Scenarios: move-work-forward-on-session-board/generate-fidelity-outputs/*/*_story.test.py.
Map: .context/story-map.md#e-generate-fidelity-outputs. Model: .context/kanban-model.md.

Steps reach the board and the session only through the World a tier hands them (`world.Ticket`, `world.Generate`,
`world.Session`), so the domain spec and the cdd tools spec replay the same steps.

Covered by the board app's TypeScript client specs in harness/kanban/app, not here, because they have no Python
operation: Choose Action And Formats (all seven: the tile's action bar and its chips); Render Fidelity Format (both:
the board app writes the render command); Send Tile Action To Chat (both: the board app writes the sketch, iterate,
and document commands and picks the chat). The Thens of the scenarios below that only the page shows (a bar's picks)
are left to those specs too.

Several scenarios name a story map at `tests/story-map.md` or under a root as `<root>/story-map.md`. The story_map
fidelity declares its markdown at `.context/story-map.md` and its drawio at `.context/story-map.drawio`
(cdd_guidance/practices/stories/stories.md), so `Session.fidelity_outputs` puts them under `<root>/.context/`; those
Thens fail until the declaration and the scenarios agree.
"""

from __future__ import annotations

from pathlib import Path

from expects import end_with, equal, expect

from harness.kanban.session_board_examples import (
    ALPHA,
    ALPHA_WORKPATH,
    BILLING_REPORT,
    PET_VISITS,
    PET_VISITS_STORY_MAP_FILE,
    PET_VISITS_STORY_MAP_ROOT,
    PET_VISITS_STORY_MAP_TEXT,
    STORY_MAP,
    generated,
)
from harness.kanban.story_test import SharedStories, expect_action
from stories.stories import Stories

shared_stories = SharedStories("Generate Fidelity Outputs")


def at_work(relative: str) -> str:
    """A path under alpha's workpath, as Session.fidelity_outputs writes it."""
    return (Path(ALPHA_WORKPATH) / relative).resolve().as_posix()


@shared_stories.scenario("Generate Fidelity Output", "Send the generate command from a tile")
def _(s):
    @s.given("billing-report is the active ticket with nothing generated and a chat is connected")
    def _(world):
        world.project.seed_session(BILLING_REPORT)
        world.project.seed_active(BILLING_REPORT)

    @s.when("the Person runs generate on story_map")
    def _(world):
        world.commands = world.Ticket.load(BILLING_REPORT.name).generate_commands(fidelities=[STORY_MAP], formats=["markdown"])

    # The command also names the ticket's session.json, as kanban_tools_spec 'should name the ticket's session in the
    # generate command' requires, because a command runs in whichever chat it is sent to.
    @s.then("the chat runs /actions-generate stories-story-map format=markdown")
    def _(world):
        expect(world.commands).to(equal(["/actions-generate stories-story-map format=markdown session=.sessions/billing-report/session.json"]))


@shared_stories.scenario("Generate Fidelity Output", "Render the earlier fidelity into a new format first")
def _(s):
    @s.given("pet-visits' story map is docs/story-map.md, generated in markdown only")
    def _(world):
        world.project.seed_session(PET_VISITS.with_log(generated("stories", "story_map")))
        world.project.seed_session_fields(PET_VISITS, outputs={"stories": {"root": PET_VISITS_STORY_MAP_ROOT}})
        world.project.seed_file(PET_VISITS_STORY_MAP_FILE, PET_VISITS_STORY_MAP_TEXT)

    @s.when("the Person generates scenarios in drawio")
    def _(world):
        world.commands = world.Ticket.load(PET_VISITS.name).generate_commands(fidelities=["stories-scenarios"], formats=["drawio"])

    # Fails today: the story map's markdown is declared at docs/.context/story-map.md, so docs/story-map.md is not its
    # output and nothing is rendered first.
    @s.then("the first command is /actions-render stories-story-map format=drawio source=markdown")
    def _(world):
        expect(world.commands[0]).to(equal("/actions-render stories-story-map format=drawio source=markdown session=.sessions/pet-visits/session.json"))

    @s.and_("the last is /actions-generate stories-scenarios format=drawio")
    def _(world):
        expect(world.commands[-1]).to(equal("/actions-generate stories-scenarios format=drawio session=.sessions/pet-visits/session.json"))


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
        expect_action(world.ticket.to_json(), STORY_MAP, "generate", "done")


@shared_stories.scenario("Resolve Fidelity Output Paths", "Put a fidelity's files under its practice's root")
def _(s):
    @s.given("the session alpha works in /work")
    def _(world):
        world.project.seed_session(ALPHA)

    @s.and_("the story_map fidelity declares root tests, markdown story-map.md, and drawio story-map.drawio")
    def _(world):
        # A fidelity's outputs are declared in its practice's guidance, cdd_guidance/practices/stories/stories.md.
        pass

    @s.when("Claude Code asks where story_map's files go")
    def _(world):
        world.outputs = world.Session.at(world.project.sessions / ALPHA.name, world.project.root).fidelity_outputs(Stories(fidelity="story_map"))

    # Fails today: stories.md declares the story map's markdown at .context/story-map.md under the workpath.
    @s.then("the markdown file is /work/tests/story-map.md")
    def _(world):
        expect(world.outputs["markdown"]).to(equal([at_work("tests/story-map.md")]))


@shared_stories.scenario("Resolve Fidelity Output Paths", "Use the practice's root named in session.json")
def _(s):
    @s.given("alpha's session.json names docs/stories as the stories root")
    def _(world):
        world.project.seed_session(ALPHA)
        world.project.seed_session_fields(ALPHA, outputs={"stories": {"root": "docs/stories"}})

    @s.when("Claude Code asks where story_map's files go")
    def _(world):
        world.outputs = world.Session.at(world.project.sessions / ALPHA.name, world.project.root).fidelity_outputs(Stories(fidelity="story_map"))

    # Fails today: the markdown goes in the root's .context folder, /work/docs/stories/.context/story-map.md.
    @s.then("the markdown file is /work/docs/stories/story-map.md")
    def _(world):
        expect(world.outputs["markdown"]).to(equal([at_work("docs/stories/story-map.md")]))


@shared_stories.scenario("Resolve Fidelity Output Paths", "Prefer the fidelity's own root")
def _(s):
    @s.given("alpha's session.json names docs/stories for stories and docs/map for story_map")
    def _(world):
        world.project.seed_session(ALPHA)
        world.project.seed_session_fields(ALPHA, outputs={"stories": {"root": "docs/stories", "story_map": {"root": "docs/map"}}})

    @s.when("Claude Code asks where story_map's files go")
    def _(world):
        world.outputs = world.Session.at(world.project.sessions / ALPHA.name, world.project.root).fidelity_outputs(Stories(fidelity="story_map"))

    # Fails today: the drawio goes in the root's .context folder, /work/docs/map/.context/story-map.drawio.
    @s.then("the drawio file is /work/docs/map/story-map.drawio")
    def _(world):
        expect(world.outputs["drawio"]).to(equal([at_work("docs/map/story-map.drawio")]))


@shared_stories.scenario("Resolve Fidelity Output Paths", "Rename a single-file output and keep a pattern")
def _(s):
    @s.given("alpha's session.json names our-map.md for story_map's markdown and one-file.py for scenarios' python")
    def _(world):
        world.project.seed_session(ALPHA)
        world.project.seed_session_fields(ALPHA, outputs={"stories": {"story_map": {"markdown": "our-map.md"}, "scenarios": {"python": "one-file.py"}}})

    @s.when("Claude Code asks where story_map's and scenarios' files go")
    def _(world):
        world.outputs = world.Session.at(world.project.sessions / ALPHA.name, world.project.root).fidelity_outputs(Stories(fidelity="story_map"))
        world.scenario_outputs = world.Session.at(world.project.sessions / ALPHA.name, world.project.root).fidelity_outputs(Stories(fidelity="scenarios"))

    # Fails today: both files go in the workpath's .context folder, /work/.context/our-map.md and /work/.context/story-map.drawio.
    @s.then("story_map's markdown is /work/tests/our-map.md and its drawio stays /work/tests/story-map.drawio")
    def _(world):
        expect((world.outputs["markdown"], world.outputs["drawio"])).to(equal(([at_work("tests/our-map.md")], [at_work("tests/story-map.drawio")])))

    @s.and_("scenarios' python keeps its declared name, such as archive_ticket_story.test.py for the story Archive Ticket")
    def _(world):
        expect(world.scenario_outputs["python"][0]).to(end_with("/{story_snake}_story.test.py"))
