---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- story_map fidelity (Discovery stage) — every sub-epic decomposed to named stories.
     Do not wrap epic, sub-epic, story, or actor names in backticks.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story-kebab-slug}.py
     — epic/sub-epic folders kebab-case; one story file per story (no {story}/ folder).
     Exception: Python epic helper only — {epic_slug}_helper.py at epic root. -->

# Story Map — Context-Driven Delivery Framework

**Sources / context:** `.context/module-context.md` (the `harness` card); `harness/agent_tools/.context/module-context.md`; `harness/agent_tools/.context/agent-tools-model.md`; `harness/markdown/.context/module-context.md`; `harness/installation/.context/module-context.md`; `harness/hooks/.context/module-context.md`; `harness/hooks/.context/hooks-runtime-model.md`; `harness/guidance/guidance.py`; `harness/guidance/action_catalogue.py`; `harness/mcp/.context/module-context.md`; `cdd_guidance/actions/.context/module-context.md`; `cdd_guidance/practices/.context/module-context.md`; user spine: register agent toolsets → install markdown files (skill, slash command, rules) and MCP → invoke those → use context guidance (install skills and .mdc, invoke instructions, generate under rules) → use practice guidance (register guidance and fidelities, invoke practice and fidelity, shared and fidelity rules constrain output) → hook dispatch → extract markdown → lifecycle actions.

**Evidence:** Observed behaviour is cited from those files. Intended: practice guidance and fidelity guidance declare real `@Hook` events from `Hook.EVENTS`, and lifecycle actions use the same mark-and-install path as practice guidance.

---

(E) Deliver Context Driven Delivery
    (E) Register Agent Toolsets
        (S) Author --> Register Agent Toolsets
        (S) Author --> Register Agent Operations
        (S) Author --> Register Agent Tools
        (S) Author --> Register Agent Instructions
        (S) Agent Toolset --> Validate Instruction Body
        (S) Agent Instructions --> Build Instruction Expansion
        (S) Agent Instructions --> Collect Deferred Tools
    (E) Install Agent Toolsets
        (S) File Installation --> Publish Markdown Files
        (S) Mcp Installation --> Record Mcp Operation
        (S) Mcp Installation --> Publish Mcp Manifest
        (S) Installer --> Store Install State
    (E) Invoke Agent Toolsets
        (S) Agent --> Invoke Skill File
        (S) Agent --> Start Slash Command
        (S) Rules --> Constrain Valid Output
        (S) Agent --> Trigger Mcp Tool
        (S) Agent --> Trigger Mcp Prompt
    (E) Use Context Guidance
        (S) Author --> Register Guidance
        (S) File Installation --> Publish Guidance Files
        (S) Agent --> Collect Guidance Instructions
        (S) Generate --> Generate Guided Content
        (S) Rules --> Constrain Valid Output
    (E) Use Practice Guidance
        (S) Author --> Register Guidance
        (S) Author --> Register Fidelities
        (S) Agent --> Collect Guidance Instructions
        (S) Agent --> Collect Fidelity Instructions
        (S) Rules --> Constrain Shared Output
        (S) Rules --> Constrain Fidelity Output
    (E) Trigger Hook Dispatch
        (S) Author --> Register Hook Event
        (S) Hook Installation --> Publish Hooks Manifest
        (S) Dispatch --> Route Hook Payload
        (S) Dispatch --> Check Enablement Flag
        (S) Dispatch --> Merge Hook Output
    (E) Extract Markdown Content
        (S) Markdown --> Search Folder Extract
        (S) Markdown --> Search File Extract
        (S) Markdown --> Search Section Extract
        (S) Markdown --> Match Extract Type
        (S) Markdown --> Convert Extract Html
    (E) Run Lifecycle Actions
        (E) Register Action Kits
            (S) Author --> Register Action Tools
            (S) Author --> Register Action Prompt
            (S) Installer --> Publish Action Command
            (S) Agent --> Start Action Prompt
        (E) Shape Context Guidance
            (S) Partition --> Partition Context Guidance
            (S) Grill --> Grill Context Guidance
            (S) Sketch --> Sketch Context Guidance
            (S) Iterate --> Iterate Context Guidance
        (E) Produce Context Guidance
            (S) Generate --> Generate Context Guidance
            (S) Document --> Document Context Guidance
            (S) Render --> Render Context Guidance
            (S) Satisfy --> Satisfy Context Guidance
            (S) Diagnose --> Delegate Context Guidance Work
        (E) Check Context Guidance
            (S) Validate --> Validate Context Guidance
            (S) Validate --> Scan Context Guidance
            (S) Repair --> Repair Context Guidance
            (S) Verify Fix --> Verify Context Guidance Fix
            (S) Validate --> Create Context Rule

---

## Scope boundary

**In scope:** Authoring an Agent Toolset with `@agent_tool` and `@agent_instructions`. Installing that toolset as two writes — File Installation publishes skill, slash command, and rules as one story (same channel, same write) and Mcp Installation publishes `mcp.json` (`.mcp.json` for Claude Code) — then invoking the skill, slash command, and MCP tool and prompt. Installed rules are not invoked as a file check — they constrain valid output. Context Guidance is installed the same way (skill and `.mdc` rules), invoked so `instructions` come back, then used to generate content those rules constrain. Practice Guidance is that same Guidance plus registered fidelities — invoke at practice scope and at fidelity scope; shared rules and fidelity-specific rules each constrain the matching AI output. Hook dispatch; extracting co-located markdown via `@markdown`; every action in the action catalogue (`ActionCatalogue`, read from the folders under `cdd_guidance/actions`: `partition`, `grill`, `sketch`, `iterate`, `generate`, `document`, `render`, `satisfy`, `diagnose`, `validate`, `repair`, `verify_fix`). Scan Context Guidance is the graph-rule scan `validate` runs, not an action of its own.

**Out of scope:** Catalog HTML pages; one-time renames and repository moves; YAML manifest CLI / `tools.ps1` invoke; inventing extra practices or product domains beyond this framework spine; scenario and acceptance-test text (later fidelities).
