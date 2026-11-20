---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check Artifacts Against Rules

Story map: [Check Artifacts Against Rules](../../../.context/story-map.md#e-check-artifacts-against-rules). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for the Validate action today (`cdd_guidance/actions/validate`). They were written after exploratory testing round 1 (defects widget-03, 10) showed that what the tool's description says of `rule` and `graph` had no scenario.

### Domain terms

- ++rule++ — one named check of a practice or fidelity, such as `verb-noun-format` (`harness/guidance/rule.py` `Rule`).
- ++session's graph++ — the knowledge graph the session holds; a validate naming `graph: true` checks it, built from what the fidelity has written when none is saved (`CheckedGraph`).
- ++written output++ — the folders a fidelity declares its files in, such as each module folder under the practice's root for code.

> In steps: the bookshop project and its files are the examples below.

## Examples

### rules a call names

| rule | of |
| --- | --- |
| ++verb-noun-format++ | stories-story-map |
| ++child-count-fits-layer++ | stories-story-map |
| ++no-such-rule++ | no guidance |

### files of the bookshop project

| file | holds |
| --- | --- |
| ++.context/story-map.md++ | the story map: Sell Books, Take Orders, Place Order |
| ++src/orders/order.ts++ | class Order, whose place operation takes five parameters, more than limit-operation-parameters allows |
| ++no/such/graph.json++ | not there |

## Story: Validate Artifact Against Rules

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/actions/validate/validate.py` `Validate.validate` | "rule: ... one rule to check. Omit it to walk each guidance's rules"; "graph: true for the session's graph ... created for the session and loaded when it is missing"; "With no paths and no graph, the folders holding the fidelity's written output are checked" |
| Defects widget-03, widget-10 | a rule's name was refused by the tool's schema; graph: true with no paths, and no arguments at all, answered No graph checked for code |

#### Scenario: Check the one rule a call names

Observed.

*Given* ++.context/story-map.md++ holds the story map
*When* Claude Code validates stories-story-map on ++.context/story-map.md++ with rule ++verb-noun-format++
*Then* the report hands the judge ++verb-noun-format++
  *And* the report leaves ++child-count-fits-layer++ out

#### Scenario: Refuse a rule no listed guidance has

Observed.

*Given* ++.context/story-map.md++ holds the story map
*When* Claude Code validates stories-story-map on ++.context/story-map.md++ with rule ++no-such-rule++
*Then* the call is refused, saying there is no rule ++no-such-rule++
  *And* the refusal lists ++verb-noun-format++ among the rules there are

#### Scenario: Check the session's graph built from the written output

Observed.

*Given* ++src/orders/order.ts++ holds class Order, whose place operation takes five parameters
  *And* the session has no saved graph
*When* Claude Code validates clean-engineering-code with graph true and no paths
*Then* the report holds the limit-operation-parameters violation in ++src/orders/order.ts++

#### Scenario: Refuse a graph file that is not there

Observed.

*Given* ++no/such/graph.json++ is not in the project
*When* Claude Code validates clean-engineering-code with graph ++no/such/graph.json++
*Then* the call is refused, naming ++no/such/graph.json++ as not there, read from the project's root

#### Scenario: Report two describes that share a subject however the spec quotes them

Observed (`cdd_guidance/practices/bdd/rules/shared_describe_subject_spec.py`). Written after exploratory testing round 3 (defect r3-rivet-10): the rule saw only Python describes written in double quotes.

*Given* a Mamba spec written in single quotes, and a Vitest spec, each hold the top-level describes `a bare agentic toolset registered for deploy` and `a bare agentic toolset with mcp-published operations registered for deploy`
*When* Claude Code validates each spec at ++bdd-behavior++
*Then* each spec carries a shared-describe-subject violation naming both describes
