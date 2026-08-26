# Stories (generator)

**Purpose:** Multi-fidelity story-map generator — discovery / exploration / engineering over peer format channels (markdown, JSON, DrawIO, Miro, Python, TypeScript, Java, JavaScript).

**Seam:** `Stories` toolset (`context_tools.stories.stories:Stories`)

**Public API:** fidelity/format construction; `guidance` (domain generate prose + CleanEngineering companion as a separate tools run); `transform`; `render(format, content)` (calls `transform` from the current format); `diagnostic()` Diagnose companion; `ce()` CleanEngineering companion; `contexts` instruction. Lifecycle generate / validate / satisfy / iterate live on kits under `context_tools/actions/` — pass this host in (`Generate().generate(tools=[stories])`).

**Dependencies:** `BaseContextTool`; format channel classes under `document` / `diagram` / `code`; `utilities.diagnose.Diagnose` (via `diagnostic()`)

**Mechanism:** `guidance` calls `super().guidance()` then `ce()` (CleanEngineering companion, tool mode) so wrap classes stay a separate tools run, not inlined. Format moves go through peer `parse` / `render` on channel StoryMaps.
