# Stories (generator)

**Purpose:** Multi-fidelity story-map generator — discovery / exploration / engineering over peer format channels (markdown, JSON, DrawIO, Miro, Python, TypeScript, Java, JavaScript).

**Seam:** `Stories` toolset (`context_tools.stories.stories:Stories`)

**Public API:** fidelity/format construction; lifecycle actions (`generate` / `validate` / `satisfy` / `iterate` / …); `transform`; `diagnostic()` Diagnose companion; `contexts` instruction

**Dependencies:** `BaseContextTool`; format channel classes under `document` / `diagram` / `code`; `utilities.diagnose.Diagnose` (via `diagnostic()`)

**Mechanism:** `satisfy` / `iterate` call `super()` then `diagnostic().diagnose()` so the shared six-phase loop stays on Diagnose (not inlined). Format moves go through peer `parse` / `render` on channel StoryMaps.
