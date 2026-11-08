"""catalog_generator - the CDD HTML catalog: a page for every practice, fidelity, lifecycle action, and utility, the
board that links them, and the approach page.

The catalog reads the live object model - the practice catalogue's ``PracticeGuidance`` and ``FidelityGuidance``, the
action catalogue's actions and their live tools, and the toolsets the installer finds - so there is no separate scraped
schema. Each page class below renders one of those objects; ``Catalog`` writes them all with the Foundry chrome.
"""
from __future__ import annotations

import html
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.agent_tools.agent_tools import tool_subject
from harness.catalog_generator.approach_copy import APPROACH_MARKDOWN, ApproachCopy
from harness.catalog_generator.approach_page import ApproachPage
from harness.catalog_generator.brand import Brand
from harness.catalog_generator.catalog_examples import CatalogFidelity
from harness.catalog_generator.catalog_practice import CatalogPractice
from harness.catalog_generator.git_citation import GitCitation
from harness.catalog_generator.hub_board import HubBoard
from harness.catalog_generator.markdown_html import MarkdownHtml
from harness.catalog_generator.page_shell import PageShell
from harness.catalog_generator.project_approach import ProjectApproach, ProjectFiles
from harness.guidance.action_catalogue import Action, ActionCatalogue
from harness.installation.destination import NoCatalog
from harness.installation.files import skill
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.markdown.format import Format
from harness.mcp.mcp_server import mcp
from harness.annotations.class_folder import class_folder
from harness.annotations.name import Name

_REPO_ROOT = Path(__file__).resolve().parents[2]
# The command a person runs to install CDD into an IDE, and the file it runs.
_INSTALL_COMMAND = "python scripts/install.py --ide Claude"
_INSTALL_SCRIPT = _REPO_ROOT / "scripts" / "install.py"
_HEADLINE = 'ABD <span class="accent">Context Driven Delivery</span> Harness'
_SITE_TITLE = "ABD Context Driven Delivery Harness"
_SITE_SENTENCE = (
    "Agentic tools that bring the best of agile product, delivery, and engineering practices into the age of AI. "
)
_BACK_TO_CATALOG = '<a href="index.html">Back to catalog</a>.'
_TITLE_LINE = re.compile(r"^#\s+.*\n+", re.MULTILINE)
# A template that is not itself a file of its format ends in .tpl after the format's extension.
_TEMPLATE_ENDING = ".tpl"


# -- What the catalog shows ---------------------------------------------------


# The utilities are the toolsets the installer finds in ``space`` (sessions, the board, the repository) and ``tools``
# (the sub-agent hand-off, Granola, the file manager), unless annotated @noCatalog. The harness's own toolsets are the framework the
# practices and actions run on, and the guidance under ``cdd_guidance`` has its own pages.
_UTILITY_PACKAGES = ("space.", "tools.")


class Utility:
    """One utility the catalog shows: a toolset a person uses beside the practices and actions, such as Repo."""

    def __init__(self, toolset_class: type) -> None:
        self.toolset_class = toolset_class

    @classmethod
    def load_all(cls) -> list[Utility]:
        """Every toolset class the installer loads from ``space`` and ``tools``, less those annotated ``@noCatalog``, in
        the order the installer finds them; each class says where it belongs through the module that defines it. A
        utility that cannot be imported raises rather than leaving a silent gap."""
        toolsets = RepositoryToolsets(_REPO_ROOT)
        classes = toolsets.classes()
        unloadable = [failure for failure in toolsets.unloadable if failure.reference.startswith(_UTILITY_PACKAGES)]
        if unloadable:
            raise unloadable[0]
        utilities = [toolset_class for toolset_class in classes if toolset_class.__module__.startswith(_UTILITY_PACKAGES)]
        return [cls(toolset_class) for toolset_class in utilities if not NoCatalog.annotates(toolset_class)]

    @property
    def name(self) -> str:
        """The utility's kebab-case name, such as ``file-manager``: its page and board ticket use it."""
        return Name(self.toolset_class.__name__).kebab

    @property
    def href(self) -> str:
        return f"tools/{self.name}.html"


class LifecycleAction:
    """One action as the catalog gives it a page: the action catalogue's ``Action``, the toolset that defines it built
    once, and that toolset's live ``AgentTool`` for it. The toolset's folder holds the action's guide and module
    overview."""

    def __init__(self, action: Action) -> None:
        self.action = action
        self._toolset: object | None = None

    @classmethod
    def load_all(cls) -> list[LifecycleAction]:
        """Every action in the action catalogue whose toolset has a live tool for it that the catalog shows: a toolset
        or an operation annotated ``@noCatalog`` stays out."""
        shown = [cls(action) for action in ActionCatalogue.actions() if not NoCatalog.annotates(action.toolset_class)]
        return [action for action in shown if action.tool is not None]

    @property
    def name(self) -> str:
        return self.action.name

    @property
    def toolset(self) -> object:
        """The toolset that defines the action, built once."""
        if self._toolset is None:
            self._toolset = self.action.toolset_class()
        return self._toolset

    @property
    def tool(self) -> object | None:
        """The toolset's live tool for this action; none when it has no such tool or annotates it ``@noCatalog``."""
        tools = self.toolset.tools
        tool = tools[self.name] if self.name in tools else None
        if tool is None or NoCatalog.annotates(getattr(tool, "callable", tool)):
            return None
        return tool

    @property
    def source_dir(self) -> Path:
        """The toolset's folder under ``cdd_guidance/actions``."""
        return self.action.folder

    @property
    def href(self) -> str:
        return f"actions/{self.name}.html"


class FidelityTemplate:
    """The template file a fidelity page shows: the one the fidelity reads its template from, in its default format,
    shown as a code fence with its path inside the practice folder."""

    def __init__(self, shown: CatalogFidelity) -> None:
        self.fidelity = shown.fidelity
        self.module_dir = Path(self.fidelity.practice_guidance.module_dir).resolve()

    @property
    def path(self) -> Path | None:
        return self.fidelity.template_file

    @property
    def relative_path(self) -> str:
        """The template's path inside its practice folder."""
        path = self.path
        try:
            return path.relative_to(self.module_dir).as_posix()
        except ValueError as error:
            logging.debug("Template %s is outside %s: %s", path, self.module_dir, error)
            return path.name

    @property
    def body(self) -> str:
        try:
            return self.path.read_text(encoding="utf-8")
        except OSError as error:
            logging.debug("Could not read template %s: %s", self.path, error)
            return ""

    @property
    def language(self) -> str:
        """The code-fence language the template's text is shown in: the format its extension names, read past a
        ``.tpl`` ending, so ``model.py.tpl`` is ``python``; ``text`` when it names none."""
        name = self.path.name.removesuffix(_TEMPLATE_ENDING)
        return Format.from_extension(Path(name).suffix).name or "text"

    @property
    def fence_html(self) -> str:
        return (
            f'<pre class="code-fence"><code class="language-{html.escape(self.language)}">'
            f"{html.escape(self.body)}</code></pre>"
        )


# -- Detail pages ---------------------------------------------------------------
#
# Each detail page is made for the object it shows and gives its file, title, navigation entry, body, and the practice
# and fidelity its board highlights. ``Catalog`` wraps each in the page chrome with the board on top.


class DetailPage:
    """A page one folder below the hub, about one practice, fidelity, action, or utility."""

    nav_current = ""

    @property
    def href(self) -> str:
        raise NotImplementedError

    @property
    def title(self) -> str:
        raise NotImplementedError

    @property
    def body(self) -> str:
        raise NotImplementedError

    @property
    def highlighted_practice(self) -> CatalogPractice | None:
        return None

    @property
    def highlighted_fidelity(self) -> CatalogFidelity | None:
        return None

    def _header(self, kind: str, title: str) -> str:
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">{html.escape(kind)}</p>'
            f'<h1 class="page-headline">{html.escape(title)}</h1>'
            f"</header>\n"
        )

    def _section(self, label: str, inner: str) -> str:
        return (
            f'<section class="install-block fidelity-guidance action-section" aria-label="{label}">'
            f"<h2>{label}</h2>{inner}</section>\n"
        )

    def _markdown_file(self, path: Path, missing: str) -> str:
        return MarkdownHtml(path.read_text(encoding="utf-8")).html if path.is_file() else missing


class PracticePage(DetailPage):
    """A practice's page: its practice-level sections, then each fidelity's title, opening, and examples, linking the
    fidelity's own page."""

    nav_current = "context-tools"

    def __init__(self, practice: CatalogPractice) -> None:
        self.practice = practice

    @property
    def href(self) -> str:
        return self.practice.href

    @property
    def title(self) -> str:
        return f"{self.practice.display_name} — CDD Catalog"

    @property
    def highlighted_practice(self) -> CatalogPractice:
        return self.practice

    @property
    def body(self) -> str:
        shared = MarkdownHtml(self.practice.shared_markdown).guidance_html
        guidance = (
            f'<section class="install-block fidelity-guidance" aria-label="Practice guidance">{shared}</section>\n'
            if shared.strip()
            else ""
        )
        return self._header("Practice", self.practice.display_name) + guidance + self._fidelities

    @property
    def _fidelities(self) -> str:
        entries = "".join(self._fidelity_entry(shown) for shown in self.practice.shown_fidelities)
        if not entries:
            return ""
        return (
            '<section class="install-block" aria-label="Fidelities">'
            "<h2>Fidelities</h2>"
            f'<div class="practice-fidelities">{entries}</div>'
            "</section>\n"
        )

    def _fidelity_entry(self, shown: CatalogFidelity) -> str:
        opening = MarkdownHtml(shown.opening).html if shown.opening else ""
        return (
            '<div class="practice-fidelity">'
            f'<h3 class="practice-fidelity__title">'
            f'<a href="../{html.escape(self.practice.fidelity_href(shown.fidelity))}">{html.escape(shown.label)}</a></h3>'
            f'<div class="practice-fidelity__opening">{opening}</div>'
            f"{shown.examples_html}"
            "</div>"
        )


class FidelityPage(DetailPage):
    """A fidelity's page: the chat command that runs it, its guidance with its examples under the Overview, and the
    template for its default format."""

    nav_current = "fidelities"

    def __init__(
        self,
        practice: CatalogPractice,
        fidelity: CatalogFidelity,
        citation: GitCitation,
        actions: list[LifecycleAction],
    ) -> None:
        self.practice = practice
        self.fidelity = fidelity
        self.citation = citation
        self.actions = actions

    @property
    def href(self) -> str:
        return self.practice.fidelity_href(self.fidelity.fidelity)

    @property
    def title(self) -> str:
        return f"{self.fidelity.label} — {self.practice.display_name}"

    @property
    def highlighted_practice(self) -> CatalogPractice:
        return self.practice

    @property
    def highlighted_fidelity(self) -> CatalogFidelity:
        return self.fidelity

    @property
    def body(self) -> str:
        label = self.fidelity.label
        return (
            self._header(f"{self.practice.display_name} · fidelity", label)
            + f"{self._chat_command}\n"
            f'<section class="install-block fidelity-guidance" '
            f'data-fidelity="{html.escape(self.fidelity.name)}" '
            f'aria-label="Fidelity guidance">'
            f"{self._guidance(label)}</section>\n"
            f"{self._template}\n"
        )

    @property
    def _chat_command(self) -> str:
        skill_name, name = self.practice.skill_name, self.fidelity.name
        links = ", ".join(f'<a href="../{action.href}">{action.name}</a>' for action in self.actions)
        return (
            f'<section class="install-block fidelity-invoke" aria-labelledby="fidelity-invoke-heading">'
            f'<h2 id="fidelity-invoke-heading">Chat invoke</h2>'
            f'<pre class="install-snippet"><code>/{skill_name} &lt;action&gt; {name}'
            f" — e.g. /{skill_name} generate {name}</code></pre>"
            f'<p class="install-hint">&lt;action&gt; is one of: {links}</p>'
            f"</section>"
        )

    def _guidance(self, label: str) -> str:
        section = self.fidelity.fidelity.section
        guidance = MarkdownHtml(f"## {label}\n\n{section}" if section else section).guidance_html
        examples = self.fidelity.examples_html
        return self._after_overview(guidance, examples) if examples else guidance

    def _after_overview(self, guidance: str, insertion: str) -> str:
        """``insertion`` at the end of the Overview section, before the next heading."""
        overview = re.search(r"<h([1-4])>Overview</h\1>", guidance)
        if not overview:
            return guidance + insertion
        following = re.search(r"<h[1-4]>", guidance[overview.end():])
        at = overview.end() + following.start() if following else len(guidance)
        return guidance[:at] + insertion + guidance[at:]

    @property
    def _template(self) -> str:
        default_format = self.fidelity.fidelity.default_format
        template = FidelityTemplate(self.fidelity)
        path = template.path
        if path is None or not path.is_file():
            return (
                '<section class="install-block fidelity-template" aria-label="Default template">'
                "<h2>Default template</h2>"
                f"<p>No template file for default format <code>{html.escape(default_format or 'unknown')}</code>.</p>"
                "</section>"
            )
        return (
            f'<section class="install-block fidelity-template" aria-label="Default template">'
            f"<h2>Default template</h2>"
            f'<p class="install-hint">Default format: <code>{html.escape(default_format or "")}</code>'
            f' — <a href="{html.escape(self.citation.blob_url(path))}">{html.escape(template.relative_path)}</a></p>'
            f"{template.fence_html}"
            f"</section>"
        )


class ActionPage(DetailPage):
    """A lifecycle action's page: the request that runs it, its guide, and its module overview."""

    nav_current = "actions"

    def __init__(self, action: LifecycleAction) -> None:
        self.action = action

    @property
    def href(self) -> str:
        return self.action.href

    @property
    def title(self) -> str:
        return f"{self.action.name} — lifecycle action"

    @property
    def body(self) -> str:
        return (
            self._header("Lifecycle action", self.action.name)
            + f'<section class="install-block action-invoke" aria-labelledby="action-invoke-heading">'
            f'<h2 id="action-invoke-heading">Request</h2>'
            f'<p class="install-hint">used as action: <code>{html.escape(self.action.name)}</code> in the request</p>'
            "</section>\n"
            + self._section("Markdown instructions", self._guide)
            + self._section("Module overview", self._overview)
        )

    @property
    def _guide(self) -> str:
        """``{action}.md`` when two actions share a toolset folder, else the folder's own guide."""
        folder = self.action.source_dir
        guides = (folder / f"{self.action.name}.md", folder / f"{folder.name}.md")
        guide = next((path for path in guides if path.is_file()), None)
        return self._markdown_file(guide, "") if guide else "<p>No dedicated guide - see module overview below.</p>"

    @property
    def _overview(self) -> str:
        overview = self.action.source_dir / ".context" / "module-context.md"
        return self._markdown_file(overview, "<p>No module-context.md yet.</p>")


class UtilityPage(DetailPage):
    """A utility's page: its module overview and its guide."""

    nav_current = "tools"

    def __init__(self, utility: Utility) -> None:
        self.utility = utility

    @property
    def href(self) -> str:
        return self.utility.href

    @property
    def title(self) -> str:
        return f"{self.utility.name} — utility"

    @property
    def body(self) -> str:
        toolset_class = self.utility.toolset_class
        folder = class_folder(toolset_class)
        purpose = f"<p>{html.escape((toolset_class.__doc__ or '').strip())}</p>"
        overview = self._markdown_file(self._module_card(folder), purpose)
        guide = self._markdown_file(folder / f"{folder.name}.md", "<p>No dedicated guide.</p>")
        return self._header("Utility", self.utility.name) + self._section("Module overview", overview) + self._section("Guide", guide)

    def _module_card(self, folder: Path) -> Path:
        """The card of the module the toolset's folder belongs to: its own, or the nearest one above it, since several
        small toolsets, such as those under ``tools``, share one module card."""
        for candidate in (folder, *folder.parents):
            card = candidate / ".context" / "module-context.md"
            if card.is_file() or candidate == _REPO_ROOT:
                return card
        return folder / ".context" / "module-context.md"


# -- The project a catalog is generated for -------------------------------------


class CatalogNotGenerated(Exception):
    """A project's own catalog generator failed; the message names the project and what the generator reported."""


# A whole catalog renders in seconds; a run this long has hung, and it would hold an MCP thread until it is stopped.
CATALOG_GENERATION_TIMEOUT_SECONDS = 600
_CATALOG_GENERATOR_MODULE = "harness.catalog_generator.generate_cdd_catalog"
_CATALOG_GENERATOR_FILE = Path("harness", "catalog_generator", "generate_cdd_catalog.py")


class CatalogProject:
    """The project a catalog is generated for: the folder its pages go into and the checkout whose guidance they show.

    A CDD checkout, such as a branch worktree, shows its own guidance in its own ``cdd_guidance/catalog``, so a branch's
    catalog shows that branch's practices and actions. Any other project shows the guidance the CDD tools serving it
    give its agents, written into the project's ``catalog`` folder beside the project's own approach slide."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    @property
    def is_cdd_checkout(self) -> bool:
        return (self.root / _CATALOG_GENERATOR_FILE).is_file()

    @property
    def is_serving_checkout(self) -> bool:
        """Whether this project is the checkout this code was imported from, whose guidance is already loaded."""
        return os.path.normcase(self.root) == os.path.normcase(_REPO_ROOT)

    @property
    def shows_own_guidance(self) -> bool:
        """Whether the catalog must be generated by the project's own code, because it is a CDD checkout whose
        guidance can differ from the guidance loaded here."""
        return self.is_cdd_checkout and not self.is_serving_checkout

    @property
    def catalog_folder(self) -> Path:
        if self.is_cdd_checkout:
            return self.root / "cdd_guidance" / "catalog"
        return self.root / "catalog"

    def generate_with_own_guidance(self, out_root: Path, brand: str) -> str:
        """Run the project's own catalog generator, so every page is read from the project's guidance and code."""
        try:
            finished = subprocess.run(
                self._generator_command(out_root, brand),
                cwd=self.root,
                env=self._generator_environment(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=CATALOG_GENERATION_TIMEOUT_SECONDS,
                check=True,
            )
        except subprocess.CalledProcessError as failure:
            raise CatalogNotGenerated(
                f"The catalog generator in {self.root} failed: {failure.stderr.strip() or failure.stdout.strip()}"
            ) from failure
        except subprocess.TimeoutExpired as failure:
            raise CatalogNotGenerated(
                f"The catalog generator in {self.root} did not finish in {CATALOG_GENERATION_TIMEOUT_SECONDS} seconds"
            ) from failure
        return finished.stdout.strip()

    def _generator_command(self, out_root: Path, brand: str) -> list[str]:
        command = [sys.executable, "-m", _CATALOG_GENERATOR_MODULE, "--out", str(out_root)]
        return command + ["--brand", brand] if brand else command

    def _generator_environment(self) -> dict[str, str]:
        """Import path for the generator: only the project's folders, so no module is read from the checkout serving
        these tools. The generator regenerates the checkout it is imported from, so it needs no project named."""
        environment = dict(os.environ)
        environment["PYTHONPATH"] = RepositoryToolsets(self.root).pythonpath()
        environment["PYTHONIOENCODING"] = "utf-8"
        return environment


@dataclass(frozen=True)
class _SourceDocument:
    """A repository document the catalog shows as a page of its own, without its title line."""

    source: Path
    file_name: str
    title: str
    heading: str
    article_class: str
    nav_current: str = ""
    include_tables: bool = False


_SOURCE_DOCUMENTS = (
    _SourceDocument(_REPO_ROOT / "README.md", "readme.html", f"README — {_SITE_TITLE}", "README", "catalog-source-doc"),
    _SourceDocument(
        _REPO_ROOT / "catalog" / "workflow.md", "workflow.html", f"CDD Workflow — {_SITE_TITLE}", "CDD Workflow",
        "catalog-workflow-page", nav_current="hub", include_tables=True,
    ),
)


@agent_toolset
class Catalog:
    """The top-level entry point - the only class ``generate_cdd_catalog.py`` calls. Holds the project it is generated
    for, the repository citation, the brand it wears, the approach copy, and the practices, lifecycle actions, and
    utilities it renders; it writes every page under ``out_root``, a project's own approach page among them, and always
    copies the Foundry commons there."""

    def __init__(
        self,
        repo_url: str = "",
        ref: str = "",
        out_root: str = "",
        brands_root: str | Path | None = None,
        approach_md_path: str | Path | None = None,
        project: str | Path | None = None,
    ) -> None:
        self.project = CatalogProject(project if project is not None else Path.cwd())
        checkout = GitCitation(repo_url, ref) if repo_url and ref else GitCitation.from_checkout()
        self.citation = GitCitation(repo_url or checkout.repo_url, ref or checkout.ref)
        self._named_out_root = Path(out_root) if out_root else None
        self.approach_md_path = Path(approach_md_path) if approach_md_path is not None else APPROACH_MARKDOWN
        self.brand = Brand(collection=brands_root)
        self._practices: list[CatalogPractice] | None = None
        self._utilities: list[Utility] | None = None
        self._lifecycle_actions: list[LifecycleAction] | None = None
        self._approach_copy: ApproachCopy | None = None

    @classmethod
    @tool_subject
    def load(cls, *, project: Path) -> Catalog:
        """The catalog of project, the folder the tool call names; one server answers every chat, so each call makes
        its own."""
        return cls(project=project)

    @property
    def repo_url(self) -> str:
        return self.citation.repo_url

    @property
    def out_root(self) -> Path:
        """The folder every page is written under: the one the caller named, else the project's catalog folder."""
        return self._named_out_root or self.project.catalog_folder

    @property
    def practices(self) -> list[CatalogPractice]:
        """The practices the catalog renders, loaded on first use."""
        if self._practices is None:
            self._practices = CatalogPractice.load_all()
        return self._practices

    @property
    def utilities(self) -> list[Utility]:
        if self._utilities is None:
            self._utilities = Utility.load_all()
        return self._utilities

    @property
    def lifecycle_actions(self) -> list[LifecycleAction]:
        if self._lifecycle_actions is None:
            self._lifecycle_actions = LifecycleAction.load_all()
        return self._lifecycle_actions

    @property
    def approach_copy(self) -> ApproachCopy:
        """The approach page's copy, read from ``approach_md_path`` on first use."""
        if self._approach_copy is None:
            self._approach_copy = ApproachCopy.load(self.approach_md_path)
        return self._approach_copy

    @property
    def board(self) -> HubBoard:
        return HubBoard(self.practices, self.lifecycle_actions, self.utilities, self.approach_copy.board_stages)

    @property
    def brands(self) -> dict[str, Path]:
        return self.brand.folders()

    @mcp
    @skill
    @agent_tool
    def generate_catalog(self, brand: str | Path = "") -> str:
        """Render the whole catalog for the project being worked on, with Foundry chrome.
        Pages go into ``out_root``: the project's ``cdd_guidance/catalog`` when
        the project is a CDD checkout, else its ``catalog`` folder. A CDD
        checkout's catalog shows that checkout's own guidance; any other
        project's shows the guidance these tools give it. No output is ever
        written outside ``out_root``.
        ``brand`` is a collection name under the brands folder, or a path to a
        brand folder; empty uses bundled abd-works."""
        if self.project.shows_own_guidance:
            return self.project.generate_with_own_guidance(self.out_root, str(brand))
        self.brand.wear(str(brand))
        self._render_catalog()
        return f"Catalog regenerated into {self.out_root} using {self.citation.repo_url}@{self.citation.ref}"

    @mcp
    @skill
    @agent_tool
    def apply_brand(self, name: str) -> str:
        """Overlay a named brand from the catalog brands collection onto the
        generated catalog commons without regenerating pages. ``name`` is a
        folder name under the brands collection, or a path to a brand folder.
        Bundled ``abd-works`` is always available."""
        if not name:
            return f"Known brands: {', '.join(sorted(self.brands))}"
        return f"Applied brand {name} under {self.brand.apply_named(self.out_root, name)}"

    @mcp
    @skill
    @agent_tool
    def generate_project_approach(self, examples_json: str = "", project_title: str = "") -> str:
        """Render ``cdd-approach.html`` for the project the call names, into its catalog folder, using its example
        artifacts. ``examples_json`` is optional JSON mapping practice → stage → path relative to the project; when
        blank, use ``.context/project-approach-examples.json`` and auto-discovery. ``project_title`` names the page;
        blank uses the saved title, else the project folder's name."""
        files = ProjectFiles(self.project.root, self.practices)
        approach = ProjectApproach.for_project(files, project_title).with_examples_json(examples_json)
        approach.save_examples()
        written = self._write_project_approach(approach)
        return f"Wrote project approach slide to {written}"

    @mcp
    @skill
    @agent_instructions
    def configure_project_approach(self, example_paths: list[str] | None = None) -> str:
        """Build a project-specific ``cdd-approach.html`` slide from example artifacts.

        example_paths={example_paths or 'discover from project tree'}

        Each example lands under one practice and one stage on the approach page.
        Use the same layout as ``catalog/cdd-approach.html``.

        **Where each example goes**

        | Practice | Discovery | Specification | Implementation |
        | --- | --- | --- | --- |
        | stories | story map | scenarios | acceptance tests |
        | ddd | bounded context map | domain model | tactics code |
        | ux | information architecture | mockup | front-end code |
        | clean_engineering | modules | model | code |
        | bdd | behavior specs | realization | development tests |

        **Step 1 — Collect examples**

        Read every path in ``example_paths``. When the list is empty,
        ``generate_project_approach`` walks the project tree itself.

        **Step 2 — Classify each file**

        A file belongs to the fidelity whose declared outputs name it: the
        same file names and patterns the session uses to find a fidelity's
        files, such as ``.context/story-map.drawio`` for the story map or
        ``{{bounded_context}}/{{aggregate}}/{{aggregate}}.ts`` for the domain
        model. ``generate_project_approach`` classifies discovered files this
        way, so classify the listed files the same way. A file no fidelity
        declares has no place until the user names one; ask rather than
        guess from its name.

        **Step 3 — Confirm the mapping**

        Show a short table: practice, stage, relative path. Edit it until
        every practice and stage the user cares about has a file.

        **Step 4 — Generate**

        Build ``examples_json`` from the confirmed mapping:

        ```json
        {{"examples": {{"stories": {{"discovery": "stories/story-map.drawio", ...}}}}}}
        ```

        Call ``generate_project_approach`` with ``examples_json``, and with
        ``project_title`` when the user names the page."""
        tools(self.generate_project_approach)
        return "Project approach slide generated."

    def write_page(self, relative_path: str, html_text: str) -> Path:
        """Write one page at ``relative_path`` under ``out_root``."""
        target = self.out_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html_text, encoding="utf-8")
        return target

    def _render_catalog(self) -> None:
        """Write every catalog page under ``self.out_root``."""
        self.out_root.mkdir(parents=True, exist_ok=True)
        self.brand.copy_commons(self.out_root)
        board = self.board
        practice_pages = [PracticePage(practice) for practice in self.practices]
        action_pages = [ActionPage(action) for action in self.lifecycle_actions]
        utility_pages = [UtilityPage(utility) for utility in self.utilities]
        for page in [*practice_pages, *self._fidelity_pages, *action_pages, *utility_pages]:
            self._write_detail_page(page, board)
        self._write_hub(board)
        self._write_approach_pages()
        for document in _SOURCE_DOCUMENTS:
            self._write_source_document(document)
        self._write_grid_pages(practice_pages, action_pages, utility_pages)

    @property
    def _fidelity_pages(self) -> list[FidelityPage]:
        return [
            FidelityPage(practice, shown, self.citation, self.lifecycle_actions)
            for practice in self.practices
            for shown in practice.shown_fidelities
        ]

    @property
    def _repo_link(self) -> str:
        return f'Get the repo <a href="{self.repo_url}" target="_blank" rel="noopener noreferrer">here</a>.'

    def _write_detail_page(self, page: DetailPage, board: HubBoard) -> None:
        shell = PageShell(
            title=page.title,
            h1=_HEADLINE,
            tagline=_SITE_SENTENCE + self._repo_link,
            body_inner=page.body,
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current=page.nav_current,
            body_wrap_class="skill-detail-page",
            kanban_embed=board.html(
                path_prefix="../", practice=page.highlighted_practice, fidelity=page.highlighted_fidelity
            ),
        )
        self.write_page(page.href, shell.html)

    def _write_hub(self, board: HubBoard) -> None:
        shell = PageShell(
            title=_SITE_TITLE,
            h1=_HEADLINE,
            tagline=_SITE_SENTENCE + self._repo_link,
            after_tagline='<a class="page-hero__approach-btn" href="cdd-approach.html">The approach</a>',
            body_inner=self._install_steps,
            nav_current="hub",
            kanban_embed=board.html(),
        )
        self.write_page("index.html", shell.html)

    @property
    def _install_steps(self) -> str:
        repo_url = html.escape(self.repo_url)
        install_script = html.escape(self.citation.blob_url(_INSTALL_SCRIPT))
        return (
            '<section class="install-block catalog-install">'
            "<details>"
            '<summary id="catalog-install-heading">Install</summary>'
            "<ol>"
            f'<li>Get the repository: <a href="{repo_url}" target="_blank" rel="noopener noreferrer">{repo_url}</a>.</li>'
            "<li>Add it to your project (clone into the workspace or add it as a sibling "
            "checkout the agent can see).</li>"
            f'<li>From the repository, run <a href="{install_script}" target="_blank" rel="noopener noreferrer">'
            f"<code>{_INSTALL_COMMAND}</code></a> (or <code>--ide Cursor</code>, <code>--ide \"VS Code\"</code>, "
            "<code>--ide Kilo</code>). That installs each practice and action into the IDE as a skill.</li>"
            "</ol>"
            "</details>"
            "</section>\n"
        )

    def _write_approach_pages(self) -> None:
        for practice in self.practices:
            practice.copy_examples_into(self.out_root)
        page = ApproachPage(self.approach_copy, self.practices, self.out_root)
        self._write_approach(page, title=_SITE_TITLE, h1=_HEADLINE, after_subhead=self._repo_link)
        for file_name, page_html in page.principle_pages.items():
            self.write_page(file_name, page_html)

    def _write_project_approach(self, approach: ProjectApproach) -> Path:
        """Write a project's own approach page, a ``ProjectApproach``, with the project's examples staged beside it."""
        self.out_root.mkdir(parents=True, exist_ok=True)
        self.brand.copy_commons(self.out_root)
        page = ApproachPage(self.approach_copy, self.practices, self.out_root, approach.staged_into(self.out_root))
        return self._write_approach(page, title=approach.page_title, h1=approach.headline, after_subhead=approach.repo_link)

    def _write_approach(self, page: ApproachPage, *, title: str, h1: str, after_subhead: str) -> Path:
        """Write the approach page's stage example pages, then the page itself as ``cdd-approach.html``."""
        page.write_stage_example_pages()
        shell = PageShell(
            title=title,
            h1=h1,
            tagline="",
            subhead=self.approach_copy.subhead,
            after_subhead=after_subhead,
            body_inner=page.body,
            body_wrap_class="approach-wrap",
        )
        return self.write_page("cdd-approach.html", shell.html)

    def _write_source_document(self, document: _SourceDocument) -> None:
        if not document.source.is_file():
            return
        text = _TITLE_LINE.sub("", document.source.read_text(encoding="utf-8").lstrip(), count=1)
        article = MarkdownHtml(text, include_tables=document.include_tables).html
        shell = PageShell(
            title=document.title,
            h1=document.heading,
            tagline=_SITE_SENTENCE + _BACK_TO_CATALOG,
            body_inner=f'<article class="{document.article_class}">{article}</article>',
            nav_current=document.nav_current,
        )
        self.write_page(document.file_name, shell.html)

    def _write_grid_pages(
        self, practice_pages: list[PracticePage], action_pages: list[ActionPage], utility_pages: list[UtilityPage]
    ) -> None:
        practices = [self._card(practice.display_name, practice.href, practice.display_name) for practice in self.practices]
        actions = [self._card(action.name, action.href, "Lifecycle action") for action in self.lifecycle_actions]
        utilities = [self._card(utility.name, utility.href, "Utility") for utility in self.utilities]
        self._write_grid("context-tools", "Context tools", "Every context tool in the catalog", practices, practice_pages)
        self._write_grid("actions", "Actions", "Lifecycle actions", actions, action_pages)
        self._write_grid("tools", "Utilities", "Foundational utilities", utilities, utility_pages)
        self._write_grid("fidelities", "Fidelities", "Every fidelity ticket", self._fidelity_cards, None)

    @property
    def _fidelity_cards(self) -> list[str]:
        return [
            self._card(
                shown.name,
                practice.fidelity_href(shown.fidelity),
                f"{practice.display_name} · {shown.column.key}",
                label="Fidelity",
            )
            for practice in self.practices
            for shown in practice.board_fidelities
        ]

    def _write_grid(self, name: str, heading: str, tagline: str, cards: list[str], pages: list[DetailPage] | None) -> None:
        """A grid page of cards; the pages' bodies are kept hidden in it, so a search of the page finds them."""
        hidden = f'<div hidden>{"".join(page.body for page in pages)}</div>' if pages is not None else ""
        shell = PageShell(
            title=f"{heading} — CDD Catalog",
            h1=heading,
            tagline=tagline,
            body_inner=f'<div class="cap-grid">{"".join(cards)}</div>{hidden}',
            nav_current=name,
        )
        self.write_page(f"{name}.html", shell.html)

    def _card(self, title: str, href: str, summary: str, label: str = "Catalog") -> str:
        return (
            f'<a class="cap-card" href="{html.escape(href)}">'
            f'<p class="cap-card__title">{html.escape(title)}</p>'
            f'<p class="cap-card__label">{html.escape(label)}</p>'
            f'<p class="cap-card__summary">{html.escape(summary)}</p>'
            f'<p class="cap-card__more">Open →</p></a>'
        )
