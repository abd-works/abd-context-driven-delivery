# Rule: Story Map from Existing Code

**Scanner:** _(none in JSON — methodological guidance for code-to-map workflows)_


When deriving a story map from **code**, start from **entry points**, derive operations and **goals**, then **epics/sub-epics/stories** — not from class names alone.

## DO

1. **Entry points** — CLI commands, UI handlers, MCP tools, APIs, acceptance tests.
2. **Operations** — list and group by functional purpose.
3. **Epics from goals** — group operations by higher-order goals (e.g. CLI entry points `render-outline`, `render-increments` → goal **Render StoryGraph** → epic **`Render StoryGraph`**).
4. **Sub-epics from behaviors** — e.g. under **Render StoryGraph** → **`Render Outline`**, **`Render Increments`** (verb–noun, same bar as **Verb–Noun Format**).
5. **Story journey** — trace flow start → middle → end; include when/why/outcome/actor and error paths where relevant.

## DON'T

- Start from **internal classes** or mirror **class structure** as epics.
- Turn **every method** into a story.
- Omit **context** (when/why/outcome) or elevate **implementation detail** as if it were user-visible behavior.
