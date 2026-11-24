---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Produce Formal Artifacts

Story map: [Produce Formal Artifacts](../../../.context/story-map.md#e-produce-formal-artifacts). Session release-1-2-fixes.

**Evidence modes.** *Observed* scenarios hold for the UX format adapters today (`cdd_guidance/practices/ux/model`) and each names the spec that runs it. Every scenario here is Observed since the person's second answers of 2026-11-20 settled the two that were Intended: what a mockup's drawing and board hold, and that a view renders between typescript and javascript. They were written after round 3 of exploratory testing (defects r3-gizmo-01, 02, 04, 05) showed that no scenario covered a UX map's trip between the formats its fidelity offers.

These scenarios belong to the story Take Artifact To Another Format And Back, whose other scenarios are in `take_artifact_to_another_format_and_back_story.test.md`; they are kept in a file of their own because they are about the UX map.

### Domain terms

- ++UX map++ — the screens, their regions and controls, and the transitions between screens, which every UX format writes.
- ++UX context++ — `ux-context.md`: the UX map's scope, invariants and notes, which hold no screen.
- ++callout++ — the note the drawing shows under a screen: the stories the screen shows and the domain terms it names.
- ++view++ — a front-end screen in production code, `*View.tsx` or `*View.jsx`, written at the front-end code fidelity.
- ++board++ — a mockup drawn in Claude Whiteboard: a section for each screen and each region, and a card for each control.
- ++served link++ — a story, scenario or step a screen or a control serves, written as a markdown link to the file and heading it is written at.

> In steps: the bookshop's files are the examples below.

## Examples

### UX files of the bookshop project

| file | holds |
| --- | --- |
| ++bookshop/.context/information-architecture.drawio++ | the drawing of the ++UX map++: Book List, Book Details, Cart, Checkout, their regions, and the transitions between them |
| ++bookshop/.context/ux-context.md++ | the ++UX context++: `Scope: Browse Books, Fill Cart`, one invariant, one note |
| ++bookshop/buy-a-book.html++ | the mockup: on Book Details the region Add To Cart with Quantity (number) and the buttons Add to cart and Back to list; on Checkout the region Payment with Street (text), Country (dropdown), Save this card (checkbox) and the button Pay |
| ++bookshop/src/CheckoutView.tsx++ | the Checkout ++view++, written in TypeScript: the component CheckoutView, which takes the props cart, onPaid and note, and hands its events the handlers handleCity and handlePay |

### what the mockup's Book Details serves

| served by | kind | ++served link++ |
| --- | --- | --- |
| the screen Book Details | story | `[Add Book To Cart](story_tests/shop/fill-cart/fill_cart_story.test.md#story-add-book-to-cart)` |
| the screen Book Details | story | `View Book`, a name with no link |
| the screen Book Details | scenario | `[Add Book To Cart › Add one book](story_tests/shop/fill-cart/fill_cart_story.test.md#scenario-add-one-book)` |
| the control Quantity in Add To Cart | step | `[Add Book To Cart › Add one book › the Customer adds 2 copies](story_tests/shop/fill-cart/fill_cart_story.test.md#scenario-add-one-book)` |
| the control Add to cart in Add To Cart | scenario | the scenario link above, and `Add Book To Cart › Add a second book`, a name with no link |
| the control Back to list in Add To Cart | | nothing |

## Story: Take Artifact To Another Format And Back

### Evidence

| Source | Note |
|--------|------|
| `cdd_guidance/practices/ux/ux.md`, Guidance | the channels are "peers at the same fidelity"; ia holds "Screens, layouts, named regions, transitions, nav components, content types. Story names and domain terms attach as traces"; at mockup "drawio remains a peer channel" |
| `cdd_guidance/actions/render/rendered_file.py` `RenderedFile` | a render reads the file as it is before the render, so "a document keeps the words its source does not hold" |
| `cdd_guidance/practices/ux/ux.md`, `front_end_code` | the fidelity writes `typescript` and `javascript` |
| The person's second answers of 2026-11-20 (`closing-brief-round-3.md`, the third wave) | "mockup in whiteboard just needs a way to associate screens and widgets to stories, scenarios, steps": a mockup's whiteboard and drawing show each screen and each control with what it serves, read back without loss; nothing more is asked of the drawings. Front-end views render between TypeScript and JavaScript both ways |
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

#### Scenario: Save a mockup's drawing and its board beside each other in the epic's .context

Observed (`cdd_guidance/practices/ux/ux_render_heavy_spec.py`, through a real cdd server; the declared paths in `ux_spec.py` and `harness/guidance/fidelity_outputs_spec.py`; the diagram chip in `space/kanban/kanban_tools_spec.py`). The person, 2026-11-20: "yes diagram is both drawio and whiteboard".

*Given* ++bookshop/buy-a-book.html++ holds the mockup
*When* Claude Code renders ++bookshop/buy-a-book.html++ to drawio, then to whiteboard
*Then* the drawing is saved as `bookshop/.context/buy-a-book.drawio`
  *And* the ++board++ is saved beside it as `bookshop/.context/buy-a-book.whiteboard`
  *And* each render answers the saved file, and the whiteboard render answers the writes that put the ++board++ in Claude
  *And* ++bookshop/buy-a-book.html++ is as it was

#### Scenario: Show on the drawing what each screen and each control serves

Observed (`drawio_ux_map_spec.py`, "a screen of a UX map drawn as draw.io"; drawn through the command line in `drawio_ux_map_heavy_spec.py`). The person decided that the drawing holds no state, interaction or description of a control; those stay in the html and the JSON.

*Given* the mockup's Book Details serves what the table above lists
*When* Claude Code renders the mockup to drawio
*Then* the ++callout++ under Book Details lists the screen's stories, then its scenarios, then its steps, each ++served link++ as a link to its target and `View Book` as its name
  *And* it has the line `Add To Cart › Quantity serves steps:` with the step's link
  *And* it has no line for Back to list

#### Scenario: Read back from the drawing what each screen and each control serves

Observed (`drawio_ux_map_spec.py`; `drawio_ux_map_heavy_spec.py`, "of a mockup whose screen and controls serve stories, scenarios and steps, that is read back").

*Given* the drawing of the mockup, with the ++callout++ under Book Details
*When* Claude Code renders the drawing to JSON
*Then* Book Details serves the story Add Book To Cart with its link's target, and the story View Book by name
  *And* it serves the scenario and the step the ++callout++ lists, each with its target
  *And* Quantity serves the step, and Add to cart serves the linked scenario and the scenario named with no link
  *And* Back to list serves nothing
  *And* Book Details has the regions Book Summary and Add To Cart, and no other

#### Scenario: Show on the board what each screen and each control serves

Observed (`cdd_guidance/practices/ux/model/whiteboard/whiteboard_ux_map_spec.py`).

*Given* the mockup's Book Details serves what the table above lists
*When* Claude Code renders the mockup to whiteboard
*Then* the ++board++ has a section for Book Details and one for Checkout, and inside Book Details a section for each of its regions
  *And* the card of what Book Details serves lists `Stories:`, `Scenarios:` and `Steps:`, each ++served link++ as a markdown link, then `Domain terms:`
  *And* the card of Quantity shows its name, its type number, and `Steps:` with the step's link
  *And* the card of Back to list shows its name and its type alone
  *And* each transition is an arrow between its screens' sections, labelled with its trigger

#### Scenario: Read back from the board what each screen and each control serves

Observed (`whiteboard_ux_map_spec.py`, "that is read back"; through the practice's render in `ux_spec.py`, "a mockup rendered to its board and back").

*Given* the ++board++ of the mockup
*When* Claude Code renders the ++board++ to JSON
*Then* each screen has its regions with their areas, and each region its controls with their types
  *And* Book Details and each of its controls serve the stories, scenarios and steps the table above lists, each link with its target
  *And* each transition joins the screens it joined, with its kind of navigation
  *And* rendering the map read back to whiteboard gives the same ++board++

#### Scenario: Read a control where a person moved its card on the board

Observed (`whiteboard_ux_map_spec.py`, "on which a person moved a control's card to another region and wrote a story on it").

*Given* a person moved the card of Back to list into the section of Book Summary on the ++board++
  *And* wrote `Stories:` with the link of Add Book To Cart on the card
*When* Claude Code renders the ++board++ to JSON
*Then* Book Summary holds the control Back to list
  *And* Back to list serves the story Add Book To Cart, with its link's target

#### Scenario: Keep where a person put a screen when the board is drawn again

Observed (`whiteboard_ux_map_spec.py`, "that is drawn again over a board on which a person moved a screen").

*Given* a person moved the section of Checkout on the ++board++
*When* Claude Code renders the mockup to whiteboard again
*Then* the section of Checkout is where the person put it

#### Scenario: Start the front-end code fidelity in a format it writes

Observed (`ux_spec.py`, "Ux fidelity and format defaults").

*Given* a session that works on UX
*When* the session moves UX to the front-end code fidelity
*Then* UX works in typescript, one of the formats that fidelity writes

#### Scenario: Render a view from typescript to javascript

Observed (`cdd_guidance/practices/ux/model/view/front_end_view_spec.py`, "a front-end view written in TypeScript"; through the practice's render in `ux_spec.py`, "a front-end view rendered to another format").

*Given* ++bookshop/src/CheckoutView.tsx++ holds the Checkout ++view++, with an interface for its props, typed parameters and results, type arguments, a cast, and an import used only for a type
*When* Claude Code renders ++bookshop/src/CheckoutView.tsx++ to javascript
*Then* the render holds the same ++view++ with every type annotation dropped, and the interface and the type-only import gone
  *And* it has the component CheckoutView, the props cart, onPaid and note, and the handlers handleCity and handlePay
  *And* the words the screen shows, `Total: {cart.total} as charged`, are as they were

#### Scenario: Render a view from javascript to typescript

Observed (`front_end_view_spec.py`, "and back to TypeScript"; `ux_spec.py`).

*Given* the Checkout ++view++ written in JavaScript
*When* Claude Code renders it to typescript
*Then* the render holds the ++view++ as it is written, with no type annotation made up for it
  *And* it has the component CheckoutView, the props cart, onPaid and note, and the handlers handleCity and handlePay

#### Scenario: Render a view onto the view file a person wrote into, losing nothing

Observed (`cdd_guidance/practices/ux/model/view/view_reshape_spec.py`, the same examples for a file in TypeScript and a file in JavaScript; through a real cdd server in `cdd_guidance/practices/ux/ux_render_heavy_spec.py`). The person, 2026-11-21: "re-render must not ever remove what is already there".

*Given* `bookshop/src/CheckoutView.jsx` holds the Checkout ++view++ an earlier render wrote, with a line a person wrote in the body of the handler handlePay
  *And* in ++bookshop/src/CheckoutView.tsx++ the handler handlePay is now named handleCheckout, and the view has gained the handler handleClear
*When* Claude Code renders ++bookshop/src/CheckoutView.tsx++ to javascript
*Then* `bookshop/src/CheckoutView.jsx` still holds handlePay with the person's line, under a comment that says it is no longer in the model
  *And* it holds handleCheckout and handleClear with empty bodies, before what the component returns
  *And* every line the file held is still in it
  *And* the render answers handlePay as kept, with handleCheckout and handleClear as the added members that may have replaced it
  *And* rendering the same ++view++ again changes nothing

#### Scenario: Add a prop or a hook the view gained, and mark one it lost

Observed (`view_reshape_spec.py`).

*Given* a view file whose component CheckoutView takes the props cart and onPaid
*When* Claude Code renders onto it a ++view++ whose component takes cart, onPaid and note, and declares one more hook
*Then* the component takes note beside cart and onPaid, and its opening line as it was is kept above as a comment
  *And* the hook is declared after the hooks the component had
*When* Claude Code renders onto it a ++view++ whose component takes cart alone
*Then* the component still takes onPaid, under a comment that says the prop is no longer in the model

#### Scenario: Keep what only the UX context, the board or the drawing holds when a map is rendered onto it

Observed (`cdd_guidance/practices/ux/model/render_onto_existing_spec.py`; the drawing through the command line in `drawio_ux_map_heavy_spec.py`).

*Given* ++bookshop/.context/ux-context.md++ holds a line and a heading `Open questions` a person wrote
  *And* the ++board++ holds a card, a screen and a note a person added, a story a person wrote on a control's card, and Checkout where a person moved it
  *And* the drawing shows a screen and a control the mockup does not hold
*When* Claude Code renders the map onto each of them
*Then* ++bookshop/.context/ux-context.md++ keeps every line the person wrote, with the map's new invariant and note after its own
  *And* the ++board++ keeps the person's card in its region, the screen, the note, the story on the card, and Checkout where it was moved
  *And* the drawing still shows the screen and the control only it held
  *And* rendering the same map again changes none of the three

#### Scenario: Refuse to render a view that declares what JavaScript cannot hold without its type

Observed (`front_end_view_spec.py`, "that declares an enum", "whose constructor declares a member in its parameters").

*Given* a ++view++ written in TypeScript that declares `enum Step`
*When* Claude Code renders it to javascript
*Then* the render is refused, naming `enum Step`
  *And* no JavaScript is written without it

#### Scenario: Refuse to render between a view and a UX map

Observed (`ux_spec.py`, "a front-end view rendered to another format").

*Given* ++bookshop/src/CheckoutView.tsx++ holds the Checkout ++view++
*When* Claude Code renders ++bookshop/src/CheckoutView.tsx++ to drawio
*Then* the render is refused: a front-end view is rendered between typescript and javascript only
  *And* ++bookshop/src/CheckoutView.tsx++ is not read as a mockup page

#### Scenario: Take a mockup to a Claude Design canvas and back

Observed (`cdd_guidance/practices/ux/model/claude_design/claude_design_ux_map_spec.py`; the saving and the trip back through the Render action in `cdd_guidance/actions/render/render_spec.py`, "that is a mockup in html, rendered to claude_design", and through a real cdd server in `cdd_guidance/actions/render/render_saves_beside_source_heavy_spec.py`). Written after defect r3-gizmo-03: the render answered `{}`, saved nothing, and a canvas could not be read back. The person, 2026-11-23: a mockup render to claude_design works and renders back.

*Given* ++bookshop/buy-a-book.html++ holds the mockup
  *And* the canvas has no version yet
*When* Claude Code renders ++bookshop/buy-a-book.html++ to claude_design
*Then* the canvas's first version holds `design-canvas/version-1/project/canvas.json` and a prototype page for each screen, `screens/book-list.dc.html` and the rest
  *And* each prototype page is a mockup page that opens on its own screen, with its regions and controls, the transitions and what it serves
  *And* `canvas.json` places each page's board on a canvas page of its own, titled with its screen's name, in screen order
*When* Claude Code renders `design-canvas/version-1/project/canvas.json` to html
*Then* the render is ++bookshop/buy-a-book.html++ as it was

#### Scenario: Refuse to read a canvas that is missing a screen's prototype page

Observed (`claude_design_ux_map_spec.py`, "whose prototype page for a screen is missing").

*Given* `design-canvas/version-1/project/canvas.json` places the board of `screens/cart.dc.html`, and the canvas holds no such page
*When* Claude Code renders `design-canvas/version-1/project/canvas.json` to html
*Then* the render is refused, naming `screens/cart.dc.html`

#### Scenario: Leave a published canvas and a screen people ported as they are

Observed (`render_spec.py`, "whose canvas's latest version is published" and "whose canvas holds a screen people ported where a prototype page goes"). Source: `harness/design_canvas/.context/cdr/0001-recipe-called-canvas-api.md`, people edit a published canvas, so only the person starts the version after it.

*Given* the canvas's latest version is published, or holds at `screens/cart.dc.html` a screen the agent ported from the product
*When* Claude Code renders ++bookshop/buy-a-book.html++ to claude_design
*Then* the render is refused, naming the published version or the ported screen
  *And* no file of the canvas is written
