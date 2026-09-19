# Stories (generator)

**Purpose:** Multi-fidelity story-map generator — discovery / exploration / engineering over peer format channels (markdown, JSON, DrawIO, Miro, Python, TypeScript, Java, JavaScript).

**Seam:** `Stories` toolset (`practices.stories.stories:Stories`)

**Public API:** fidelity/format construction; `guidance` (domain generate prose + CleanEngineering companion as a separate tools run); `transform`; `render(format, content)` (calls `transform` from the current format); `diagnostic()` Diagnose companion; `ce()` CleanEngineering companion; `contexts` instruction. Lifecycle generate / validate / satisfy / iterate live on kits under `actions/` — pass this Guidance in (`Generate().generate(tools=[stories])`). Catalog fidelity YAML must invoke that kit, not `action: generate` on this class.

**Dependencies:** `BaseContextTool`; format channel classes under `document` / `diagram` / `code`; `tools.diagnose.Diagnose` (via `diagnostic()`)

**Mechanism:** `guidance` calls `super().guidance()` then `ce()` (CleanEngineering companion, tool mode) so wrap classes stay a separate tools run, not inlined. Format moves go through peer `parse` / `render` on channel StoryMaps.
