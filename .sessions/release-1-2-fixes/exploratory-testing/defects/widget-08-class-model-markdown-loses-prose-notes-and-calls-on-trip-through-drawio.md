# A class model's markdown rendered to drawio and back is overwritten without its front matter, descriptions, property and operation notes, and collaborator calls, and gains relationships nobody wrote

- **Charter:** Round 1 - generate, validate, render and the fidelity output choices as an agent that spells names every way
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a class model's trip through the formats.
- **Module and class:** `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save` (writes over the source model), with the Clean Engineering adapters `cdd_guidance/practices/clean_engineering/model/markdown` and `model/drawio`.
- **Severity:** wrong result (a person's model file is rewritten with less than it held)

## Steps
Sandbox `repo`, session `main` (`drv\c9.json`). `src/.context/src-model.md` written after `templates/class-model.md`:

    ---
    fidelity: [model]
    artifact: [ce-domain-model]
    format: md
    ---

    # Orders

    **Module:** `src`

    Orders a customer places at the bookshop.

    ---

    ## Order

    An order and its lines.

    ### **Order** <<Aggregate Root>>

    + Order(lines: list[OrderLine])
    ------
    + lines: list[OrderLine]
    	// the books ordered
    + << composition >> lines: list[OrderLine]
    ----
    + total(): Money
    	-> OrderLine.price
    	// the sum of the lines' prices
    + cancel(reason: str): OrderCancelled
    	// an order already shipped is refused

    ### **OrderLine** <<Value Object>>

    + OrderLine(title: str, price: Money)
    ------
    + title: str
    + price: Money

1. `render.render {"guidance": "clean-engineering-model", "format": "drawio", "paths": ["src/.context/src-model.md"], "source": "markdown"}`
2. `render.render {"guidance": "clean-engineering-model", "format": "markdown", "paths": ["src/.context/src-model.drawio"], "source": "drawio"}`

## Expected
"The same classes, operations, and relationships must appear in every selected representation" (`clean_engineering.md`, model fidelity). What the drawing cannot hold (prose, notes) is kept from the markdown already there, or the render does not write over the richer file.

## Actual
Step 2 answers the path of src-model.md, which now reads in full:

    # Orders

    ## Order <<Aggregate Root>>

    + Order(lines: list[OrderLine])
    ------
    + << composition >> lines: list[OrderLine]
    + << composition >> lines: list[OrderLine]
    ----
    + total(): Money
    + cancel(reason: str): OrderCancelled

    ## OrderLine <<Value Object>>

    + OrderLine(title: str, price: Money)
    ------
    + title: str
    + << association >> price: Money
    ----

Lost: the front matter, the Module line, both descriptions, the group heading, every `//` note, and the call `-> OrderLine.price`. Changed: the class headings are no longer the template's `### **Name**`; the plain property `lines` became a second composition; `price: Money` became an association.

## Tier that should catch it
Unit: `class_dependency_round_trip_spec.py` / `class_heritage_round_trip_spec.py` cover relationships on a trip; none compares a model written after the template, with notes and calls, before and after markdown -> drawio -> markdown.

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on port 48933, on a fresh repository of my own (`C:\dev\_et\sparky\confirm\widget\wz.py`; the report's `drv` files are not in the report). After markdown to drawio to markdown, `src-model.md` is the report's text word for word, with the doubled `<< composition >> lines` and `<< association >> price: Money`. Where the loss is, in three places: (1) the drawing does not hold the prose, the `//` notes or the call `-> OrderLine.price` (none of those words is in `src-model.drawio`), so the markdown-to-drawio side drops them; (2) the adapter that reads the drawing adds what nobody wrote, a second composition for `lines` and an association for `price`; (3) the save writes that poorer text over the person's file whole, front matter and group heading included.
- Cause, if you found it: The Clean Engineering model's drawio adapter for (1) and (2); `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save` for (3).
- Shares its cause with: widget-04, widget-05
