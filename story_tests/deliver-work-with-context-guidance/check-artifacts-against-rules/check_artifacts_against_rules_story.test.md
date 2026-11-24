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

#### Scenario: Name a path the graph read no node from

Observed (`cdd_guidance/actions/validate/validate_spec.py`). Written after exploratory testing round 3 (defects r3-rivet-02, r3-widget-08): a sketch, a tree in markdown, or a class model in markdown gave the graph no node, and the report read "No graph rule violations. All scanned graph rules passed.", the words a file with checked nodes gets. Validate's description says a path's graph rules "run on" the files named; a file no rule ran on is named so.

*Given* `specs/bookshop-sketch.md` holds a BDD sketch, which no graph reading reads a node from
  *And* ++src/orders/order.ts++ holds class Order, whose place operation takes five parameters
*When* Claude Code validates clean-engineering-code on `specs/bookshop-sketch.md` and ++src/orders/order.ts++
*Then* the report says no graph rule ran on `specs/bookshop-sketch.md`
  *And* the report holds the limit-operation-parameters violation of ++src/orders/order.ts++

#### Scenario: Say no graph rule passed when no named path gave the graph a node

Observed (`cdd_guidance/actions/validate/validate_spec.py`).

*Given* `specs/bookshop-sketch.md` holds a BDD sketch, which no graph reading reads a node from
*When* Claude Code validates clean-engineering-code on `specs/bookshop-sketch.md`
*Then* the report says no graph rule ran on `specs/bookshop-sketch.md`
  *And* the report does not say the graph rules passed

#### Scenario: Refuse an empty path as it refuses a missing one

Observed (`cdd_guidance/actions/validate/validate_spec.py`). Written after exploratory testing round 1 (question widget-14, answered 2026-11-23): an empty path was read as the project's root, so the call checked the whole project nobody named, while a missing path was refused by name.

*Given* ++.context/story-map.md++ holds the story map
*When* Claude Code validates stories-story-map on ++.context/story-map.md++ and a path that is empty or only spaces
*Then* the call is refused, saying an empty path names no file or folder
  *And* no validation report is saved

## Story: Read Validated Files As Their Practice Writes Them

#### Scenario: Report two describes that share a subject however the spec quotes them

Observed (`cdd_guidance/practices/bdd/rules/shared_describe_subject_spec.py`). Written after exploratory testing round 3 (defect r3-rivet-10): the rule saw only Python describes written in double quotes.

*Given* a Mamba spec written in single quotes, and a Vitest spec, each hold the top-level describes `a bare agentic toolset registered for deploy` and `a bare agentic toolset with mcp-published operations registered for deploy`
*When* Claude Code validates each spec at ++bdd-behavior++
*Then* each spec carries a shared-describe-subject violation naming both describes

#### Scenario: Give a story test validated alone the place its story map gives it

Observed for the read (`cdd_guidance/practices/stories/stories_spec.py`). Written after exploratory testing round 3 (defect r3-sparky-10): a story test under `story_tests` named without its map was read as a map built from its folders, so validate counted one story in a sub-epic of two and read a flat epic as an epic holding a sub-epic of its own name.

*Given* ++.context/story-map.md++ holds the sub-epic Take Orders with the stories Place Order and Cancel Order
  *And* the story test of Place Order sits under `story_tests/sell-books/take-orders/place-order/` and names the map on a `# Map:` line
*When* Claude Code validates the story test at ++stories-scenarios++, naming no story map
*Then* Take Orders holds Place Order and Cancel Order, as the map does
  *And* Place Order holds the story test's scenarios

#### Scenario: Ask no examples file of an example a markdown scenarios file holds

Observed (`cdd_guidance/practices/stories/rules/acceptance_tests_spec.py`). Written after exploratory testing round 3 (defect r3-sparky-04): each row of an examples table in a markdown scenarios file carried a domain-fixture-example-files violation it could never meet.

*Given* a markdown scenarios file written after `templates/md/scenarios.md` holds its examples as rows of a table
*When* Claude Code validates it at ++stories-scenarios++
*Then* no example of it carries a domain-fixture-example-files violation
