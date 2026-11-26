"""Mamba spec for a Claude Design story map. Render writes the canvas: the map page and the screens page."""

import json
import re
import shutil
import tempfile
from pathlib import Path

from mamba import after, description, context, it, before
from expects import be, contain, equal, expect, have_keys, have_len

from cdd_guidance.practices.ux.model.claude_design.story_canvas import (
    ClaudeDesignEpic,
    ClaudeDesignStory,
    ClaudeDesignStoryMap,
    StoryCanvasSetup,
)
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen, WrittenMarkup
from cdd_guidance.practices.source_code.call_graph import CallGraph
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownStep
from cdd_guidance.practices.stories.model.story_map import Epic, Scenario, Step, StepType, Story, StoryMap
from cdd_guidance.practices.stories.model.story_map_files import source_at
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap


def _story_map() -> StoryMap:
    story_map = StoryMap()
    epic = Epic("Onboard A Customer", 1)
    sub_epic = Epic("Select Plan", 1)
    story = Story("Choose Plan", 1)
    story.actors.append("Customer")
    scenario = Scenario("See the plan catalog", 1)
    scenario.steps.append(Step("the Customer has no account", StepType.GIVEN, 1))
    scenario.steps.append(Step("the Customer opens My Paradise", StepType.WHEN, 2))
    story.scenarios.append(scenario)
    sub_epic.stories.append(story)
    sub_epic.stories.append(Story("Create Credentials", 2))
    epic.epics.append(sub_epic)
    story_map.epics.append(epic)
    return story_map


def _catalog_screen() -> Screen:
    screen = Screen("Plan catalog", 1)
    screen.image = "shots/plan-catalog.png"
    screen.prototype = "plan-catalog.dc.html"
    screen.show_step("Choose Plan \u203a See the plan catalog \u203a the Customer opens My Paradise")
    return screen


def _ux_map(*screens: Screen) -> UxMap:
    ux_map = UxMap.create()
    for screen in screens:
        ux_map.append_screen(screen)
    return ux_map


def _outline_map() -> StoryMap:
    """Create Credentials with an outline whose steps name its columns, and two rows in its Examples table."""
    story_map = StoryMap()
    epic = Epic("Create Account", 1)
    story = Story("Create Credentials", 1)
    outline = Scenario("Enter Invalid credentials", 1)
    outline.steps.append(Step("the Customer has entered {example}", StepType.GIVEN, 1))
    outline.steps.append(Step("the Customer registers the credentials", StepType.WHEN, 2))
    outline.steps.append(Step("the {message} message is shown", StepType.THEN, 3))
    outline.examples["missing email"] = {"message": "++email required++"}
    outline.examples["password missing letters"] = {"message": "password rule"}
    story.scenarios.append(outline)
    epic.stories.append(story)
    story_map.epics.append(epic)
    return story_map


_DOMAIN_MODEL = """# Domain model

### Cart <<Aggregate Root>> <<Entity>>

A cart holds the lines a Customer picks.

---

+ add(line)
\t+ total

### Line <<Entity>>

A line on a plan.
"""

_CART = "../domain/domain-model.md#cart-aggregate-root-entity"
_LINE = "../domain/domain-model.md#line-entity"


def _linked_step(line: str, phase: StepType, order: int, realization: str = "") -> MarkdownStep:
    """A step read from line of a scenario file in stories/, as the scenarios reader reads one."""
    keyword, text = re.match(r"\*(\w+)\* (.*)$", line).groups()
    step = MarkdownStep(text, phase, order)
    step.keyword = keyword
    step.source = source_at("stories/choose-plan.md", order)
    step.read_from(line)
    if realization:
        step.call_graph = CallGraph().read(realization)
    return step


def _linked_map() -> StoryMap:
    """Choose Plan, whose steps link cart and line to their classes, one of them linking cart to Line."""
    story_map = _story_map()
    scenario = story_map.epics[0].epics[0].stories[0].scenarios[0]
    scenario.steps = [
        _linked_step(f"*Given* the Customer has a ++[cart]({_CART})++", StepType.GIVEN, 1, "Cart.create()"),
        _linked_step("*When* the Customer opens My Paradise", StepType.WHEN, 2, "Catalog.open()\n  -> Plan.list()"),
        _linked_step(f"*Then* the ++[cart]({_CART})++ holds a ++[line]({_LINE})++ and no carts", StepType.THEN, 3),
        _linked_step(f"*Then* the ++[cart]({_LINE})++ is still empty", StepType.THEN, 4),
    ]
    return story_map


def _tree_of(explorer: str) -> list:
    return json.loads(explorer.split("tree() {\nreturn ", 1)[1].split(";\n}", 1)[0])


with description("a Claude Design story map") as self:
    with before.each:
        self.files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(_catalog_screen()))).render(_story_map()))
        self.canvas = json.loads(self.files["project/canvas.json"])

    with context("rendered from a story map whose step is shown on a screen"):
        with it("puts the story map, the story explorer and each screen on its own page"):
            expect([page["id"] for page in self.canvas["pages"]]).to(equal(["story-map", "screens", "screen-plan-catalog"]))
            expect(self.canvas["boards"]["screens/plan-catalog.dc.html"]["page"]).to(equal("screen-plan-catalog"))

        with it("draws the whole story map on one artboard: epic, sub-epic and story cards"):
            story_map = self.files["project/Main.dc.html"]
            for name in ("Onboard A Customer", "Select Plan", "Choose Plan", "Create Credentials"):
                expect(story_map).to(contain(name))
            expect(self.canvas["boards"]["Main.dc.html"]["page"]).to(equal("story-map"))
            expect([name for name in self.canvas["boards"] if self.canvas["boards"][name]["page"] == "story-map"]).to(equal(["Main.dc.html"]))

        with it("sizes the story map to one column per story inside its margin"):
            board = self.canvas["boards"]["Main.dc.html"]
            expect(board["w"]).to(equal(2 * ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px + 2 * ClaudeDesignStoryMap.margin))

        with it("puts the screen a story's step is shown on under the story, opening the explorer at that step"):
            story_map = self.files["project/Main.dc.html"]
            expect(story_map).to(contain('src="shots/plan-catalog.png"'))
            expect(story_map).to(contain('href="/screens/explorer.dc.html#story=Choose%20Plan&scenario=See%20the%20plan%20catalog'))

        with it("links only the thumbnails, not the story cards"):
            expect(self.files["project/Main.dc.html"].count("<a href")).to(equal(1))

        with it("draws each epic once, across all its sub-epics"):
            expect(self.files["project/Main.dc.html"].count("Onboard A Customer")).to(equal(1))

        with it("draws on the dark abd background, not white"):
            expect(self.files["project/Main.dc.html"]).to(contain("#0B0B0B"))
            expect(self.files["project/Main.dc.html"]).not_to(contain("#ffffff"))

        with it("places the explorer on its page and the prototype screen alone on its own page"):
            expect(self.canvas["boards"]["screens/explorer.dc.html"]["page"]).to(equal("screens"))
            expect(self.canvas["boards"]["screens/plan-catalog.dc.html"]["page"]).to(equal("screen-plan-catalog"))

        with it("draws the prototype screen inside the explorer for the scenario that shows it"):
            explorer = self.files["project/screens/explorer.dc.html"]
            expect(explorer).to(contain('<dc-import name="plan-catalog"'))
            expect(explorer).to(contain('go="{{goToStory}}"'))
            expect(explorer).to(contain('"p": "plan-catalog"'))

        with it("hands each screen the selected step, so the screen can play it"):
            expect(self.files["project/screens/explorer.dc.html"]).to(contain('step="{{stepText}}"'))

        with it("hands each screen the position of the selected step group, so a scenario with several actions shows each outcome"):
            expect(self.files["project/screens/explorer.dc.html"]).to(contain('step-index="{{stepIndex}}"'))

        with it("hands each screen the kind of the selected step group, so it types what the Customer enters on a When"):
            explorer = self.files["project/screens/explorer.dc.html"]
            expect((explorer.count('step-kind="{{stepKind}}"'), explorer.count("stepKind: scen.b ? '' : (step.k || '')"))).to(equal((1, 1)))

    with context("rendered from a scenario with two actions, on a screen that names its story but no steps"):
        with before.each:
            story_map = _story_map()
            scenario = story_map.epics[0].epics[0].stories[0].scenarios[0]
            scenario.steps.append(Step("the catalog lists the plans", StepType.THEN, 3))
            scenario.steps.append(Step("the Customer picks Atlas", StepType.WHEN, 4))
            scenario.steps.append(Step("the cart holds Atlas", StepType.THEN, 5))
            screen = Screen("Plan catalog", 1)
            screen.prototype = "plan-catalog.dc.html"
            screen.show_story("Choose Plan")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(screen))).render(story_map))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("derives one step group per action: what leads to each action, its outcome, and the last outcome"):
            groups = [
                "Given the Customer has no account\nWhen the Customer opens My Paradise",
                "Then the catalog lists the plans\nWhen the Customer picks Atlas",
                "Then the cart holds Atlas",
            ]
            expect(self.explorer).to(contain(json.dumps([{"x": group, "i": [], "k": kind} for group, kind in zip(groups, ("when", "when", "then"))])))

    with context("rendered from a scenario with two actions, on a screen that names the first action and the last outcome"):
        with before.each:
            story_map = _story_map()
            scenario = story_map.epics[0].epics[0].stories[0].scenarios[0]
            scenario.steps.append(Step("the catalog lists the plans", StepType.THEN, 3))
            scenario.steps.append(Step("the Customer picks Atlas", StepType.WHEN, 4))
            scenario.steps.append(Step("the cart holds Atlas", StepType.THEN, 5))
            screen = _catalog_screen()
            screen.image = ""
            screen.show_step("Choose Plan \u203a See the plan catalog \u203a the cart holds Atlas")
            screen.show_story("Choose Plan")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(screen))).render(story_map))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("groups the steps at the step the UX map names, not at each action"):
            groups = [
                "Given the Customer has no account\nWhen the Customer opens My Paradise",
                "Then the catalog lists the plans\nWhen the Customer picks Atlas\nThen the cart holds Atlas",
            ]
            expect(self.explorer).to(contain(json.dumps([{"x": group, "i": [], "k": "when"} for group in groups])))

    with context("rendered from an epic that holds its stories directly, with no sub-epic"):
        with before.each:
            story_map = StoryMap()
            epic = Epic("Choose Lines", 1)
            epic.stories.append(Story("Add Line To Cart", 1))
            story_map.epics.append(epic)
            explorer = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(story_map))["project/screens/explorer.dc.html"]
            self.tree = json.loads(explorer.split("tree() {\nreturn ", 1)[1].split(";\n}", 1)[0])

        with it("lists the stories under the epic itself, with no sub-epic named after it"):
            expect([(epic["n"], epic["e"], [story["n"] for story in epic["s"]]) for epic in self.tree]).to(equal([("Choose Lines", [], ["Add Line To Cart"])]))

    with context("rendered from epics nested three deep"):
        with before.each:
            story_map = StoryMap()
            epic, sub_epic, inner = Epic("Onboard A Customer", 1), Epic("Choose Lines", 1), Epic("Pick Plans", 1)
            inner.stories.append(Story("Display Plans", 1))
            sub_epic.epics.append(inner)
            sub_epic.stories.append(Story("View Cart", 2))
            epic.epics.append(sub_epic)
            story_map.epics.append(epic)
            explorer = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(story_map))["project/screens/explorer.dc.html"]
            self.tree = json.loads(explorer.split("tree() {\nreturn ", 1)[1].split(";\n}", 1)[0])

        with it("nests each epic under the one that holds it, as deep as the story map does"):
            inner = self.tree[0]["e"][0]["e"][0]
            expect((self.tree[0]["n"], self.tree[0]["e"][0]["n"], inner["n"], [story["n"] for story in inner["s"]])).to(
                equal(("Onboard A Customer", "Choose Lines", "Pick Plans", ["Display Plans"])))

        with it("keeps the stories an epic holds beside its sub-epics"):
            expect([story["n"] for story in self.tree[0]["e"][0]["s"]]).to(equal(["View Cart"]))

    with context("rendered from an outline whose steps name its Examples columns"):
        with it("writes each row's values by its name, in plain words, so a picked row can fill the steps"):
            explorer = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(_outline_map()))["project/screens/explorer.dc.html"]
            tree = json.loads(explorer.split("tree() {\nreturn ", 1)[1].split(";\n}", 1)[0])
            expect(tree[0]["s"][0]["c"][0]["r"]).to(equal({
                "missing email": {"example": "missing email", "message": "email required"},
                "password missing letters": {"example": "password missing letters", "message": "password rule"},
            }))

    with context("rendered from steps that mark their terms"):
        with before.each:
            story_map = _story_map()
            scenario = story_map.epics[0].epics[0].stories[0].scenarios[0]
            scenario.steps.append(Step("the ++[cart](../cart.md)++ holds **Line 1** · ++Atlas++", StepType.THEN, 3))
            self.explorer = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(_catalog_screen()))).render(story_map))["project/screens/explorer.dc.html"]

        with it("writes each step in the explorer as plain words, without its term marks"):
            expect(self.explorer).to(contain("Then the cart holds Line 1 · Atlas"))
            expect(self.explorer).not_to(contain("++Atlas++"))
            expect(self.explorer).not_to(contain("**Line 1**"))

    with context("rendered from steps that link their domain terms to the domain model"):
        with before.all:
            self.root = Path(tempfile.mkdtemp(prefix="cdd-story-canvas-terms-"))
            (self.root / "domain").mkdir()
            (self.root / "domain" / "domain-model.md").write_text(_DOMAIN_MODEL, encoding="utf-8")
            screen = Screen("Plan catalog", 1)
            screen.prototype = "plan-catalog.dc.html"
            screen.show_story("Choose Plan")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(screen), files_root=self.root)).render(_linked_map()))
            self.explorer = files["project/screens/explorer.dc.html"]
            self.groups = _tree_of(self.explorer)[0]["e"][0]["s"][0]["c"][0]["t"]
            self.cards = json.loads(self.explorer.split("classCards() {\nreturn ", 1)[1].split(";\n}", 1)[0])

        with after.all:
            shutil.rmtree(self.root, ignore_errors=True)

        with it("gives each step group the linked terms its steps name, each with the key of its class card"):
            expect(self.groups[1]["m"]).to(equal({"cart": "domain/domain-model.md#cart-aggregate-root-entity",
                                                  "line": "domain/domain-model.md#line-entity"}))

        with it("finds a linked term in a Given as well as a When or Then"):
            expect(self.groups[0]["m"]).to(equal({"cart": "domain/domain-model.md#cart-aggregate-root-entity"}))

        with it("opens the class a term is linked to most often when it links to more than one"):
            expect(self.groups[0]["m"]["cart"]).to(equal("domain/domain-model.md#cart-aggregate-root-entity"))

        with it("matches whole words only, so a word holding a term is no term"):
            expect(self.groups[1]["x"]).to(contain("carts"))
            expect(list(self.groups[1]["m"])).to(equal(["cart", "line"]))

        with it("gives epics, stories and scenarios no terms"):
            story = _tree_of(self.explorer)[0]["e"][0]["s"][0]
            expect(("m" in story, "m" in story["c"][0])).to(equal((False, False)))

        with it("writes each class card once, by its key, with the heading as its title and stereotypes in guillemets"):
            expect({key: card["title"] for key, card in self.cards.items()}).to(equal({
                "domain/domain-model.md#cart-aggregate-root-entity": "Cart «Aggregate Root» «Entity»",
                "domain/domain-model.md#line-entity": "Line «Entity»",
            }))

        with it("writes the card's text as the model's section, up to the next heading as high, each rule as a dashed line and tabs as spaces"):
            expect(self.cards["domain/domain-model.md#cart-aggregate-root-entity"]["text"]).to(equal(
                "A cart holds the lines a Customer picks.\n\n– – –\n\n+ add(line)\n    + total"))

        with it("gives a group whose steps are realized their realizations, each under its line"):
            expect(self.groups[0]["z"]).to(equal(
                "Given the Customer has a cart\nCart.create()\n\nWhen the Customer opens My Paradise\nCatalog.open()\n  -> Plan.list()"))

        with it("gives a group whose steps have no realization none"):
            expect("z" in self.groups[1]).to(equal(False))

    with context("drawn as the explorer's page"):
        with before.each:
            self.page = self.files["project/screens/explorer.dc.html"]

        with it("draws each row as a block that acts as a button, so a term's click inside it reaches the row"):
            expect(self.page).to(contain('<div role="button" tabindex="0" class="{{row.cls}}" onClick="{{row.pick}}">'))
            expect(self.page).not_to(contain('<button type="button" class="{{row.cls}}"'))

        with it("draws each linked term as a span naming its card"):
            expect(self.page).to(contain('<span class="sm-term" data-card="{{part.card}}">{{part.text}}</span>'))

        with it("puts the class card below the scrolling list of steps, never over it"):
            rows_end = self.page.index("</sc-for>\n</div>", self.page.index('list="{{rows}}"'))
            expect(rows_end < self.page.index('class="sm-card-divider"') < self.page.index('class="sm-card"')).to(be(True))

        with it("closes the card with its ×"):
            expect(self.page).to(contain('onClick="{{closeCard}}">×</span>'))

        with it("puts a divider above the card that drags to resize it"):
            expect(self.page).to(contain('<div class="sm-card-divider" role="separator" aria-orientation="horizontal" title="Drag to resize" onPointerDown="{{startCardResize}}"></div>'))
            expect(self.page).to(contain(".sm-card-divider{flex:0 0 auto;height:10px;cursor:row-resize"))

        with it("shows a realization toggle under a step group that has one"):
            expect(self.page).to(contain('<sc-if value="{{row.hasRealization}}" hint-placeholder-val="{{ false }}"><span class="sm-real-toggle"'))

    with context("rendered from a story with no screens"):
        with it("gives that story no thumbnail"):
            expect(self.files["project/Main.dc.html"]).not_to(contain("story=Create%20Credentials"))

    with context("rendered with more screens than Claude Design keeps pages for"):
        with before.each:
            screens = []
            for number in range(45):
                screen = Screen(f"Screen {number}", number + 1)
                screen.prototype = f"screens/screen-{number}.dc.html"
                screen.show_story("Choose Plan")
                screens.append(screen)
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(*screens))).render(_story_map()))
            self.canvas = json.loads(files["project/canvas.json"])

        with it("keeps within the 40 pages a canvas holds"):
            expect(len(self.canvas["pages"]) <= 40).to(be(True))

        with it("puts every board on a page the canvas has, so none falls back onto the story map"):
            pages = {page["id"] for page in self.canvas["pages"]}
            expect([name for name, board in self.canvas["boards"].items() if board["page"] not in pages]).to(equal([]))

        with it("lays the boards that share a page side by side, none covering another"):
            boards = list(self.canvas["boards"].values())
            covering = [(a["title"], b["title"]) for i, a in enumerate(boards) for b in boards[i + 1:]
                        if a["page"] == b["page"] and a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]]
            expect(covering).to(equal([]))

    with context("rendered into a project whose prototype screen loads its design system's scripts"):
        with before.each:
            workspace = Path(tempfile.mkdtemp(prefix="cdd-story-canvas-"))
            screens = workspace / "project" / "screens"
            screens.mkdir(parents=True)
            (screens / "plan-catalog.dc.html").write_text(
                '<script src="./support.js"></script>\n<link rel="stylesheet" href="../ds/app/tokens.css">\n'
                '<script src="../ds/app/bundle.js"></script>\n<script src="../flow.js"></script>',
                encoding="utf-8",
            )
            screen = _catalog_screen()
            screen.prototype = "screens/plan-catalog.dc.html"
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(workspace=str(workspace), ux_map=_ux_map(screen))).render(_story_map()))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("loads the scripts the screen loads, so the screen's components draw inside the explorer"):
            expect(self.explorer).to(contain('<script src="../ds/app/bundle.js"></script>'))
            expect(self.explorer).to(contain('<script src="../flow.js"></script>'))

        with it("keeps the screen's stylesheets"):
            expect(self.explorer).to(contain('<link rel="stylesheet" href="../ds/app/tokens.css">'))

    with context("rendered into a project whose story screen is a phone screen"):
        with before.all:
            self.workspace = Path(tempfile.mkdtemp(prefix="cdd-story-canvas-size-"))
            screens = self.workspace / "project" / "screens"
            screens.mkdir(parents=True)
            phone = StoryScreen(title="Plan catalog", story="Choose Plan", markup=WrittenMarkup(head="", body="<main></main>"),
                                positions={"See the plan catalog": [{}]}, width=390, height=844)
            (screens / "plan-catalog.dc.html").write_text(phone.html, encoding="utf-8")
            screen = _catalog_screen()
            screen.prototype = "screens/plan-catalog.dc.html"
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(workspace=str(self.workspace), ux_map=_ux_map(screen))).render(_story_map()))
            self.sized_canvas = json.loads(files["project/canvas.json"])
            self.sized_explorer = files["project/screens/explorer.dc.html"]

        with after.all:
            shutil.rmtree(self.workspace, ignore_errors=True)

        with it("sizes the screen's own board to the screen, not to a desktop"):
            board = self.sized_canvas["boards"]["screens/plan-catalog.dc.html"]
            expect((board["w"], board["h"])).to(equal((390, 844)))

        with it("imports the screen across the pane's width, so the screen's own frame centres itself in it"):
            expect(self.sized_explorer).to(contain('hint-size="390px,844px" style="display: block; width: 100%"></dc-import>'))

        with it("draws the screen on the explorer's dark background, not white"):
            expect(self.sized_explorer).to(contain("height: 100%; background: #0B0B0B; overflow: auto"))

    with context("rendered with a screen that names a scenario, and a story whose screen names only the story"):
        with before.each:
            select_plan = Screen("Select plan", 2)
            select_plan.prototype = "select-plan.dc.html"
            select_plan.show_scenario("Choose Plan \u203a Pick from the cart")
            credentials = Screen("Create account", 3)
            credentials.prototype = "create-credentials.dc.html"
            credentials.show_story("Create Credentials")
            story_map = _story_map()
            choose_plan = story_map.epics[0].epics[0].stories[0]
            from_cart = Scenario("Pick from the cart", 2)
            from_cart.steps.append(Step("the cart has no plan", StepType.GIVEN, 1))
            choose_plan.scenarios.append(from_cart)
            create = story_map.epics[0].epics[0].stories[1]
            display = Scenario("Display Create Account", 1)
            display.steps.append(Step("the User opens sign-up", StepType.WHEN, 1))
            create.scenarios.append(display)
            refused = Scenario("Email already registered", 2)
            refused.steps.append(Step("an account exists", StepType.GIVEN, 1))
            create.scenarios.append(refused)
            shot = Screen("an account exists", 4)
            shot.image = "shots/email-already-registered.png"
            shot.show_step("Create Credentials › Email already registered › an account exists")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(_catalog_screen(), select_plan, credentials, shot))).render(story_map))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("shows a scenario whose steps show no screen on its own shownOn screen"):
            expect(self.explorer).to(contain('"n": "Pick from the cart", "b": false, "p": "select-plan"'))

        with it("shows a scenario with no screen of its own on its story's screen"):
            expect(self.explorer).to(contain('"n": "Display Create Account", "b": false, "p": "create-credentials"'))

        with it("shows a scenario whose steps have only a screenshot on its story's screen, not the screenshot"):
            expect(self.explorer).to(contain('"n": "Email already registered", "b": false, "p": "create-credentials"'))

    with context("rendered with the story code's locations"):
        with before.each:
            sources = {"Choose Plan": "tests/select_plan.story.shared.ts:69",
                       "Choose Plan \u203a See the plan catalog": "tests/select_plan.story.shared.ts:73"}
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(_catalog_screen()), sources=sources)).render(_story_map()))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("gives the explorer each story's and scenario's location, for the copy-to-open request"):
            expect(self.explorer).to(contain('"n": "Choose Plan", "f": "tests/select_plan.story.shared.ts:69"'))
            expect(self.explorer).to(contain('"f": "tests/select_plan.story.shared.ts:73"'))

    with context("rendered from a canvas the caller already holds"):
        with before.each:
            self.held = ClaudeDesignStoryMap().copy_of(_story_map())
            canvas = ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(_catalog_screen()), sources={"Choose Plan": "tests/select_plan.story.shared.ts:69"}))
            canvas.render(self.held)

        with it("leaves the caller's canvas without the screens of that render"):
            expect(self.held.screen_map.screens).to(equal([]))

        with it("leaves the caller's canvas without the sources of that render"):
            expect(self.held.sources).to(equal({}))

        with it("keeps each canvas's sources apart"):
            expect(ClaudeDesignStoryMap().sources).not_to(be(self.held.sources))

    with context("rendered with a screen that serves a story"):
        with before.each:
            screen = _catalog_screen()
            screen.show_story("Choose Plan")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map(screen))).render(_story_map()))
            self.canvas = json.loads(files["project/canvas.json"])
            self.panel = files["project/context/plan-catalog.dc.html"]

        with it("puts a read-only story panel beside the screen on its page"):
            board = self.canvas["boards"]["context/plan-catalog.dc.html"]
            expect(board["page"]).to(equal("screen-plan-catalog"))
            expect(board["x"]).to(equal(1680))
            expect("is_interactive" in board).to(equal(False))

        with it("opens the screen's story to its scenarios and steps, and greys the rest"):
            expect(self.panel).to(contain('<div class="cx-story cx-on">Choose Plan</div>'))
            expect(self.panel).to(contain('<div class="cx-scenario">See the plan catalog</div>'))
            expect(self.panel).to(contain('<div class="cx-story">Create Credentials</div>'))
