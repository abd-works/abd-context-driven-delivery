### Rule: A mechanism opens with a "Why this shape" section that crystallises the design insight

Every mechanism-context.md must include a "Why this shape" section between the Overview and the File Structure. This section captures the insight from the grill-me / design conversation that produced the mechanism — the problem the naive approach creates, the specific inversion that solves it, and the two or three disciplines that keep the inversion from collapsing under maintenance pressure. It is the section a future reader consults when they want to propose an "obvious improvement" and need to discover why the current shape exists before they break it.

Passing means the section names a real design pivot (the fixed part of the algorithm, the single composition root, the abstraction seam) and at least two disciplines that would look arbitrary without it (why behavior lives in mixins but state lives in composition; why backends never reach sideways; why extension is additive and modification is forbidden). Failing means the section is missing, or it restates the file structure and rules in narrative form without saying *why* those choices were made, or it praises the mechanism without naming the alternatives it rejected.

**Why this rule exists:** the most important design decisions are the ones made in the grill-me conversation and immediately forgotten — the reasons a walk lives on the base and not the subclass, the reason state is composed rather than inherited, the reason there is exactly one registration point and not per-instance discovery. Six months later someone proposes duplicating the walk into each subclass, adding a second registration point, or refactoring composition into inheritance, and the spec has no record of why not. The mechanism drifts one refactor at a time. "Why this shape" is where the crystallised insight lives so it survives contact with new engineers.

#### DO

- Open with the naive approach and its cost, then the inversion.

  **Example (pass):** *"The problem: every backend does the same tree walk but writes to a different medium; if each backend implements the walk, you get N copies of reconciliation logic that drift. The inversion: `translateFrom` is defined once on the base and never overridden; backends contribute only `updateSelf`, `childCollections`, and `createChildXxx`."* Reader now knows what the pivot is and why nothing else would work.

- Name each discipline with an italicised lead phrase and explain what breaks without it.

  **Example (pass):** *"Behavior lives in mixins; state lives in composition."* One sentence: mixins give polymorphism without duplicating state; composition gives a swappable payload without leaking format details up into the tree. *"Backends never reach sideways."* One sentence: shared behavior lives one layer up, never in a peer — that is what makes adding a backend purely additive.

- Name the reference instance when one exists and say what it exercises.

  **Example (pass):** *"Document backends are the reference implementation because they exercise the contract minimally. Diagrams add positioning as a middle abstraction layer; code backends add AST manipulation the same way. The pattern doesn't change — the middle layer varies."* A new reader knows exactly which existing code to study first.

- Keep it to three or four short paragraphs. Length is not the point — density is.

  **Example (pass):** four paragraphs, one insight each, no more than three sentences per paragraph, no wall-of-text explanations of the file structure (that lives in the File Structure section).

#### DO NOT

- Omit the section.

  **Example (fail):** the mechanism jumps from Overview straight into File Structure. Rules section says "backends must not reach sideways" but there is no explanation of *why*. Future engineers see the rule as arbitrary and negotiate around it.

- Restate the file structure and rules as narrative.

  **Example (fail):** *"This mechanism has a base class called StoryNode and four backend slots: node, element, map, synchronizer. The node mixin implements three methods. The element holds the serializable payload."* This is a description, not an insight. The reader learns nothing they wouldn't learn from the File Structure and Class Specification sections below.

- Praise the mechanism without naming the alternative it rejected.

  **Example (fail):** *"This mechanism cleanly separates concerns and enables extensibility."* Any mechanism could claim this. The reader has no way to tell which "obvious improvement" would violate the design or why.

- Bury the pivot in a wall of text.

  **Example (fail):** two pages of prose covering history, evolution, contributors, and considered-but-rejected variants — but the reader still can't answer "what is the one thing I must not change?" after reading it. Density beats length.

- Duplicate content from the Rules section.

  **Example (fail):** the "Why this shape" section is a bulleted list identical to the Rules section without any explanation of the trade-off each rule protects. The two sections should feed each other: rules state what must be true, "Why this shape" states why breaking any of them collapses the mechanism.

**Source:** Grill-me conversations produce the most valuable design content in the whole spec, and it evaporates fastest without an explicit home. This section is that home.
