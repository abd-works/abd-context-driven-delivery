"""Acceptance tests for the "Render Self-Contained Catalog Pages" epic - one
`it` per sketch story's single main-flow scenario.
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import before, description, it

from catalog_generator.catalog_generator import (
    Catalog,
    CatalogAction,
    CatalogContextTool,
    CatalogFidelity,
    CatalogTool,
    CatalogUtility,
    CatalogFidelityGuidance,
    load_registry,
    ActionResolution,
    resolve_lifecycle_actions,
)
from practices.ddd.ddd import Ddd
from diagnose.diagnose import Diagnose

_REPO_URL = "https://github.com/org/repo"
_REF = "abc123"


with description("Render Action Page With Fixed Sections"):
    with description("given an action's own name, tools-called list, guide, and module overview"):
        with before.all:
            self.resolutions = {r.name: r for r in resolve_lifecycle_actions()}
            self.owner = ActionResolution.live_owner()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {name: f"actions/{name}.html" for name in self.resolutions}
            self.catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            resolution = self.resolutions["repair"]
            action = self.owner.agent_tools["repair"]
            self.catalog_action.action = action
            self.catalog_action.owner = self.owner
            self.catalog_action.source_dir = resolution.source_dir
            self.page = self.catalog_action.generate_catalog()

        with it("carries the Lifecycle action badge and a one-line used-as note"):
            expect("Lifecycle action" in self.page).to(be_true)
            expect("used as action:" in self.page).to(be_true)
            expect("<code>repair</code>" in self.page).to(be_true)
            expect('id="raw-manifest"' in self.page).to(equal(False))

        with it("shows calls, markdown instructions, and module overview in order — no Code dump"):
            calls_at = self.page.find("Tools / actions called")
            md_at = self.page.find("Markdown instructions")
            overview_at = self.page.find("Module overview")
            expect(calls_at < md_at < overview_at).to(be_true)
            expect("<h2>Code</h2>" in self.page).to(equal(False))

        with it("renders guide and module-context as HTML, not a raw markdown fence"):
            expect('class="language-markdown"' in self.page).to(equal(False))
            expect("fidelity-guidance" in self.page).to(be_true)


with description("Render Fidelity Page With Quick-Invoke And Illustrated Example"):
    with description("given a fidelity's skill name, its own key, and the ten lifecycle actions"):
        with before.all:
            self.resolutions = resolve_lifecycle_actions()
            self.owner = Ddd()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {r.name: f"../actions/{r.name}.html" for r in self.resolutions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            self.catalog_fidelity = CatalogFidelity(_REPO_URL, _REF, catalog_action, self.resolutions)
            guidances = CatalogFidelityGuidance.scrape(Ddd)
            tactics = next(g for g in guidances if g.key == "tactics")
            self.catalog_fidelity.skill_name = "ddd"
            self.catalog_fidelity.fidelity_name = "tactics"
            self.catalog_fidelity.owner = self.owner
            self.catalog_fidelity.guidance = tactics.guidance
            self.page = (
                self.catalog_fidelity.section_0_html()
                + self.catalog_fidelity.generate_catalog()
            )

        with it("opens with the /{skill} <action> {fidelity} command line (HTML-escaped for a real browser)"):
            # A browser renders `<action>` visibly only if the HTML source
            # escapes it - this is the literal command line's real markup.
            expect("/ddd &lt;action&gt; tactics" in self.page).to(be_true)

        with it("lists all ten lifecycle actions as hyperlinks"):
            for name in (
                "partition", "grill", "sketch", "generate", "document",
                "iterate", "validate", "satisfy", "repair", "createRule",
            ):
                expect(f">{name}<" in self.page).to(be_true)

        with it("does not carry a raw manifest subsidiary link in the header"):
            header = self.page[: self.page.find("</header>")]
            expect("Raw manifest format" in header).to(equal(False))
            expect("../manifests/" in header).to(equal(False))

        with it("falls back the illustrated-example panel to the no-example message when unconfigured"):
            expect("No illustrated example configured yet" in self.page).to(be_true)


with description("Render Context Tool Page"):
    with description("given one toolset's Purpose prose and its resolved fidelity cards"):
        with before.all:
            self.resolutions = resolve_lifecycle_actions()
            self.owner = Ddd()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {r.name: f"../actions/{r.name}.html" for r in self.resolutions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            catalog_fidelity = CatalogFidelity(_REPO_URL, _REF, catalog_action, self.resolutions)
            self.catalog_context_tool = CatalogContextTool(_REPO_URL, _REF, catalog_fidelity)
            guidances = CatalogFidelityGuidance.scrape(Ddd)
            self.catalog_context_tool.owner = self.owner
            self.catalog_context_tool.display_name = "Domain-Driven Design"
            self.catalog_context_tool.skill_name = "ddd"
            self.catalog_context_tool.guidances = guidances
            self.page = self.catalog_context_tool.generate_catalog()

        with it("shows the tool's badge and Purpose prose"):
            expect("Domain-Driven Design" in self.page).to(be_true)
            expect("bounded contexts" in self.page.lower() or "Apply" in self.page).to(be_true)

        with it("shows one card per fidelity, in declared stage order"):
            bounded_at = self.page.find("bounded-context")
            building_at = self.page.find("building-blocks")
            tactics_at = self.page.find(">tactics<")
            if tactics_at < 0:
                tactics_at = self.page.find("tactics")
            expect(bounded_at < building_at < tactics_at).to(be_true)


with description("Render Utility Page"):
    with description("given a utility's Purpose prose and its optional {utility}.md guide"):
        with before.all:
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            resolutions = resolve_lifecycle_actions()
            hrefs = {r.name: f"actions/{r.name}.html" for r in resolutions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            self.catalog_utility = CatalogUtility(_REPO_URL, _REF, catalog_tool, catalog_action)
            self.catalog_utility.owner = Diagnose()
            self.catalog_utility.display_name = "diagnose"
            self.page = self.catalog_utility.generate_catalog()

        with it("shows the utility's Purpose/Seam prose"):
            expect("diagnose" in self.page).to(be_true)
            expect(len(self.page) > 0).to(be_true)


with description("Render Hub Board With Actions And Utilities Rows"):
    with description("given the CDD header row, the five context-tool rows, and the assembled rows"):
        with before.all:
            self.tmp = Path(tempfile.mkdtemp())
            context_tool_entries, utility_entries = load_registry()
            lifecycle_actions = resolve_lifecycle_actions()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {r.name: f"actions/{r.name}.html" for r in lifecycle_actions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            catalog_fidelity = CatalogFidelity(_REPO_URL, _REF, catalog_action, lifecycle_actions)
            catalog_context_tool = CatalogContextTool(_REPO_URL, _REF, catalog_fidelity)
            catalog_utility = CatalogUtility(_REPO_URL, _REF, catalog_tool, catalog_action)
            self.catalog = Catalog(
                repo_url=_REPO_URL,
                ref=_REF,
                out_root=str(self.tmp),
                catalog_context_tool=catalog_context_tool,
                catalog_action=catalog_action,
                catalog_utility=catalog_utility,
            )
            self.action_owner = ActionResolution.live_owner()
            self.catalog._context_tool_entries = context_tool_entries
            self.catalog._utility_entries = utility_entries
            self.catalog._lifecycle_actions = lifecycle_actions
            self.catalog._action_owner = self.action_owner
            self.catalog._render_catalog()
            self.index_html = (self.tmp / "index.html").read_text(encoding="utf-8")

        with it("writes index.html with the CDD header row on top"):
            expect(
                self.index_html.find("context-driven-delivery")
                < self.index_html.find("stories")
            ).to(be_true)

        with it("shows the Actions row and the Utilities row below the board"):
            board_at = self.index_html.find('id="catalog-kanban"')
            actions_at = self.index_html.find("Actions</h3>")
            utilities_at = self.index_html.find("Utilities</h3>")
            expect(board_at < actions_at < utilities_at).to(be_true)

        with it("ships Foundry commons CSS into the output catalog"):
            expect((self.tmp / "commons" / "site.css").is_file()).to(be_true)
            expect((self.tmp / "commons" / "foundry-catalog.css").is_file()).to(be_true)
            expect((self.tmp / "commons" / "cdd-board.css").is_file()).to(be_true)
            expect('href="commons/site.css' in self.index_html).to(be_true)

        with it("does not write manifest YAML under the output catalog"):
            expect((self.tmp / "manifests").exists()).to(equal(False))

        with it("does not ship a maintainer regen-command note on the public hub"):
            expect("generate_cdd_catalog" in self.index_html).to(equal(False))
            expect("regen-note" in self.index_html).to(equal(False))

        with it("shows Install steps under the board with repo URL and Harness generate"):
            expect("catalog-install-heading" in self.index_html).to(be_true)
            expect("https://github.com/org/repo" in self.index_html or _REPO_URL in self.index_html).to(be_true)
            expect("harness/harness.py" in self.index_html).to(be_true)
            expect("action <code>generate</code>" in self.index_html).to(be_true)
            utilities_at = self.index_html.find("Utilities</h3>")
            install_at = self.index_html.find("catalog-install-heading")
            expect(utilities_at < install_at).to(be_true)

        with it("links the CDD Workflow page underneath the board and writes workflow.html"):
            expect('href="workflow.html"' in self.index_html).to(be_true)
            expect("catalog-workflow-heading" in self.index_html).to(be_true)
            workflow_at = self.index_html.find("catalog-workflow-heading")
            install_at = self.index_html.find("catalog-install-heading")
            expect(workflow_at < install_at).to(be_true)
            expect((self.tmp / "workflow.html").is_file()).to(be_true)
            workflow_html = (self.tmp / "workflow.html").read_text(encoding="utf-8")
            expect("CDD Workflow" in workflow_html).to(be_true)
            expect("Scenario 1" in workflow_html).to(be_true)
            expect('href="actions/partition.html"' in workflow_html).to(be_true)


with description("Render Flat Grid Pages"):
    with description("given every rendered tool, fidelity, action, and utility card"):
        with before.all:
            self.tmp = Path(tempfile.mkdtemp())
            context_tool_entries, utility_entries = load_registry()
            lifecycle_actions = resolve_lifecycle_actions()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {r.name: f"actions/{r.name}.html" for r in lifecycle_actions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            catalog_fidelity = CatalogFidelity(_REPO_URL, _REF, catalog_action, lifecycle_actions)
            catalog_context_tool = CatalogContextTool(_REPO_URL, _REF, catalog_fidelity)
            catalog_utility = CatalogUtility(_REPO_URL, _REF, catalog_tool, catalog_action)
            self.catalog = Catalog(
                repo_url=_REPO_URL,
                ref=_REF,
                out_root=str(self.tmp),
                catalog_context_tool=catalog_context_tool,
                catalog_action=catalog_action,
                catalog_utility=catalog_utility,
            )
            self.action_owner = ActionResolution.live_owner()
            self.catalog._context_tool_entries = context_tool_entries
            self.catalog._utility_entries = utility_entries
            self.catalog._lifecycle_actions = lifecycle_actions
            self.catalog._action_owner = self.action_owner
            self.catalog._render_catalog()

        with it("lists every context tool, action, and utility card on its own grid page"):
            for page_name, expected in (
                ("context-tools.html", "Context-driven delivery"),
                ("actions.html", "createRule"),
                ("tools.html", "diagnose"),
            ):
                content = (self.tmp / page_name).read_text(encoding="utf-8")
                expect(expected in content).to(be_true)
