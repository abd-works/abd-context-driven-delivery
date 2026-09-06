# Input traps — abd-story-mapping

Assumptions, ambiguities, and missing context that commonly produce bad story maps. Check each trap against available input before generating — flag gaps honestly; do not invent structure to fill them.

- **Hidden actors** — who actually uses this — is "the user" hiding three different people with different goals, or is there a system actor nobody mentioned?
- **Actor reality** — for every actor, confirm they exist in this iteration. Ask: is this a real human role, or an automated system? If automated, does the automation exist yet? Do not assume an actor is real because it sounds plausible — verify it. If everything is manual in this iteration, automated actors do not belong on the map.
- **Behaviors vs. tasks** — are these outcomes people care about, or build tasks disguised as stories? "Implement payment gateway" is a task; "Process customer payment" is a behavior. Which are we looking at?
- **Vague story names** — when a story uses a vague verb or noun ("provision", "manage", "handle", "set up", "improve"), ask what the actual concrete steps are. A story name must describe one observable behavior, not a category of work.
- **Tool specificity** — when a story describes a generic behavior ("extract content", "send notification"), ask which specific tool or mechanism is actually used. Generic behavior names produce generic output; name the tool.
- **Missing triggers** — are there background processes, scheduled jobs, or external systems that kick off behaviors nobody has surfaced yet? They always show up later as gaps.
- **Sequencing** — read the sub-epics in order. Can each story actually be done before the next one starts? Are there prerequisites that haven't appeared yet? Repo-before-extraction, setup-before-use. Common sense must pass.
- **Delivery epics and CDD flow** — if there is an epic about delivering value, check whether the stories inside it mirror the CDD fidelity flow (shaping → discovery → exploration → specification → engineering). A delivery epic with generic "generate → review → submit" stories has not been connected to the actual delivery process.
- **Scope bleeding** — where does this product's responsibility end and another system's begin? If that boundary isn't drawn, stories will leak across it.
- **Duplication across sub-epics** — before finalising, scan all sub-epics for overlap. Do any two sub-epics describe the same behaviour under different names? If yes, collapse or kill the duplicate — do not carry redundant sub-epics forward.
- **Depth agreement** — does everyone expect the same level of detail from this map — an outline to frame conversations, or a full breakdown to plan work? Mismatched expectations waste everyone's time.
