"""Acceptance tests for the "Render Self-Contained Catalog Pages" epic - one
`it` per sketch story's single main-flow scenario.
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import before, description, it

from harness.catalog_generator.catalog_generator import (
    Catalog,
    CatalogAction,
    CatalogContextTool,
    CatalogFidelity,
    CatalogTool,
    CatalogPractice,
    CatalogUtility,
    RegistryEntry,
    SkillSlashName,
    resolve_lifecycle_actions,
)
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.actions.diagnose.diagnose import Diagnose

_REPO_URL = "https://github.com/org/repo"
_REF = "abc123"


with description("Render Action Page With Fixed Sections"):
    with description("given an action's own name, tools-called list, guide, and module overview"):
        with before.all:
            self.actions = {action.name: action for action in resolve_lifecycle_actions()}
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {name: action.href for name, action in self.actions.items()}
            self.catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            self.page = self.catalog_action.generate_catalog(self.actions["repair"])

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
            self.lifecycle_actions = resolve_lifecycle_actions()
            self.owner = Ddd()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {action.name: f"../{action.href}" for action in self.lifecycle_actions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            self.catalog_fidelity = CatalogFidelity(_REPO_URL, _REF, catalog_action, self.lifecycle_actions)
            practice = CatalogPractice(self.owner, skills=SkillSlashName([]))
            self.page = self.catalog_fidelity.generate_catalog(practice, self.owner.fidelities["tactics"])

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
            self.lifecycle_actions = resolve_lifecycle_actions()
            self.owner = Ddd()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {action.name: f"../{action.href}" for action in self.lifecycle_actions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            catalog_fidelity = CatalogFidelity(_REPO_URL, _REF, catalog_action, self.lifecycle_actions)
            self.catalog_context_tool = CatalogContextTool(_REPO_URL, _REF, catalog_fidelity)
            practice = CatalogPractice(self.owner, skills=SkillSlashName([]))
            self.page = self.catalog_context_tool.generate_catalog(practice)

        with it("shows the practice name, shared rules, and purpose prose"):
            expect("Domain-Driven Design" in self.page).to(be_true)
            expect("bounded contexts" in self.page.lower() or "Apply" in self.page).to(be_true)
            expect("ubiquitous-language-everywhere" in self.page).to(be_true)

        with it("links each fidelity page, in declared stage order"):
            section = self.page[self.page.find('aria-label="Fidelities"'):]
            bounded_at = section.find("bounded-context")
            model_at = section.find(">model<")
            if model_at < 0:
                model_at = section.find("model")
            tactics_at = section.find(">tactics<")
            if tactics_at < 0:
                tactics_at = section.find("tactics")
            expect(bounded_at < model_at < tactics_at).to(be_true)
            expect("cap-card" in section).to(equal(False))
            expect("Draw where language changes" in section).to(be_true)


with description("Render Utility Page"):
    with description("given a utility's Purpose prose and its optional {utility}.md guide"):
        with before.all:
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            lifecycle_actions = resolve_lifecycle_actions()
            hrefs = {action.name: action.href for action in lifecycle_actions}
            catalog_action = CatalogAction(_REPO_URL, _REF, catalog_tool, hrefs)
            self.catalog_utility = CatalogUtility(_REPO_URL, _REF, catalog_tool, catalog_action)
            diagnose = RegistryEntry("diagnose", Diagnose.__module__, "Diagnose", Diagnose)
            self.page = self.catalog_utility.generate_catalog(diagnose)

        with it("shows the utility's Purpose/Seam prose"):
            expect("diagnose" in self.page).to(be_true)
            expect(len(self.page) > 0).to(be_true)


with description("Render Hub Board With Actions And Utilities Rows"):
    with description("given the CDD header row, the five context-tool rows, and the assembled rows"):
        with before.all:
            self.tmp = Path(tempfile.mkdtemp())
            lifecycle_actions = resolve_lifecycle_actions()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {action.name: action.href for action in lifecycle_actions}
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

        with it("links the approach as a hero button and writes approach plus README pages"):
            approach_at = self.index_html.find('href="cdd-approach.html"')
            board_at = self.index_html.find('id="catalog-kanban"')
            expect(approach_at != -1).to(be_true)
            expect(approach_at < board_at).to(be_true)
            expect('page-hero__approach-btn' in self.index_html).to(be_true)
            expect('href="readme.html"' in self.index_html).to(equal(False))
            approach_html = (self.tmp / "cdd-approach.html").read_text(encoding="utf-8")
            readme_html = (self.tmp / "readme.html").read_text(encoding="utf-8")
            expect("page-hero" in approach_html).to(be_true)
            expect("approach-stage-row" in approach_html).to(be_true)
            expect("approach-detail" in approach_html).to(be_true)
            expect("approach-principles" in approach_html).to(be_true)
            expect("Context Driven Delivery Practices" in approach_html).to(be_true)
            expect("Product Engineering" in approach_html).to(be_true)
            expect("Iterate and Learn" in approach_html).to(be_true)
            expect("page-hero" in readme_html).to(be_true)
            expect("Basic usage" in readme_html).to(be_true)

        with it("writes workflow.html and leaves it off the hub under the board"):
            expect("catalog-workflow-heading" in self.index_html).to(equal(False))
            expect('href="workflow.html"' in self.index_html).to(equal(False))
            expect((self.tmp / "workflow.html").is_file()).to(be_true)
            workflow_html = (self.tmp / "workflow.html").read_text(encoding="utf-8")
            expect("CDD Workflow" in workflow_html).to(be_true)
            expect("Scenario 1" in workflow_html).to(be_true)
            expect('href="actions/partition.html"' in workflow_html).to(be_true)


with description("Render Flat Grid Pages"):
    with description("given every rendered tool, fidelity, action, and utility card"):
        with before.all:
            self.tmp = Path(tempfile.mkdtemp())
            lifecycle_actions = resolve_lifecycle_actions()
            catalog_tool = CatalogTool(_REPO_URL, _REF)
            hrefs = {action.name: action.href for action in lifecycle_actions}
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
            self.catalog._render_catalog()

        with it("lists every context tool, action, and utility card on its own grid page"):
            for page_name, expected in (
                ("context-tools.html", "Domain-Driven Design"),
                ("actions.html", "createRule"),
            ):
                content = (self.tmp / page_name).read_text(encoding="utf-8")
                expect(expected in content).to(be_true)
            tools_html = (self.tmp / "tools.html").read_text(encoding="utf-8")
            expect("diagnose" in tools_html).to(equal(False))
