### Guidance

**Decompose through interactions.** Cover the business capability with Epics, then ground each Epic in Stories that demonstrate real behaviour. Find the **walking skeleton**, the smallest end-to-end path that works and delivers value, and validate it before adding later increments. Split increments by actor, data, workflow, channel, interface, non-functional requirement, or business rule when that creates a demonstrable step.

**Map the complete outcome.** Include the primary path, supporting actors, system interactions, reversals, and recovery behaviour needed to achieve the outcome. Administrators, support staff, partner onboarding, cancellations, refunds, escalations, and failures belong on the map when sources require them, because a forward path alone does not describe the working product.

**Treat a system hop as a boundary interaction.** A hop is an observable request and response across a named system boundary, not every internal function call. Keep internal fan-out within the boundary Story unless another system exposes its own observable interaction. Give an intermediary its own Story when it validates, decides, or translates; keep simple forwarding or display as an outcome on the caller's Story.

### Rules

- **verb-noun-format** — Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.
- **story-name-captures-system-mechanic** — At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.
- **four-to-nine-children** — Keep 4-9 direct children, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes.
- **branch-on-mechanical-uniqueness** — Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.
- **right-size-story-nodes** — Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.
- **behaviours-not-one-time-tasks** — Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.
