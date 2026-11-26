---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check Clean Engineering Code Through The Graph

Story map: [Check Clean Engineering Code Through The Graph](../../../../.context/story-map.md#e-check-clean-engineering-code-through-the-graph). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds today and names the code that runs it, the rules in `cdd_guidance/practices/clean_engineering/rules/` reading the facts `reading/compared_facts.py` records across the graph, with each example in `rules/fixtures/cross_file_examples.py`; `rules/cross_file_rules_spec.py` and the story test beside this file run them. Built on 2026-11-22, step 2 of `.sessions/_backlog/check-clean-engineering-across-files.md`.

### Domain terms

- ++rule of scope all++ — a graph rule about how files use one another, which validate runs over the whole working copy whatever paths it is given, reporting what it finds outside them marked. A judged one lists its candidates outside those paths only when validate is asked for the judged pass.
- ++candidate++ — what a rule lists for a judge or a person to read; it is never a violation. A checked rule may list a candidate beside the violations it decides.
- ++own names++ — the names a body gives its own values: its parameters and its locals.

> In steps: the billing project holds `billing/invoice.py`, whose class Invoice totals its lines, and `shipping/parcel.py`, whose class Parcel costs its items; the desk project holds a Desk, a Clerk, an Archive, and a Board; the checks project holds a registry of the checks Alpha, Beta, and Gamma; the store project holds a Cart and a Till; and the shop project holds the modules shop, pricing, stock, and tax, each with its module card.

## Story: Judge Clean Engineering Rules Across Files

### Evidence

Observed (`operation_checks.py` `EliminateDuplication`, `UseConsistentNaming`; `cross_file_rules.py` `HoldStateOnTheObject`, `SeamNamesCurrentCode`; `coupling_rules.py` `DoNotInventParallelObjectModels`).

#### Scenario: List operations in different files that do the same work, once as a group

*Given* Invoice.total in `billing/invoice.py` and Parcel.cost in `shipping/parcel.py` total their lines with the same four statements, each under own names of its own
*When* the graph rules run
*Then* eliminate-duplication lists both operations in one candidate

#### Scenario: Report a body copied word for word

*Given* Invoice.total and Parcel.total have the same body, word for word
*When* the graph rules run
*Then* eliminate-duplication reports Parcel.total as a violation the graph decides
  *And* it lists no group of the two beside it

#### Scenario: List two verbs for one concept

*Given* Cart has get_order and Till has fetch_order
*When* the graph rules run
*Then* use-consistent-naming lists both operations, the target order, and the verbs fetch and get

#### Scenario: Report a module card the code has moved on from

*Given* the shop card names Basket in its seam and stock and `ledger/books` as dependencies, and the shop code imports tax
*When* the graph rules run
*Then* seam-names-current-code reports the seam term, the dependency not imported, the dependency that is no folder, and the import the card does not name
  *And* each is a violation the graph decides, not a candidate

#### Scenario Outline: Report each rule's failing example and pass its repaired example

*Given* the failing example and the repaired example of <rule>
*When* the graph rules run
*Then* <rule> lists the failing example
  *And* it lists nothing in the repaired example

| rule |
| --- |
| eliminate-duplication |
| hold-state-on-the-object-not-in-parameters |
| do-not-invent-parallel-object-models |
| use-consistent-naming |
| seam-names-current-code |

#### Scenario: Run each rule over the whole working copy

*Given* the rules that compare files
*When* validate is given paths
*Then* each rule still runs over the whole working copy

## Story: Judge Passed Parameters And Second Registries

#### Scenario: List a parameter handed down to two other classes

*Given* Desk.open hands its session to Clerk.file, which hands it to Archive.store
*When* the graph rules run
*Then* hold-state-on-the-object-not-in-parameters lists Desk.open, naming the session and each operation it passes

#### Scenario: Pass a parameter handed between one class's own operations, or to a constructor

*Given* Desk.open hands its session only to Desk's own operations, or to the constructor of the Clerk made for it
*When* the graph rules run
*Then* hold-state-on-the-object-not-in-parameters lists nothing

#### Scenario: List a class every operation of which takes the same parameter

*Given* each of Board's three operations takes a ticket
*When* the graph rules run
*Then* hold-state-on-the-object-not-in-parameters lists Board

#### Scenario: List a second registry of the same classes

*Given* `report/listing.py` lists Alpha, Beta and Gamma, which `checks/registry.py` already holds
*When* the graph rules run
*Then* do-not-invent-parallel-object-models lists both collections and the classes they share

#### Scenario: Pass a list of exported names, and one that spells the classes' names as labels

*Given* `checks/__init__.py` exports Alpha, Beta and Gamma in `__all__`, and `report/listing.py` lists their names as strings
*When* the graph rules run
*Then* do-not-invent-parallel-object-models lists nothing
