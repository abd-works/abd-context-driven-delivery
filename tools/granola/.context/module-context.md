# tools/granola
*Granola* files unorganized Granola meeting notes into folders and brings chosen notes into a project folder's `.context/granola/` as independent context files, one file per note. The MCP instructions `granola.organize(scope)` propose a folder for each note and file them after the user confirms; `granola.context(notes, folder)` captures notes into a folder. The MCP tools `granola.format_filing_plan`, `granola.list_note_context`, and `granola.write_note_context` do the local work those instructions call for.

- **Purpose:** Keep meeting notes organized in Granola and turn the ones that matter into context files beside the work they inform.
- **Seam (terms):** Granola, `granola.organize`, `granola.context`, `granola.format_filing_plan`, `granola.list_note_context`, `granola.write_note_context`
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation`, `harness/mcp`; the Granola MCP connector, which the instructions call for listing, reading, and filing notes

## Constraint

Create and move nothing in Granola until the user confirms the filing plan. Write each note verbatim to its own file; do not merge notes or summarize across them, so each context file can be read and cited alone.
