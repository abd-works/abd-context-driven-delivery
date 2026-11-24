---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Read Practice Trees From Source

Story map: [Read Practice Trees From Source](../../../../.context/story-map.md#e-read-practice-trees-from-source). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds for UX's graph reading today (`cdd_guidance/practices/ux/model/graph_reading.py`) and names the spec that runs it. They were written after round 3 of exploratory testing (defect r3-gizmo-06) showed that no UX file added a node to the knowledge graph, and the person answered that UX joins the graph.

### Domain terms

- ++UX map file++ — a file a UX map is written in: its drawing (a draw.io file the drawio-ux command line wrote, or one with a Site Map or Detailed IA page), a mockup's board (a `.whiteboard` file that draws a screen), `ux-map.json` or `ux.json`, a mockup page that carries its map, or `ux-context.md`.
- ++domain term++ — a name a screen lists as the domain thing it shows, such as Book.
- ++Story Demo control++ — a control that runs story steps in a mockup and shows the value of a bound field.
- ++served link++ — a story, scenario or step a screen or a control serves, written as a markdown link whose target is the file and heading it is written at, taken from the folder of the UX map file or from the project's folder.

> In steps: the bookshop's files are the examples below.

## Examples

### files of the bookshop project

| file | holds |
| --- | --- |
| ++bookshop/ux-map.json++ | the UX map Bookshop: the screens Book List, Home and Book Details; on Book List the region Books with the button Open book, whose interaction goes to Book Details, and the ++Story Demo control++ Titles, bound to `book.title`, which runs the step `the Customer opens the book list`; the transition Open book from Book List to Book Details; the content type Book Card; the nav component Main Nav |
| ++bookshop/.context/information-architecture.drawio++ | a drawing of the one screen Cart |
| ++bookshop/.context/ux-context.md++ | the scope and the note `Deferred epic: Review Books.` |
| ++bookshop/.context/story-map.drawio++ | a story map's drawing, which is no ++UX map file++ |
| ++bookshop/package.json++ | a JSON file that is no ++UX map file++ |
| ++bookshop/browse-books.whiteboard++ | a mockup's board: the screen Book List, its region Books, and the control Search, which serves the scenario List every book by a ++served link++ |
| ++.context/story-map.md++ | Sell Books, Browse Books, with the stories Browse Book List and View Book |
| ++story_tests/sell-books/browse-books/browse_books_story.test.md++ | Browse Book List's scenario List every book, with the step `the Customer opens the book list` |
| ++.context/domain-model.md++ | the aggregate Book with its root Book |
| ++src/book.py++ | the class Book with the property `title` |

### what each screen of ++bookshop/ux-map.json++ lists

| screen | stories | domain terms |
| --- | --- | --- |
| Book List | Browse Book List | Book |
| Home | View Book, Wish For Book | Shelf |
| Book Details | | |

### what the control Open book of ++bookshop/ux-map.json++ serves

| kind | ++served link++ | written at |
| --- | --- | --- |
| story | `[Browse Book List](../story_tests/sell-books/browse-books/browse_books_story.test.md#story-browse-book-list)` | the story's heading in its story file |
| scenario | `[Browse Book List › List every book](../story_tests/sell-books/browse-books/browse_books_story.test.md#scenario-list-every-book)` | the scenario's heading |
| scenario | `[Browse Book List › List every book](../story_tests/sell-books/none_story.test.md#scenario-list-every-book)` | a file that is not there |
| scenario | `[Browse Book List › List every book](../story_tests/sell-books/browse-books/browse_books_story.test.md#scenario-list-no-book)` | a heading the file does not have |
| step | `[Browse Book List › List every book › every book is listed](../story_tests/sell-books/browse-books/browse_books_story.test.md#scenario-list-every-book)` | the heading of the step's scenario |

## Story: Read UX Maps

### Evidence

| Source | Note |
|--------|------|
| The person's answer of 2026-11-20 (`closing-brief-round-3.md`, answer 2) | "UX joins the graph: its screens, regions, controls, interactions and transitions are nodes, with edges to the stories a screen shows and the domain terms it names" |
| `cdd_guidance/practices/ux/model/schema.yaml` | a screen `shows` stories, each of which records `shownOn`; `domainTerms` are the classes named on the screen; a transition goes `from` and `to` a screen; a Story Demo control has `storySteps` and a `boundField` |
| The person's second answers of 2026-11-20 (the third wave) | a mockup's whiteboard and drawing associate each screen and each control with the stories, scenarios and steps it serves, "joined in the graph by edges" |
| The person's answer 3 | "Nothing is joined on a name alone" where a file names its target another way; a class in several practices is several nodes |
| Defect r3-gizmo-06 | the graph held no UX node for a project with a UX map in every format, and validate reported that every UX graph rule passed |

#### Scenario: Read each UX map file into a map of its own

Observed (`cdd_guidance/practices/ux/model/graph_reading_spec.py`).

*Given* the bookshop project holds five ++UX map file++s
*When* the Knowledge Graph reads the bookshop project for UX
*Then* the graph holds a UX map for ++bookshop/ux-map.json++, one for ++bookshop/.context/information-architecture.drawio++, one for ++bookshop/.context/ux-context.md++, one for ++bookshop/browse-books.whiteboard++ and one for `bookshop/.context/browse-books.whiteboard`
  *And* it holds no UX node for ++bookshop/.context/story-map.drawio++ or ++bookshop/package.json++

#### Scenario: Hold a node for each part of a UX map

Observed (`graph_reading_spec.py`).

*Given* ++bookshop/ux-map.json++ holds the UX map Bookshop
*When* the Knowledge Graph reads the bookshop project for UX
*Then* the map holds the screens Book List, Home and Book Details
  *And* Book List holds the region Books, which holds the control Open book and the ++Story Demo control++ Titles
  *And* Open book holds the interaction open
  *And* the map holds the transition Open book, the content type Book Card, the nav component Main Nav and its context
  *And* each screen is placed at the line of ++bookshop/ux-map.json++ that names it

#### Scenario: Join a transition and an interaction to the screens they go to

Observed (`graph_reading_spec.py`).

*Given* the transition Open book goes from Book List to Book Details
*When* the Knowledge Graph reads the bookshop project for UX
*Then* the transition Open book has a `from` edge to Book List and a `to` edge to Book Details
  *And* the interaction open has a `destination` edge to Book Details

#### Scenario: Join a screen to the stories it shows

Observed (`graph_reading_spec.py`).

*Given* ++.context/story-map.md++ holds the stories Browse Book List and View Book
*When* the Knowledge Graph reads the bookshop project for UX and Stories
*Then* Book List has a `shows` edge to the story Browse Book List
  *And* the story View Book has a `shownOn` edge to Home
  *And* Home has no edge for Wish For Book, which the story map does not hold

#### Scenario: Join a control to the story, scenario and step it serves

Observed (`graph_reading_spec.py`, "from a project whose story map and domain model the graph reads too").

*Given* the control Open book serves what the table above lists
*When* the Knowledge Graph reads the bookshop project for UX and Stories
*Then* Open book has a `shows` edge to the story Browse Book List
  *And* it has a `showsScenarios` edge to the scenario List every book
  *And* it has a `showsSteps` edge to the Then step `every book is listed` of that scenario
  *And* the scenario List every book has a `shownOn` edge to Open book

#### Scenario: Join nothing to a served link whose target names no story file or heading

Observed (`graph_reading_spec.py`, the same context).

*Given* Open book has a ++served link++ named for the scenario List every book whose target is a file that is not there
  *And* another whose target is a heading the story file does not have
*When* the Knowledge Graph reads the bookshop project for UX and Stories
*Then* Open book has one `showsScenarios` edge, to the scenario at the heading its first link names
  *And* neither of the other two links is joined to the scenario of the same name

#### Scenario: Follow a served link written from the project's folder, or to a file with no heading

Observed (`graph_reading_spec.py`, the same context).

*Given* the screen Book Details serves the story Browse Book List by a ++served link++ whose target is written from the project's folder
  *And* it serves the scenario List every book by a link to the story file with no heading
*When* the Knowledge Graph reads the bookshop project for UX and Stories
*Then* Book Details has a `shows` edge to the story Browse Book List
  *And* it has a `showsScenarios` edge to the scenario of that file whose key is `Browse Book List › List every book`

#### Scenario: Join a control drawn on a mockup's board to the scenario it serves

Observed (`graph_reading_spec.py`, the same context).

*Given* ++bookshop/browse-books.whiteboard++ draws the control Search, which serves the scenario List every book
*When* the Knowledge Graph reads the bookshop project for UX and Stories
*Then* the graph holds the screen Book List, the region Books and the control Search for ++bookshop/browse-books.whiteboard++
  *And* Search has a `showsScenarios` edge to the scenario List every book

#### Scenario: Follow a served link in a board saved in the epic's .context

Observed (`graph_reading_spec.py`, the same context).

*Given* `bookshop/.context/browse-books.whiteboard` holds the same board, its ++served link++ still written from the folder `bookshop`, where the mockup it was drawn from sits
*When* the Knowledge Graph reads the bookshop project for UX and Stories
*Then* the control Search of that board has a `showsScenarios` edge to the scenario List every book

#### Scenario: Keep what a control serves when the scenarios are not read

Observed (`graph_reading_spec.py`, "from a project that holds the map as JSON, its drawing, and its UX context").

*Given* the control Open book serves what the table above lists
*When* the Knowledge Graph reads the bookshop project for UX alone
*Then* Open book keeps each ++served link++ as its file writes it
  *And* Open book has no `shows`, `showsScenarios` or `showsSteps` edge
  *And* the read reports no failure

#### Scenario: Join a screen to the domain class a domain term names

Observed (`graph_reading_spec.py`).

*Given* ++.context/domain-model.md++ holds the aggregate Book with its root Book
*When* the Knowledge Graph reads the bookshop project for UX, DDD and Clean Engineering
*Then* Book List has a `domainTerms` edge to the DDD class Book, the aggregate's root
  *And* Home has no `domainTerms` edge, since no class is named Shelf

#### Scenario: Join a Story Demo control to the step it runs and the property it shows

Observed (`graph_reading_spec.py`).

*Given* the ++Story Demo control++ Titles runs `the Customer opens the book list` and is bound to `book.title`
*When* the Knowledge Graph reads the bookshop project for UX, Stories and Clean Engineering
*Then* Titles has a `storySteps` edge to the When step `the Customer opens the book list` of Browse Book List, a story its screen shows
  *And* Titles has a `boundField` edge to the property `title` of the class Book
  *And* Titles has no edge for a step no story holds

#### Scenario: Run the screen rules on the screens read

Observed (`graph_reading_spec.py`).

*Given* ++bookshop/ux-map.json++ holds a screen named Home
*When* the Knowledge Graph reads the bookshop project for UX and runs its rules
*Then* the screen Home carries a screen-names-use-domain-terms violation

#### Scenario: Read a UX map file again after it changes

Observed (`graph_reading_spec.py`).

*Given* the Knowledge Graph has read the bookshop project for UX and Stories
  *And* a person adds the screen Cart, which shows View Book, to ++bookshop/ux-map.json++
*When* the Knowledge Graph refreshes ++bookshop/ux-map.json++
*Then* the map holds Book List, Home, Book Details and Cart, each once
  *And* Cart has a `shows` edge to the story View Book
