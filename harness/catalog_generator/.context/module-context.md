# harness/catalog_generator
*Catalog* renders the CDD catalog: a set of self-contained HTML pages that show every practice, its fidelities and rules, the lifecycle actions, and the utilities, read straight from the live guidance classes and their markdown, so the pages show exactly what an agent is given. A person runs it as `catalog.generate_catalog` (also installed as a skill) or `python -m harness.catalog_generator.generate_cdd_catalog`; pages are written only under the output folder (`cdd_guidance/catalog/` by default) and cite source through links to the Git remote, so the folder can be published anywhere.
`catalog.apply_brand` lays a named brand over the generated pages without rendering them again. `catalog.configure_project_approach` asks the person which of their artifacts shows each practice at each stage, and `catalog.generate_project_approach` renders that project's own `cdd-approach.html` from the answer.
`@noCatalog` (harness/installation) keeps a class, fidelity, or operation out of the pages without changing what is installed.

- **Purpose:** Show people what CDD offers, as pages generated from the same guidance the agent follows, for CDD itself or for one project's approach.
- **Seam (terms):** Catalog; the MCP operations `catalog.generate_catalog`, `catalog.apply_brand`, `catalog.generate_project_approach`, `catalog.configure_project_approach`; `python -m harness.catalog_generator.generate_cdd_catalog`
- **Dependencies (one-way):** harness/agent_tools, harness/guidance (*PracticeCatalogue*, *PracticeGuidance*, *FidelityGuidance*), harness/markdown, harness/installation, harness/mcp, and at call time every practice and action class it renders. Nothing imports this module back.

## Constraint

Render from the live guidance object a page is about, never from a copy of its fields, so a page cannot disagree with the guidance. Keep each fidelity's guidance as a `### {fidelity}` heading inside `## Fidelities` in the practice markdown, because that heading is how the catalog finds it. Write only under the output folder, and cite source only through Git links, so the generated pages work wherever they are copied.
