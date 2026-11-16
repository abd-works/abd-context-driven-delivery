# cdd_guidance/agents
*Agents* are the role prompts CDD installs as sub-agents: Discoverer (`discovery.md`), Specification (`specification.md`), Implementation (`implementation.md`) and Context (`context.md`). Each says what the role produces, which practices and fidelities it works at, and which actions it uses. They hold no code: the installer publishes each file as an agent definition in every IDE.

- **Purpose:** Give each delivery role one prompt, so a role's work is the same in every IDE and every chat.
- **Seam (terms):** Discoverer, Specification, Implementation, Context
- **Dependencies (one-way):** none in code; the prompts name the practices in `cdd_guidance/practices` and the actions in `cdd_guidance/actions` they use.

## Constraint

A prompt names practices, fidelities and actions by the names the catalogues publish; it never restates a practice's rules, which stay in the practice. Change the prompt here and reinstall; never edit an installed copy.
