---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Produce Formal Artifacts

Story map: [Produce Formal Artifacts](../../../.context/story-map.md#e-produce-formal-artifacts). Session release-1-2-fixes.

**Evidence modes.** *Observed* scenarios hold for the UX format adapters today (`cdd_guidance/practices/ux/model`) and each names the spec that runs it. *Intended* scenarios say what a trip should keep where a format cannot hold it yet; each names the evidence still missing. They were written after round 3 of exploratory testing (defects r3-gizmo-01, 02, 04, 05) showed that no scenario covered a UX map's trip between the formats its fidelity offers.

These scenarios belong to the story Take Artifact To Another Format And Back, whose other scenarios are in `take_artifact_to_another_format_and_back_story.test.md`; they are kept in a file of their own because they are about the UX map.

### Domain terms

- ++UX map++ — the screens, their regions and controls, and the transitions between screens, which every UX format writes.
- ++UX context++ — `ux-context.md`: the UX map's scope, invariants and notes, which hold no screen.
- ++callout++ — the note the drawing shows under a screen: the stories the screen shows and the domain terms it names.
- ++view++ — a front-end screen in production code, `*View.tsx` or `*View.jsx`, written at the front-end code fidelity.

> In steps: the bookshop's files are the examples below.

## Examples

### UX files of the bookshop project

| file | holds |
| --- | --- |
| ++bookshop/.context/information-architecture.drawio++ | the drawing of the ++UX map++: Book List, Book Details, Cart, Checkout, their regions, and the transitions between them |
| ++bookshop/.context/ux-context.md++ | the ++UX context++: `Scope: Browse Books, Fill Cart`, one invariant, one note |
| ++bookshop/buy-a-book.html++ | the mockup: on Book Details the region Add To Cart with Quantity (number) and the buttons Add to cart and Back to list; on Checkout the region Payment with Street (text), Country (dropdown), Save this card (checkbox) and the button Pay |
| ++bookshop/src/CheckoutView.tsx++ | the Checkout ++view++ |

## Story: Take Artifact To Another Format And Back

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/ux/ux.md`, Guidance | the channels are "peers at the same fidelity"; ia holds "Screens, layouts, named regions, transitions, nav components, content types. Story names and domain terms attach as traces"; at mockup "drawio remains a peer channel" |
| `cdd_guidance/actions/render/rendered_file.py` `RenderedFile` | a render reads the file as it is before the render, so "a document keeps the words its source does not hold" |
| `cdd_guidance/practices/ux/ux.md`, `front_end_code` | the fidelity writes `typescript` and `javascript` |
| Defects r3-gizmo-01, 02, 04, 05 | each render between the drawing and the UX context emptied the other file; a drawing read back had none of the stories, domain terms, layouts, areas or controls it was drawn from, and a region named after two buttons; the front-end code fidelity's default format was one it does not write, and a render of a view failed with a list of other formats |

#### Scenario: Keep the UX context when the drawing is rendered to markdown

Observed (`cdd_guidance/practices/ux/ux_spec.py`, "a UX map rendered over the other file its fidelity keeps").

*Given* ++bookshop/.context/ux-context.md++ holds the scope, one invariant and one note
*When* Claude Code renders ++bookshop/.context/information-architecture.drawio++ to markdown
*Then* ++bookshop/.context/ux-context.md++ holds the same scope, invariant and note

#### Scenario: Keep the drawing when the UX context is rendered to drawio

Observed (`ux_spec.py`, the same subject).

*Given* ++bookshop/.context/information-architecture.drawio++ draws four screens
*When* Claude Code renders ++bookshop/.context/ux-context.md++ to drawio
*Then* ++bookshop/.context/information-architecture.drawio++ is as it was, with its four screens and their transitions

#### Scenario: Keep the invariants a map does not hold when it is rendered to markdown

Observed (`ux_spec.py`, the same subject).

*Given* a ++UX map++ in JSON with the scope `Place New Order` and no invariant
  *And* ++bookshop/.context/ux-context.md++ holds one invariant
*When* Claude Code renders the map to markdown
*Then* ++bookshop/.context/ux-context.md++ holds `Scope: Place New Order`
  *And* it still holds its invariant

#### Scenario: Read back the stories and domain terms a drawing shows

Observed (`cdd_guidance/practices/ux/model/drawio/drawio_ux_map_spec.py`; drawn through the command line in `drawio_ux_map_heavy_spec.py`).

*Given* the drawing shows the ++callout++ `Stories: Add Book To Cart · View Book`, `Domain terms: Book · Cart Line` under Book Details
*When* Claude Code renders ++bookshop/.context/information-architecture.drawio++ to JSON
*Then* Book Details shows the stories Add Book To Cart and View Book
  *And* it names the domain terms Book and Cart Line
  *And* each other screen has the stories of the ++callout++ under its own box

#### Scenario: Read back a screen's layout, each region's area, and a transition's kind of navigation

Observed (`drawio_ux_map_spec.py`; `drawio_ux_map_heavy_spec.py`).

*Given* a ++UX map++ whose Book Details has the layout split-screen, whose regions fill the areas panel and body, and whose transition Check out is a top nav
*When* Claude Code renders the map to drawio, then the drawing back to JSON
*Then* Book Details has the layout split-screen
  *And* its regions fill the areas panel and body
  *And* the transition Check out is a top nav

#### Scenario: Read back the controls a drawing shows, in their own regions

Observed (`drawio_ux_map_spec.py`; `drawio_ux_map_heavy_spec.py`).

*Given* ++bookshop/buy-a-book.html++ holds the mockup
*When* Claude Code renders ++bookshop/buy-a-book.html++ to drawio, then the drawing back to JSON
*Then* Book Details has the regions Book Summary and Add To Cart, and no other
  *And* Add To Cart holds Quantity (number), then the buttons Add to cart and Back to list
  *And* Payment holds Street (text), Country (dropdown), Save this card (checkbox), then the button Pay

#### Scenario: Read the controls of a drawing that keeps no control types

Observed (`drawio_ux_map_spec.py`).

*Given* a drawing made before the drawing kept each control's type, with the row `Quantity` and the action strip `Add to cart · Back to list` in Add To Cart
*When* Claude Code renders the drawing to JSON
*Then* Add To Cart holds Quantity with no type, then the buttons Add to cart and Back to list

#### Scenario: Keep what a drawing does not show

Intended. Evidence still missing: where the drawing keeps them is the person's decision. A drawing shows no state or interaction of a control, no story step a control runs, no description of a screen, no content type or nav component, and not the map's name, so a mockup read back from its drawing has none of them.

*Given* ++bookshop/buy-a-book.html++ holds controls with states, interactions and story steps
*When* Claude Code renders ++bookshop/buy-a-book.html++ to drawio, then the drawing back to html
*Then* each control still has its states, its interactions and its story steps

#### Scenario: Start the front-end code fidelity in a format it writes

Observed (`ux_spec.py`, "Ux fidelity and format defaults").

*Given* a session that works on UX
*When* the session moves UX to the front-end code fidelity
*Then* UX works in typescript, one of the formats that fidelity writes

#### Scenario: Refuse to render a view

Observed (`ux_spec.py`, "a front-end view rendered to another format").

*Given* ++bookshop/src/CheckoutView.tsx++ holds the Checkout ++view++
*When* Claude Code renders ++bookshop/src/CheckoutView.tsx++ to javascript
*Then* the render is refused: UX front-end views are written by hand, not rendered
  *And* ++bookshop/src/CheckoutView.tsx++ is not read as a mockup page

#### Scenario: Render a view between typescript and javascript

Intended. Evidence still missing: whether a view is rendered at all, and by which practice, is the person's decision (defect r3-gizmo-05); today the render is refused, as the scenario above says.

*Given* ++bookshop/src/CheckoutView.tsx++ holds the Checkout ++view++
*When* Claude Code renders ++bookshop/src/CheckoutView.tsx++ to javascript
*Then* `bookshop/src/CheckoutView.jsx` holds the same ++view++
