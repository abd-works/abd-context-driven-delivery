---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Report Unused And Poorly Connected Code

Story map: [Report Unused And Poorly Connected Code](../../../../.context/story-map.md#e-report-unused-and-poorly-connected-code). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds today and names the code that runs it, `cdd_guidance/practices/clean_engineering/rules/cross_file_rules.py` (`PutLogicOnTheOwningResource`) reading the fact `reading/owned_dependencies.py` records, with each example in `rules/fixtures/cross_file_examples.py`; `rules/cross_file_rules_spec.py` and the story test beside this file run them. Built on 2026-11-22, step 2 of `.sessions/_backlog/check-clean-engineering-across-files.md`.

### Domain terms

- ++dependency++ — an edge the graph records from one class of the code to another class it creates, calls, or reads, with how the class reaches the other (created on each call, created in the constructor, looked up by name, held as a field, handed in as a parameter) and the operations it reaches it from.
- ++candidate++ — what a judged rule lists for a judge or a person to read; it is never a violation. A judged rule of scope all lists its candidates in the paths a validate is given on every validate, and over the rest of the working copy only when the validate asks for the judged pass.

> In steps: the shop project holds `shop/price_list.py`, whose class PriceList is made from a currency, `shop/depot.py`, whose class Depot a class operation finds by name, `shop/note.py`, whose class Note shows a message, and `shop/cart.py`, whose class Cart totals the cart.

## Story: Report Runtime Dependency That Should Be Owned

### Evidence

Observed (`cross_file_rules.py` `PutLogicOnTheOwningResource`, `owned_dependencies.py` `DependenciesToOwn`). The rule is `put-logic-on-the-owning-resource`, judged, of scope all.

#### Scenario: List a class that builds another on each call from strings

*Given* Cart's operation total builds `PriceList("usd")` on each call
*When* the graph rules run
*Then* put-logic-on-the-owning-resource lists Cart as a candidate, saying it builds a PriceList on each call in total
  *And* the candidate names Cart as the owner to consider, with the PriceList as a part it builds once and keeps (composition) or one handed to it and held (association)

#### Scenario: List a class that looks another up by name

*Given* Cart's operation park finds a Depot by name, `Depot.named("north")`
*When* the graph rules run
*Then* put-logic-on-the-owning-resource lists Cart as a candidate, saying it looks up a Depot by name in park

#### Scenario Outline: Pass a dependency that is owned or handed in

*Given* Cart reaches PriceList <how>
*When* the graph rules run
*Then* put-logic-on-the-owning-resource lists nothing

| how |
| --- |
| through a field that holds the PriceList it was handed |
| through a PriceList handed to the operation as a parameter |
| through the PriceList its constructor builds and keeps |

#### Scenario: Pass a class built on each call from a formatted message

*Given* Cart's operation warn builds `Note(f"no price for {sku}")` on each call
*When* the graph rules run
*Then* put-logic-on-the-owning-resource lists nothing

#### Scenario: Report a rule's failing example and pass its repaired example

*Given* the failing example, where Cart builds a PriceList on each call, and the repaired example, where Cart holds the PriceList it is handed
*When* the graph rules run
*Then* put-logic-on-the-owning-resource lists the failing example
  *And* it lists nothing in the repaired example

#### Scenario: List the candidates outside the paths given only when validate asks for the judged pass

*Given* Cart builds a PriceList on each call in `shop/cart.py`
*When* Claude Code validates clean-engineering-model on `docs` without the judged pass
*Then* the report lists no put-logic-on-the-owning-resource candidate
  *And* validated on `shop` without the judged pass, it lists the candidate, as it lists every candidate in the paths given
  *And* validated on `docs` with the judged pass, it lists the candidate in `shop/cart.py`, marked as found outside the paths given
