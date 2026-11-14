# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the saved graph of the session's folder (`.context/graph.json`, which exists only after `graph.load_working_copy` has run on that folder); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `space/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (markdown: C:/dev/abd-cdd-cdd-chat-small-improveme/.context/bounded-context-map.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-10 05:23:03 UTC
**Project:** abd-cdd-cdd-chat-small-improveme
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\cdd-chat-small-improvements\validation-reports\ddd-bounded-context-20261110T052258.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 21

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `ubiquitous-language-everywhere`

One term per concept, taken from the business, used identically on the map, in the model, in the code, and in the tests. A technical synonym makes every reader keep a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (ubiquitous-language-everywhere):

### `model-the-domain-not-the-implementation`

Model what the business does, not what the current database, screens, or vendor API expose. A model shaped by an existing implementation locks in decisions nobody chose on purpose.

Evaluate the current context against this rule (model-the-domain-not-the-implementation):

### `vocabulary-traces-to-domain-source`

Trace every term back to domain experts or an upstream artifact. Invent a word and each layer keeps its own glossary.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before locking a context boundary or aggregate, read every referenced segment, sketch, grill-answer, and handoff in full. Titles and indexes show words, not mechanics; a boundary drawn from headings alone misses coupling that shows up only in the prose.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-concepts`

Only model contexts, aggregates, and types the source describes or the user explicitly asks for. Invented contexts and DTO-shaped nouns become code nobody asked for and integrations nobody planned.

Evaluate the current context against this rule (do-not-invent-concepts):

### `experts-words-preferred`

Use the words domain experts use. An invented synonym becomes a second term every reader must translate.

Evaluate the current context against this rule (experts-words-preferred):

### `domain-concepts-not-technical-names`

Name contexts, aggregates, and concepts — not `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, or `*Request`. Do not invent a type for fields that already belong on a concept. A technical name carries no meaning the business would recognize, so rules parked on it cannot be found where the concept lives and get re-implemented elsewhere.

Evaluate the current context against this rule (domain-concepts-not-technical-names):

### `bc-by-lifecycle-not-ui-themes`

Partition by ubiquitous language and how fast the model changes, not by UI themes or journey stages. Do not mint journey-themed contexts that duplicate core domain contexts. Screens and journeys are redrawn while language boundaries hold; a boundary cut along the UI has to move with every redesign and drags the model with it.

Evaluate the current context against this rule (bc-by-lifecycle-not-ui-themes):

### `one-meaning-per-context`

Inside a context, one definition per term; name and translate false cognates across contexts. Several aggregates per context is normal. Do not wrap each aggregate in its own bounded context. Two meanings under one word become contradictory code that both looks consistent; a context per aggregate walls one language off from itself and charges integration cost for nothing.

Evaluate the current context against this rule (one-meaning-per-context):

### `bc-above-aggregate`

A bounded context names a business area, department, or system collection with its own ubiquitous language — not a single aggregate. If the only candidate context is one aggregate, nest it under a broader context or record it as an **Integrations:** arc; omit the `###` heading. No real language boundary is better than a heading that merely duplicates an aggregate name.

Evaluate the current context against this rule (bc-above-aggregate):

### `one-module-per-context-when-small`

A consolidated custom context with only a handful of collaborating types is one clean-engineering module, not one package per aggregate or per class. Several entities under one `#### {module}/` is normal; four modules for four classes in the same context is the packaging version of `bc-above-aggregate`.

Evaluate the current context against this rule (one-module-per-context-when-small):

### `aggregate-clusters-entities`

An aggregate is a consistency cluster with a chosen root and the entities inside it — not one `####` heading per entity class. Several `#####` entities under one aggregate is normal; five aggregates for five account types that share one customer file is the same mistake at a finer grain.

Evaluate the current context against this rule (aggregate-clusters-entities):

### `integrations-cross-context-only`

**Integrations:** arcs cross a bounded-context boundary only. Another entity or aggregate in the same context is a property on the type that uses it — not an integration.

Evaluate the current context against this rule (integrations-cross-context-only):

### `dependency-fields-tracked`

Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc that names only a neighbor context does not tell anyone what to build.

Evaluate the current context against this rule (dependency-fields-tracked):

### `no-orphan-contexts`

Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.

Evaluate the current context against this rule (no-orphan-contexts):

### `vendor-not-implementation`

The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere, because they can change while the domain meaning remains stable.

Evaluate the current context against this rule (vendor-not-implementation):

### `context-tree-bc-aggregate-concept`

Three levels on the bounded_context card only: BC → Aggregate → concept. Classes, stereotypes, and repositories wait for **model**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.

Evaluate the current context against this rule (context-tree-bc-aggregate-concept):

### `bounded-context-file-marks-the-folder`

In code, a bounded context is the folder that contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and each aggregate folder under it. A folder of classes with no such file is a module or a package, so the map and the tree disagree about where the language boundary is.

Evaluate the current context against this rule (bounded-context-file-marks-the-folder):

### `link-arrow-target`

Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.

Evaluate the current context against this rule (link-arrow-target):

### `hang-deps-on-owning-bc`

Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.

Evaluate the current context against this rule (hang-deps-on-owning-bc):

### `user-facing-system-first`

The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

Evaluate the current context against this rule (user-facing-system-first):
