Build order: `practices` → `practices/clean_engineering` → `practices/bdd` → `practices/stories` → `practices/ux` → `practices/ddd` → `practices/agent_bdd`

# practices

*Practices* are fields of expertise — Clean Engineering, BDD, Stories, UX, DDD, agent BDD — each a *PracticeGuidance* plus co-located markdown. Lifecycle generate / validate / document live on *actions*, not on the practice class.

### Stage

- A named deepen step written on a fidelity as **Stage:** — discovery, specification, or implementation — so modules / model / code line up across practices.

- **Purpose:** Hold one *PracticeGuidance* per field so the same kits can generate and check work against that field’s words.
- **Seam (terms):** PracticeGuidance, Stage, attach_practice_workspace
- **Dependencies (one-way):** `harness/guidance`, `tools/workspace`
- **Constraint:** Do not put `/generate` on the practice. Pass the practice into the kit: `Generate().generate(guidance=[ce])`. `attach_practice_workspace` binds a *Workspace* onto the practice — it is not a second workspace type.

# practices/clean_engineering

Partition, type, and implement objects — modules, then model, then code — in the caller’s language.

- **Purpose:** Partition, type, and implement objects — modules, then model, then code — in the caller’s language.
- **Seam (terms):** CleanEngineering, `@clean-engineering-modules`, `@clean-engineering-model`, `@clean-engineering-code`
- **Dependencies (one-way):** `harness/guidance`
- **Constraint:** Each `# {path}` opens with language, then Purpose / Seam / Dependencies / Constraint bullets. Typed class dumps wait for model. A mistake in `module-context.md` is named here in the same turn.

# practices/bdd

Lock describe/it observations first, then fill tests red-green, then hand class code to Clean Engineering.

- **Purpose:** Lock describe/it observations first, then fill tests red-green, then hand class code to Clean Engineering.
- **Seam (terms):** Bdd
- **Dependencies (one-way):** `harness/guidance`, `practices/clean_engineering`

# practices/stories

Map stakeholder behaviour as Epic → Story so later fidelities share one hierarchy.

- **Purpose:** Map stakeholder behaviour as Epic → Story so later fidelities share one hierarchy.
- **Seam (terms):** Stories
- **Dependencies (one-way):** `harness/guidance`, `practices/clean_engineering`

# practices/ux

Decide screens, then greybox, then production UI, in domain words.

- **Purpose:** Decide screens, then greybox, then production UI, in domain words.
- **Seam (terms):** Ux
- **Dependencies (one-way):** `harness/guidance`, `practices/stories`, `practices/clean_engineering`

# practices/ddd

Draw where language changes — bounded context, then building blocks, then tactics — and reuse Clean Engineering for the OO ladder.

- **Purpose:** Draw where language changes — bounded context, then building blocks, then tactics — and reuse Clean Engineering for the OO ladder.
- **Seam (terms):** Ddd
- **Dependencies (one-way):** `harness/guidance`, `practices/clean_engineering`
- **Constraint:** Do not restate Clean Engineering class analysis in DDD artifacts. Use the fidelity’s Clean Engineering companion.

# practices/agent_bdd

Drive a real agent through `agent(...)` and assert on the parsed run — not a mocked transcript.

- **Purpose:** Drive a real agent through `agent(...)` and assert on the parsed run — not a mocked transcript.
- **Seam (terms):** AgentBdd, agent, instruct, instruct_use_tool, ai_judge
- **Dependencies (one-way):** `practices/bdd`
- **Constraint:** Specs call the harness only inside `with agent(...)`. Do not import CLI backends from specs.
