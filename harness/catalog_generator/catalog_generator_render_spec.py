"""BDD specs for the catalog's pages: each practice, fidelity, action, and utility page, the hub, and the grids."""
import tempfile
from pathlib import Path
from unittest.mock import patch

from expects import be_true, equal, expect
from mamba import before, context, description, it

from harness.catalog_generator.catalog_generator import (
    ActionPage,
    Catalog,
    CatalogPractice,
    FidelityPage,
    GitCitation,
    LifecycleAction,
    PracticePage,
    SkillSlashName,
    Utility,
    UtilityPage,
)
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.actions.diagnose.diagnose import Diagnose
from tools.echo.echo import Echo

_REPO_URL = "https://github.com/org/repo"
_REF = "abc123"
_CITATION = GitCitation(_REPO_URL, _REF)


with description("a lifecycle action's page"):
    with before.all:
        actions = {action.name: action for action in LifecycleAction.load_all()}
        self.page = ActionPage(actions["repair"]).body

    with it("should carry the Lifecycle action badge"):
        expect("Lifecycle action" in self.page).to(be_true)

    with it("should say the action is used by its name in a request"):
        expect("used as action: <code>repair</code>" in self.page).to(be_true)

    with it("should show its markdown instructions before its module overview"):
        expect(self.page.find("Markdown instructions") < self.page.find("Module overview")).to(be_true)

    with it("should render its guide as HTML rather than a markdown fence"):
        expect('class="language-markdown"' in self.page).to(equal(False))


with description("a fidelity's page"):
    with before.all:
        self.actions = LifecycleAction.load_all()
        practice = CatalogPractice(Ddd(), skills=SkillSlashName([]))
        tactics = next(shown for shown in practice.shown_fidelities if shown.name == "tactics")
        self.page = FidelityPage(practice, tactics, _CITATION, self.actions).body

    with it("should open with the chat command, escaped for a browser"):
        expect("/ddd &lt;action&gt; tactics" in self.page).to(be_true)

    with it("should link every lifecycle action"):
        expect(all(f'<a href="../{action.href}">{action.name}</a>' in self.page for action in self.actions)).to(be_true)

    with it("should show the template for its default format"):
        expect("Default template" in self.page).to(be_true)


with description("a practice's page"):
    with before.all:
        self.page = PracticePage(CatalogPractice(Ddd(), skills=SkillSlashName([]))).body

    with it("should show the practice's name"):
        expect("Domain-Driven Design" in self.page).to(be_true)

    with it("should show the practice's shared rules"):
        expect("ubiquitous-language-everywhere" in self.page).to(be_true)

    with it("should link each fidelity page in declared stage order"):
        section = self.page[self.page.find('aria-label="Fidelities"'):]
        positions = [section.find(f">{label}<") for label in ("bounded-context", "model", "tactics")]
        expect(positions == sorted(positions) and -1 not in positions).to(be_true)

    with it("should give each fidelity the opening of its overview"):
        expect("Draw where language changes" in self.page).to(be_true)


with description("a utility's page"):
    with it("should name the utility"):
        expect("diagnose" in UtilityPage(Utility(Diagnose)).body).to(be_true)

    with context("that shares its module card with other toolsets"):
        with it("should show the card of the module its package belongs to"):
            expect("they share this one card" in UtilityPage(Utility(Echo)).body).to(be_true)


with description("a generated catalog"):
    with context("given the repository's address and commit"):
        with it("should not ask git for them"):
            with patch.object(GitCitation, "from_checkout", side_effect=AssertionError("git was run")):
                expect(Catalog(repo_url=_REPO_URL, ref=_REF).citation.ref).to(equal(_REF))

    with context("that has been rendered"):
        with before.all:
            self.tmp = Path(tempfile.mkdtemp())
            Catalog(repo_url=_REPO_URL, ref=_REF, out_root=str(self.tmp))._render_catalog()
            self.index_html = (self.tmp / "index.html").read_text(encoding="utf-8")

        with it("should put the CDD header above the practices on the hub board"):
            expect(self.index_html.find("context-driven-delivery") < self.index_html.find("stories")).to(be_true)

        with it("should show the Actions and Utilities rows below the board"):
            positions = [self.index_html.find(mark) for mark in ('id="catalog-kanban"', "Actions</h3>", "Utilities</h3>")]
            expect(positions == sorted(positions)).to(be_true)

        with it("should ship the Foundry styles into the catalog"):
            styles = ("site.css", "foundry-catalog.css", "cdd-board.css")
            expect(all((self.tmp / "commons" / style).is_file() for style in styles)).to(be_true)

        with it("should ship the approach page's script into the catalog"):
            expect((self.tmp / "commons" / "catalog-approach.js").is_file()).to(be_true)

        with it("should show the install steps below the board"):
            expect(self.index_html.find("Utilities</h3>") < self.index_html.find("catalog-install-heading")).to(be_true)

        with it("should link the install script the steps tell a person to run"):
            expect(f'{_REPO_URL}/blob/{_REF}/scripts/install.py' in self.index_html).to(be_true)

        with it("should link the approach from the hero"):
            expect('class="page-hero__approach-btn" href="cdd-approach.html"' in self.index_html).to(be_true)

        with it("should write the approach page"):
            expect("Iterate and Learn" in (self.tmp / "cdd-approach.html").read_text(encoding="utf-8")).to(be_true)

        with it("should write the README page"):
            expect("Basic usage" in (self.tmp / "readme.html").read_text(encoding="utf-8")).to(be_true)

        with it("should write the workflow page with its action links"):
            workflow = (self.tmp / "workflow.html").read_text(encoding="utf-8")
            expect('href="actions/partition.html"' in workflow).to(be_true)

        with it("should leave the workflow page off the hub"):
            expect('href="workflow.html"' in self.index_html).to(equal(False))

        with it("should list the context tools on their grid page"):
            expect("Domain-Driven Design" in (self.tmp / "context-tools.html").read_text(encoding="utf-8")).to(be_true)

        with it("should list the lifecycle actions on their grid page"):
            expect('href="actions/generate.html"' in (self.tmp / "actions.html").read_text(encoding="utf-8")).to(be_true)

        with it("should leave a toolset annotated noCatalog off the utilities grid"):
            expect("diagnose" in (self.tmp / "tools.html").read_text(encoding="utf-8")).to(equal(False))
