---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Epic: Align Formats In Files App

Map: [story-map.md](../../../.context/story-map.md#e-align-formats-in-files-app). Acceptance tests: `space/session/format_alignment_heavy_spec.py` for what the session answers on a real project, in process and through the cdd server; `space/session/format_alignment_spec.py` for the rules one object decides; `harness/files_app/app/files/format-alignment.spec.ts` for what only the page shows; `align-formats-in-files-app.story.ui_e2e_spec.py` beside this file for the page on its real server.

### Domain terms

- guidance selection: the stages and practices a session has selected and the formats chosen for each fidelity they cover (`space/session/guidance_selection.py` *GuidanceSelection*).
- chosen format: a format a person or an action chose for a fidelity in the session, such as the story map's markdown, drawio and whiteboard (`FidelitySessionOutput.chosen_formats`).
- document: one piece of a fidelity's work as the file each chosen format writes it to, such as `.context/story-map.md`, `.context/story-map.drawio` and `.context/story-map.whiteboard`, which the fidelity declares beside one another.
- graph reading: the nodes and edges the knowledge graph reads from one file, each node by its type and name, each edge by its kind and the two nodes it joins (`space/session/format_alignment.py` *GraphReading*). A format the graph does not read itself is first rendered into the fidelity's leading format.
- gap: one thing a diagnosis found, in plain words, with its kind, its file, and the file it is aligned from when a render closes it (*AlignmentGap*).
- diagnosis: every gap of a session, and the fidelities checked (*AlignmentDiagnosis*, `session.diagnose_alignment`).
- alignment: the renders that close the gaps a render can close, each file rendered, each failure met, and the diagnosis afterwards (*AlignmentResult*, `session.align_formats`).
- failure: a render the alignment could not make, answered as its kind, the file it was writing, and what the render said (*AlignmentFailure*).
- callout: what a link to a heading of another file opens in place under its line (`session.file` callouts).

## Story: Diagnose And Align Session Formats

Requested 2026-11-20, the person: "we need a diagnose and align button that goes on context viewer through graph and selected stages, fidelities, formats and determines gaps and then syncs, failures can be fixed; check graphs for alignment; check callouts match".

Decided in the code, since the request leaves it open (`space/session/format_alignment.py`): a missing file is rendered from the fidelity's leading format, its first chosen document format; a file that lacks what another holds is rendered from the one that holds more; two files that each hold something the other lacks are a person's decision, and while they conflict no file of that document is rendered.

##### Example: fill-cart

The session fill-cart works on Stories alone, with markdown, drawio and whiteboard chosen for its story map. Its story map `.context/story-map.md` holds the epic Fill Cart, the sub-epic Review Cart, and the stories Change Cart Line Quantity and Remove Cart Line.

#### Scenario: Report a chosen format whose file is missing

*Given* the session ++fill-cart++ has written its story map as markdown alone
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports `.context/story-map.drawio` as a missing file, aligned from `.context/story-map.md`
*And* the diagnosis reports `.context/story-map.whiteboard` as a missing file, aligned from `.context/story-map.md`

#### Scenario: Render the missing formats

*Given* the session ++fill-cart++ has written its story map as markdown alone
*When* the Person aligns the session's formats
*Then* the alignment renders `.context/story-map.drawio` and `.context/story-map.whiteboard` from `.context/story-map.md`
*And* the alignment says the whiteboard still goes on its board in Claude
*And* the diagnosis afterwards holds no gap

#### Scenario: Name the nodes and edges one format lacks

*Given* the session ++fill-cart++ has its story map written in every chosen format
*And* the card of the story Remove Cart Line was dropped from `.context/story-map.drawio`
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports that `.context/story-map.drawio` lacks Story 'Remove Cart Line' and the edge SubEpic 'Review Cart' decomposedInto Story 'Remove Cart Line', which `.context/story-map.md` holds
*And* the gap names `.context/story-map.md` as the file it is aligned from

#### Scenario: Align the format that lacks from the format that holds more

*Given* the session ++fill-cart++ has its story map written in every chosen format
*And* the card of the story Remove Cart Line was dropped from `.context/story-map.drawio`
*And* a person moved the card of the story Change Cart Line Quantity in the drawing
*When* the Person aligns the session's formats
*Then* `.context/story-map.drawio` draws Remove Cart Line again
*And* the card of Change Cart Line Quantity stays where the person put it
*And* the diagnosis afterwards holds no gap

#### Scenario: Leave formats that conflict to the person

*Given* the session ++fill-cart++ has its story map written in every chosen format
*And* the story Remove Cart Line was dropped from `.context/story-map.drawio` alone
*And* the story Change Cart Line Quantity was dropped from `.context/story-map.md` alone
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports the two files as a conflict, naming what each holds alone, with no file to align from
*And* the diagnosis leaves `.context/story-map.md`, which lacks what the whiteboard holds, to the person too
*When* the Person aligns the session's formats
*Then* every file of the story map is left as it is

#### Scenario: Answer a render that fails as a failure

*Given* the session ++fill-cart++ has its story map written in every chosen format
*And* `.context/story-map.md` was emptied and `.context/story-map.whiteboard` was deleted
*When* the Person aligns the session's formats
*Then* the alignment answers a failure of kind render_failed for `.context/story-map.whiteboard`, saying that `.context/story-map.md` is empty

#### Scenario: Render a chosen code format that has no file

Answered 2026-11-20, the person: "all renders should result in the final output -> file".

*Given* a session working on DDD alone has markdown and python chosen for its domain model
*And* `.context/domain-model.md` holds the bounded context Ordering with the aggregates Cart and Order, and no Python file is there
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports the Python as a missing file, aligned from `.context/domain-model.md`
*When* the Person aligns the session's formats
*Then* the alignment saves `ordering/cart/cart.py` and `ordering/order/order.py`, each holding its aggregate's classes
*And* the diagnosis afterwards holds no Python gap

#### Scenario: Reshape a code file that already has code

Answered 2026-11-21, the person: "render should match files to the new shape, but existing code, comments, whatever exists only in one shape must be preserved".

*Given* a session whose class model holds the class Cart with the operation total, rendered to Python, and a person wrote total's body in `src/ordering/ordering.py`
*And* the operation check_out is added to Cart in `src/ordering/.context/ordering-model.md`
*When* the class model is rendered to Python again
*Then* `src/ordering/ordering.py` holds total with the body the person wrote
*And* it holds check_out, empty
*And* the render lists nothing to migrate

#### Scenario: Keep a member the model no longer holds, for migration

*Given* a session whose class Cart has total with a body in `src/ordering/ordering.py`
*And* total is renamed to subtotal in the class model
*When* the class model is rendered to Python again
*Then* `src/ordering/ordering.py` still holds total and its body, in the class Cart, under a line saying it is no longer in the model
*And* it holds subtotal, empty
*And* the render lists Cart.total to migrate, with Cart.subtotal as what may have replaced it

#### Scenario: Fail a render that would lose a line

*Given* a format that writes onto the existing text itself, and answers a text without a line the file holds
*When* the render is saved
*Then* the render fails, naming the line it would lose
*And* the file is left as it was

#### Scenario: Report a drawing that cannot be read

*Given* the session ++fill-cart++ has its story map written in every chosen format
*And* `.context/story-map.drawio` no longer holds a whole drawing
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports `.context/story-map.drawio` as an unreadable format, with no file to align from

#### Scenario: Report a callout that opens nothing

*Given* the session ++fill-cart++ has its story map written in every chosen format
*And* `.context/story-map.md` links the heading `#cart-that-is-not-there` of `.context/domain-model.md`, which holds no such heading
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports the callout in `.context/story-map.md` whose target is missing

#### Scenario: Report callouts and edges that do not match

*Given* the session ++fill-cart++ has a story test `story_tests/fill-cart/review-cart/remove_cart_line_story.test.md` holding a scenario of the story Remove Cart Line, with no `Map:` line and no link from the story
*And* `.context/story-map.md` links the heading `#cart` of `.context/domain-model.md`, which no practice of the session reads
*When* the Person diagnoses the session's formats
*Then* the diagnosis reports the edge from the story to each scenario as an edge no callout shows
*And* the diagnosis reports the link to `#cart` as a callout no edge matches
*And* a story test whose `# Map:` line names its story's heading reports no gap, because the edge from the story to its scenarios matches the callout

#### Scenario: Diagnose and align from the Files app

*Given* the session ++fill-cart++ has written its story map as markdown alone, and the Person has the Files app open on it
*When* the Person presses Diagnose
*Then* the Files app lists the two missing files as gaps, each marked as one Align closes
*When* the Person presses Align
*Then* the Files app lists `.context/story-map.drawio` and `.context/story-map.whiteboard` as rendered from `.context/story-map.md`
*And* the Files app says no gap is left

#### Scenario: Send a gap a render does not close to be fixed

*Given* the Files app shows a gap that waits for a person, or a failure the alignment met
*When* the Person presses Fix on it
*Then* the failure band shows it in the session's own words with the file it is in, where its Fix sends it to the chat as [Send Failure To Be Fixed](../review-files-in-files-app/send_failure_to_be_fixed_story.test.md#story-send-failure-to-be-fixed) describes
