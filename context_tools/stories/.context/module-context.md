# Stories (generator)

**Purpose:** Multi-fidelity story-map generator — discovery / exploration / engineering over peer format channels (markdown, JSON, DrawIO, Miro, Python, TypeScript, Java, JavaScript).

**Seam:** `Stories` toolset (`context_tools.stories.stories:Stories`)

**Public API:** fidelity/format construction; lifecycle actions (`generate` / `validate` / `satisfy` / `iterate` / …); `transform`; `render(format, content)` (calls `transform` from the current format); `diagnostic()` Diagnose companion; `contexts` instruction

**Dependencies:** `BaseContextTool`; format channel classes under `document` / `diagram` / `code`; `utilities.diagnose.Diagnose` (via `diagnostic()`)

**Mechanism:** `generate` / `iterate` / `satisfy` call `super()` then `ce()` (CleanEngineering companion) **only at acceptance_tests fidelity** so wrap classes stay in sync; `satisfy` / `iterate` (at that fidelity) also call `diagnostic().diagnose()` so the shared six-phase loop stays on Diagnose (not inlined). Format moves go through peer `parse` / `render` on channel StoryMaps.
