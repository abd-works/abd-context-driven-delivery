You just edited C:\dev\abd-context-driven-delivery\sandbox\mm3e\no-yaml\story-map.md. Check that edit against these rules and fix anything that does not follow them:
vocabulary-traces-to-domain-source
read-all-source-context-in-full
do-not-invent-requirements
evidence-distinguishes-observed-inferred-and-intended
verb-noun-format
story-name-captures-system-mechanic
four-to-nine-children
branch-on-mechanical-uniqueness
right-size-story-nodes
behaviours-not-one-time-tasks
**/*story-map*
**/*_story.test.*
**/*story_test*
**/*story-test*
**/*-sketch.md

## Shared rules

```yaml
alwaysApply: false
globs: "**/*story-map*,**/*_story.test.*,**/*story_test*,**/*story-test*,**/*-sketch.md"
```

Whenever you define or change user interactions and resulting system behavior, at any level of detail. Follow these rules.

- **`vocabulary-traces-to-domain-source`** - Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.
- **`read-all-source-context-in-full`** - Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.
- **`do-not-invent-requirements`** - Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.
- **`evidence-distinguishes-observed-inferred-and-intended`** - Label behaviour as observed, inferred, or intended and cite its source. When available evidence cannot exercise required behaviour, write the intended GWT and state the limitation, because an unobserved expectation must not be presented as a fact.

---

#### Rules

```yaml
alwaysApply: false
globs: "**/*story-map*,**/*-sketch.md"
```

Whenever you create, alter, or delete epics, sub-epics, or stories on the map, or change scenarios or acceptance work that forces a map change. Follow these rules.

If this change will not stay here, follow `practices/stories.mdc`.

- **`verb-noun-format`** - Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.
- **`story-name-captures-system-mechanic`** - At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.
- **`four-to-nine-children`** - Keep 4-9 direct children, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes.
- **`branch-on-mechanical-uniqueness`** - Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.
- **`right-size-story-nodes`** - Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.
- **`behaviours-not-one-time-tasks`** - Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

---