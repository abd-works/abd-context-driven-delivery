# Grill Answers

### Where a practice’s default format lives

On each `FidelityGuidance`, parsed from that fidelity’s markdown block (`**Default format:**`, already written next to `**Stage:**` in `stories.md`, `ux.md`, `ddd.md`, `bdd.md`, `clean_engineering.md`, `car.md`, `cdd.md`). Drop `_FIDELITY_FORMAT_DEFAULTS` / `_fidelity_format_defaults` on the practice classes. `PracticeGuidance` does not own a stage→format table. An explicit constructor `format` still overrides the fidelity default. Catalog scrape that today reads the Python dict must read the same markdown field.

### How a practice relates to Clean Engineering

Each `FidelityGuidance` (owned by its `PracticeGuidance`) holds an optional Clean Engineering **fidelity** companion — another `FidelityGuidance`, not a `ce()` on the practice. Absent or empty markdown → null → skip. Present → use that companion (guidance and later operations). Declare it on the same fidelity block as Stage and Default format (`**Clean Engineering:**` plus the CE fidelity name: `modules` / `model` / `code`). Clean Engineering’s own fidelities stay null.

### Who owns render

Callers use the **Render action** (`actions/render`: for each Guidance, `host.render(format, content)`). Practices must present one seam so that action can pick transformers — not a second orchestrator on BDD/DDD/Stories.

Each practice that has its own artifact keeps **`model/`** for the canonical types, and **one folder per format underneath `model/`** named after the format (`model/drawio/`, `model/miro/`, `model/markdown/`, `model/python/`, `model/html/`, …). Not siblings of `model/`. Drop the `document/` / `diagram/` / `code/` / `web/` grouping. Reorganization of existing parse/render types — not new conversion behavior.

BDD and DDD keep no format folders; their fidelities’ Clean Engineering companions supply render.

`PracticeGuidance.render` is the shared loop: source format `parse` → model → target format `render`. Empty format folders and a companion → that companion’s practice `render`. Format-specific extras (Stories Miro upload, CE drawio positioning) stay in the format folder.

