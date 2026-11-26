# widget-7: The story explorer's class card shows a class model's markdown marks as text: the title reads "**Cart** «Aggregate Root»" and the language reads "The *Cart* is…", "- **Lines.** The Cart…"

- **Charter:** C4
- **Tester:** Widget
- **Story:** Explore Stories In Story UI (class cards a step's term opens); `clean_engineering.md` model fidelity "Open each class card with its language … the whiteboard and the story explorer show the card it heads".
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/class_cards.py` `ClassCard.from_section` (strips only the `#` marks and turns `<< >>` into « »); `explorer.dc.html` draws `{{cardTitle}}` and `{{cardText}}` as plain text (`white-space:pre-wrap`).
- **Severity:** cosmetic (paragraph breaks and bullets do survive; the bold and italic marks show as asterisks)

## Steps

1. A project whose class model follows `cdd_guidance/practices/clean_engineering/templates/class-model.md` (`### **Cart** <<Aggregate Root>>`, language with `*Cart*` and `- **Lines.** …`), e.g. `cdd_guidance/practices/clean_engineering/model/fixtures/bookshop/ordering-model.md` copied to `src/ordering/.context/class-model.md`.
2. A scenario step linking a term to it: `*Given* the Bookshop sells ++[Shop Cart](../../src/ordering/.context/class-model.md#cart-aggregate-root)++ Tiny Tales`.
3. Draw the explorer (as `choose_lines_explorer_spec._drawn_tree`) and read `classCards()` in the page.

## Expected

The card's title "Cart «Aggregate Root»" (as pml-web's `#### Cart <<Aggregate Root>> <<Entity>>` gives "Cart «Aggregate Root» «Entity»"), and the language without literal `*` / `**`, or drawn as emphasis.

## Actual

```
title: "**Cart** «Aggregate Root»"
text:  "The *Cart* is the books a customer means to buy, …\n\n- **Lines.** The Cart adds a *CartLine* …"
```
Every class model written from the Clean Engineering template (bold class headings, italic terms, bold responsibility names) shows this way.

## Tier that should catch it

Unit: a `class_cards` example over a template-shaped heading and language; the existing examples use pml-web's unbolded `####` headings.

## Also seen by
