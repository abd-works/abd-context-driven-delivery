# harness/catalog_generator

The *Catalog* renders CDD's practices, actions, and approach as pages; a *CatalogPractice* is one practice as every page and the session board show it, and a *CatalogFidelity* is one of its fidelities as the catalog shows it, with its board column.

- **Purpose:** Show people what CDD offers, as pages generated from the same guidance the agent follows, for CDD itself or for one project's approach.
- **Seam (terms):** Catalog, CatalogPractice, CatalogFidelity; the MCP operations `catalog.generate_catalog`, `catalog.apply_brand`, `catalog.generate_project_approach`, `catalog.configure_project_approach`; `python -m harness.catalog_generator.generate_cdd_catalog`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/installation, harness/git, harness/mcp

## Catalog

The top-level entry point - the only class `generate_cdd_catalog.py` calls. Holds the project it is generated for, and writes every page with the parts it holds: its project, its brand, its approach copy, and its practices.

+ Catalog(project: CatalogProject | None = None, citation: GitCitation | None = None, brand: Brand | None = None)
------
+ << composition >> project: CatalogProject
+ << association >> citation: GitCitation
+ << association >> brand: Brand
+ repo_url: str
+ out_root: Path
+ << composition >> practices: list[CatalogPractice]
+ utilities: list[Utility]
+ lifecycle_actions: list[LifecycleAction]
+ approach_copy: ApproachCopy
+ board: HubBoard
+ brands: dict[str, Path]
----
+ load(project: Path): Catalog
+ generate_catalog(brand: str | Path = ''): str
+ apply_brand(name: str): str
+ generate_project_approach(examples_json: str = '', project_title: str = ''): str
+ configure_project_approach(example_paths: list[str] | None = None): str
+ write_page(relative_path: str, html_text: str): Path
---<<loads>>--> CatalogPractice
---<<lists actions from>>--> ActionCatalogue
---<<finds the utilities with>>--> RepositoryToolsets
---<<creates>>--> GitCitation
---<<creates>>--> HubBoard

## CatalogPractice

One practice as the catalog shows it: the live `PracticeGuidance`, the catalog card it gives itself, its place in the catalogue, and the fidelities it shows, each placed in the board's stage columns. Its slash command is the folder the Claude Code skill install writes its skill into.

+ CatalogPractice(practice: PracticeGuidance, skills: FileInstallation | None = None, position: int = 0, catalogue: tuple[PracticeGuidance, ...] = ())
------
+ << association >> practice: PracticeGuidance
+ position: int
+ key: str
+ display_name: str
+ label: str
+ product_engineering_label: str
+ gives_stage_examples: bool
+ family: str
+ perspective: str
+ order: int
+ spec_blurb: str
+ href: str
+ skill_name: str
+ fidelities: list[FidelityGuidance]
+ << composition >> shown_fidelities: list[CatalogFidelity]
+ board_fidelities: list[CatalogFidelity]
+ on_board: bool
+ examples_folder: Path
+ shared_markdown: str
+ << association >> skills: CatalogSkills
----
+ of_practices(practices: Iterable[PracticeGuidance]): list[CatalogPractice]
+ load_all(): list[CatalogPractice]
	-> PracticeCatalogue.create_all
+ fidelity_in(column: StageColumn): CatalogFidelity | None
+ fidelity_at(stage: str): CatalogFidelity | None
+ fidelity_href(fidelity: FidelityGuidance): str
+ language_of(path: Path): str | None
+ copy_examples_into(out_root: Path): None
---<<creates>>--> CatalogFidelity
---<<reads fidelities of>>--> PracticeGuidance
---<<lists practices from>>--> PracticeCatalogue
---<<names its skills through>>--> CatalogSkills
---<<creates>>--> Name
---<<reads a file's format with>>--> Format
---<<leaves out what is annotated>>--> NoCatalog

## CatalogSkills

The skill install whose folder names are the slash commands the catalog shows, made once for the practices of one catalog.

+ CatalogSkills(install: SkillInstallation)
------
----
+ create(): CatalogSkills
+ skill_of(guidance: PracticeGuidance | FidelityGuidance): str
---<<creates, with its own record>>--> SkillInstallation
---<<creates>>--> IdeLayout
---<<asks whether Skill publishes>>--> AgentTool

## CatalogFidelity

A fidelity as the catalog shows it: its board column, its board label, the opening of its overview, and its example files.

+ CatalogFidelity(fidelity, practice: CatalogPractice)
------
+ << association >> fidelity: FidelityGuidance
+ << association >> practice: CatalogPractice
+ name: str
+ stage: str
+ column: StageColumn | None
+ label: str
+ opening: str
+ example_files: list[Path]
+ panel_example_files: list[Path]
+ examples_html: str
----
---<<reads stage of>>--> FidelityGuidance
---<<finds its column in>>--> StageColumn
---<<creates>>--> ExampleFile
