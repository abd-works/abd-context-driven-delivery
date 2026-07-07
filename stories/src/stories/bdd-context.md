## Story Model

a Story Map
  it should hold no Epics
  it should hold no Increments

  with 4 Epics in sequential order
    it should hold 4 Epics
    it should list the Epics in sequential order

    with a fifth Epic appended
      it should hold 5 Epics
      the last Epic in sequential order
        it should be the appended Epic

    with the first Epic removed
      it should hold 3 Epics
      it should discard the SubEpics that lived under the removed Epic
      it should renumber the remaining Epics

    with the first Epic renamed
      it should preserve the sequential order of the Epics
      the first Epic
        it should carry the new name

    with the Epics reordered
      it should list the Epics in the new order
      it should reflect each Epic's new position in its sequential order

    with the first Epic holding 3 SubEpics
      the first Epic
        it should hold 3 SubEpics

      with a SubEpic appended to the first Epic
        the first Epic
          it should hold 4 SubEpics

      with the first SubEpic of the first Epic removed
        the first Epic
          it should hold 2 SubEpics
          it should discard the Stories that lived under the removed SubEpic

      with the first SubEpic of the first Epic renamed
        the first SubEpic of the first Epic
          it should carry the new name

      with a nested SubEpic added under the first SubEpic
        the first SubEpic of the first Epic
          it should hold 1 nested SubEpic
          it should report hasSubEpics as true

      with the first SubEpic moved from the first Epic to the second Epic
        the first Epic
          it should hold 2 SubEpics
        the second Epic
          it should hold one additional SubEpic
        the moved SubEpic
          it should keep its Stories and their Scenarios

      with the first SubEpic of the first Epic holding 2 Stories
        the first SubEpic of the first Epic
          it should hold 2 Stories

        with a Story appended to the first SubEpic
          the first SubEpic of the first Epic
            it should hold 3 Stories

        with the first Story of the first SubEpic removed
          the first SubEpic of the first Epic
            it should hold 1 Story
            it should discard the Scenarios that lived under the removed Story

        with the first Story of the first SubEpic renamed
          the first Story of the first SubEpic
            it should carry the new name

        with the first Story typed as system
          the first Story of the first SubEpic
            it should carry the StoryType system

        with the first Story moved from the first SubEpic to the second SubEpic
          the first SubEpic of the first Epic
            it should hold 1 Story
          the second SubEpic of the first Epic
            it should hold one additional Story
          the moved Story
            it should keep its Scenarios

        with the first Story of the first SubEpic holding 3 Scenarios
          the first Story of the first SubEpic
            it should hold 3 Scenarios

          with a Scenario appended to the first Story
            the first Story of the first SubEpic
              it should hold 4 Scenarios
            the last Scenario in sequential order
              it should be the appended Scenario

          with the first Scenario of the first Story removed
            the first Story of the first SubEpic
              it should hold 2 Scenarios
              it should renumber the remaining Scenarios

          with the first Scenario of the first Story renamed
            the first Scenario of the first Story
              it should carry the new name

          with the given clauses of the first Scenario updated
            the first Scenario of the first Story
              it should carry the new given clauses
              it should preserve its name and sequentialOrder

          with the interactions of the first Scenario replaced
            the first Scenario of the first Story
              its when and then clauses
                it should reflect the new interactions

          with the Scenarios of the first Story reordered
            the first Story of the first SubEpic
              it should list the Scenarios in the new order

  with 2 Increments in sequential order
    it should hold 2 Increments
    it should list the Increments in sequential order

    with an Increment appended
      it should hold 3 Increments
      the last Increment in sequential order
        it should be the appended Increment

    with the first Increment removed
      it should hold 1 Increment
      it should renumber the remaining Increment

    with the first Increment renamed
      the first Increment
        it should carry the new name

    with the outcome of the first Increment updated
      the first Increment
        it should carry the new outcome
        it should preserve its name and sequentialOrder

    with a story name added to the first Increment
      the first Increment
        it should hold one additional story name
        its story-name list
          it should remain a list of name strings, not Story object references

    with the Increments reordered
      it should list the Increments in the new order

## Scenario

<!-- Scenario is a StoryNode leaf: `childCollections` returns []; clauses and interactions are copied through updateSelf, not reconciled as tree children. -->

a Scenario
  it should report itself as a leaf StoryNode
  it should return an empty list from childCollections

  that has been translated from another Scenario of the same semantic type
    it should carry every field from the source (name, sequentialOrder, storyName, given, interactions, isOutline, exampleRows, background, evidence)
    its interactions
      it should be a value copy — mutating the source's interactions after translation should not affect the target

  that carries multiple interactions
    it should expose whenClauses as the flat when-clause list across all interactions in order
    it should expose thenClauses as the flat then-clause list across all interactions in order
    it should expose allClauses as given + each interaction's when + then in order

  whose given clauses include an "And " continuation
    the continuation clause
      it should carry isContinuation true
      it should preserve the "And " prefix verbatim in text

  whose interaction contains a "But " continuation in its then clauses
    the continuation clause
      it should carry isContinuation true
      it should preserve the "But " prefix verbatim in text

## Increment

<!-- Increment is a StoryNode leaf: `childCollections` returns []; stories list, outcome, and prompt are copied through updateSelf. -->

an Increment
  it should report itself as a leaf StoryNode
  it should return an empty list from childCollections

  that has been translated from another Increment of the same semantic type
    it should carry every field from the source (name, sequentialOrder, outcome, slicingNotes, stories, decisionPrompt)
    its stories list
      it should be a value copy of story-name strings, not object references to Story nodes

  that references a story name not present in any Story on the StoryMap
    the model
      it should not raise
    a scanner walking the StoryMap
      it should be able to detect the orphan reference by comparing name lists

## Test Suite

<!-- TestSuite / TestCase / Test are populated by scanners at load time and NEVER translated across formats. They carry a Tier and a Language tag. -->

a SubEpic
  it should hold an empty testSuites list before loading
  it should report empty testSuites as no test coverage for any tier

  that has been loaded from a workspace with domain and server tier test files
    it should hold 2 TestSuites — one per discovered tier
    every TestSuite
      it should carry a Tier discovered from its file-name segment
      it should carry a Language discovered from its file extension
      it should carry a source SourceLocation pointing at the backing test file

  that has been loaded from a workspace where a tier test file has no matching `*-stories.<ext>` sibling in the same language
    the loader
      it should raise a loader error naming the missing stories file

  that has been translated from another SubEpic of the same semantic type
    its testSuites
      it should be a value copy — TestSuite objects are ValueObjects and are copied through updateSelf; they never reconcile as tree children

a Story
  it should hold an empty testCases list before loading
  it should report an empty testCases list as no test coverage across any tier

  that has been loaded from a workspace whose tier test files contain matching TestCases
    it should hold one TestCase per tier where a matching case exists
    every TestCase
      it should carry the Tier inherited from its containing TestSuite
      it should carry a storySource SourceLocation pointing at the Story constant in the sibling `*-stories.<ext>` file (same language as its TestSuite)
      every Test inside it
        it should carry a scenarioSource SourceLocation pointing at the Scenario key in the same sibling stories file

a workspace where two languages contribute test suites to the same SubEpic
  it should hold TestSuites in each Language for that SubEpic
  every TestSuite
    it should reference a stories-file sibling in its own Language (the Python suite reads `_stories.py`; the TypeScript suite reads `-stories.ts`)

## StoryNode Reconciliation

a StoryNode

  that has been translated from a source of the same semantic type with no differences
    the UpdateReport
      it should record no adds, removes, renames, or reorders
      it should hold a NodeSnapshot of the target captured before translation
    the target
      it should be unchanged in every field

  that has been asked to translate from a source of a different semantic type
    it should reject the translation

  that has been translated from a source with an added child
    the target
      it should hold the new child
      the new child on the target
        it should be of the correct semantic type for its position
        it should carry every field from the source child
    the UpdateReport
      it should record the new child

  that has been translated from a source with a removed child
    the target
      it should no longer hold the removed child
    the UpdateReport
      it should record the removed child

  that has been translated from a source with a renamed child
    the target child
      it should carry the new name
    the UpdateReport
      it should record the rename with a confidence score

  that has been translated from a source with reordered children
    the target
      it should list the children in the source's order
    the UpdateReport
      it should record the reorder

  that has been translated from a source with a child moved to a different parent
    the old parent on the target
      it should no longer hold the child
    the new parent on the target
      it should hold the child
    the UpdateReport
      it should record one removed child under the old parent and one added child under the new parent

  that has been translated from a source whose children include a mix of matches, renames, and additions
    the target children matched to a source child by name and sequential order
      it should keep its identity through reconciliation
      it should carry every field from the matched source child
    the target children that correspond to unmatched source children
      it should appear as fresh instances of the correct semantic type for their position
    every child collection on the target
      it should be fully reconciled against the corresponding source collection

  that has been reversed against the UpdateReport it produced
    it should be restored to the name and sequential order captured in the NodeSnapshot
    every descendant
      it should be restored to its captured state by position

  that has been asked to reverse against a report produced by a different node
    it should reject the reverse

a StoryMap being translated from another StoryMap
  it should reconcile epics as tree children
  it should reconcile increments as tree children in the same pass
  the UpdateReport
    it should record epic-level and increment-level changes independently

## Documents

a Markdown document
  it should contain no headings

  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 top-level headings
    it should contain 3 second-level headings under the first top-level heading
    it should list every Story as a bullet under its SubEpic
    it should preserve the sequential order of every node

    with a fifth Epic appended in the source Story Map and re-rendered
      it should contain 5 top-level headings
      the first 4 headings
        it should be unchanged

    with the first Epic removed in the source Story Map and re-rendered
      it should contain 3 top-level headings
      the headings for the removed Epic and its descendants
        it should be absent

    with the first Epic renamed in the source Story Map and re-rendered
      the first heading
        it should carry the new name
      the headings under it
        it should be unchanged

  that holds a rendered Story Map with inline scenarios
    every Story with at least one Scenario
      it should carry a Scenario subsection under its Story heading, one per Scenario in sequential order
      every Scenario subsection
        it should hold a scenario-name heading
        it should hold a **Given** bulleted list carrying the Scenario's given clauses verbatim
        it should hold a **When** bulleted list carrying each interaction's when clauses verbatim
        it should hold a **Then** bulleted list carrying each interaction's then clauses verbatim

    with the given clauses of the first Scenario updated and the document re-rendered
      the **Given** bullets of the first Scenario
        it should carry the updated clauses

    with a Scenario removed from the first Story and the document re-rendered
      the first Story's Scenario subsections
        it should no longer contain the removed Scenario's subsection

  that is being read back into a MarkdownStoryMap
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story, and Scenario in sequential order

  that has been edited and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document

  that is not a valid Markdown story map
    the read
      it should be rejected

a Markdown thin-slicing document
<!-- thin-slicing.md carries Increments. Reconciled into StoryMap.increments via the separate increment load path. -->

  that is absent from the workspace
    the loader
      it should treat StoryMap.increments as empty
      it should not raise

  that holds a rendered increment list of 2 Increments
    it should contain one section per Increment in sequential order
    every Increment section
      it should carry its name as the section heading
      it should list its stories as an ordered list of name strings
      it should carry its outcome and decisionPrompt when non-empty

    with a third Increment appended and the document re-rendered
      it should contain 3 Increment sections

    with the first Increment removed and the document re-rendered
      it should contain the remaining Increment sections in renumbered order

  that has been edited and synced back against a canonical Story Map's increments
    the reconstructed StoryMap.increments
      it should reflect every edit
    the returned UpdateReport
      it should list every add, remove, rename, and reorder applied to the increment collection

a story-graph.json document
  it should contain no Epics and no increments

  that holds a serialized Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic entries under `epics[]`
    the first Epic entry
      it should contain 3 SubEpic entries
    every Story
      it should be nested under its SubEpic entry
    every Scenario
      it should be nested under its Story entry, carrying its name, given, and interactions[] fields
    every Story entry
      it should preserve its StoryType field
    it should preserve the sequential order of every node

    with a fifth Epic appended and the document re-serialized
      it should contain 5 Epic entries

    with the first Epic removed and the document re-serialized
      it should contain 3 Epic entries
      it should hold no orphan SubEpic entries

    with a Scenario appended to the first Story and the document re-serialized
      the first Story entry
        it should contain one additional Scenario entry at the end

  that holds a serialized Story Map with 2 Increments
    it should contain 2 Increment entries under `increments[]`
    every Increment entry
      it should carry its name, outcome, slicingNotes, stories[], and decisionPrompt fields

    with an Increment appended and the document re-serialized
      it should contain 3 Increment entries under `increments[]`

  that is being read back into a JsonStoryMap
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story, Scenario, and Increment in sequential order

  that has been edited and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document

  that does not conform to the story-graph.json schema
    the read
      it should be rejected

## Diagrams
<!-- The subject is a Story Map made of DiagramStoryNodes. Every operation on this Story Map is observed for BOTH the domain change (child added, node renamed, ...) AND the layout consequence (positioning, sizing, row shifts). They are never separated. -->
<!-- DrawIO Story Map and Miro Story Map inherit every behavior below and add only backend-specific serialization + roundtrip observations. -->
<!-- Each concrete diagram document is ONE view: story-map, scenario, or thin-slice. Each view supports the full parse / render / sync surface. A view is authoritative for its own slice of the model and reconciles only that slice on sync. -->

### Story-map view

a diagram Story Map in the story-map view
  it should hold no Epics

  with 4 Epics in sequential order
    it should hold 4 Epics
    every Epic
      it should sit on the Epic row
      it should sit at the X of its sequential position on the Epic row
      it should span its own base width when it holds no SubEpics
    the SubEpic row for depth 0
      it should sit directly below the Epic row
    the actor row
      it should sit directly below the deepest SubEpic row
    the Story row
      it should sit directly below the actor row

    with a fifth Epic appended
      it should hold 5 Epics
      the last Epic in sequential order
        it should be the appended Epic
        it should sit at the rightmost X on the Epic row
      the first four Epics
        it should keep their previous X positions

    with the first Epic removed
      it should hold 3 Epics
      it should discard the SubEpics that lived under the removed Epic
      the remaining Epics
        it should renumber to 1, 2, 3
        it should shift left to close the gap left by the removed Epic

    with the first Epic renamed
      the first Epic
        it should carry the new name
        it should stay at its previous X on the Epic row
      it should preserve the sequential order of the Epics

    with the Epics reordered
      it should list the Epics in the new order
      every Epic
        it should sit at the X of its new sequential position on the Epic row

    with the first Epic holding 3 SubEpics
      the first Epic
        it should hold 3 SubEpics
        it should widen to span the combined width of its 3 SubEpics
      every SubEpic of the first Epic
        it should sit on the SubEpic row for depth 0
        it should sit at the X of its sequential position within the first Epic's span
      every Epic to the right of the first Epic
        it should shift right to accommodate the first Epic's new width

      with a SubEpic appended to the first Epic
        the first Epic
          it should hold 4 SubEpics
          it should widen to span 4 SubEpics
        the appended SubEpic
          it should sit at the rightmost X within the first Epic's span
        every Epic to the right of the first Epic
          it should shift right by the width of one SubEpic

      with the first SubEpic of the first Epic removed
        the first Epic
          it should hold 2 SubEpics
          it should narrow to span 2 SubEpics
          it should discard the Stories that lived under the removed SubEpic
        every Epic to the right of the first Epic
          it should shift left by the width of one SubEpic

      with the first SubEpic of the first Epic renamed
        the first SubEpic of the first Epic
          it should carry the new name
          it should stay at its previous X on the SubEpic row for depth 0

      with a nested SubEpic added under the first SubEpic
        the first SubEpic of the first Epic
          it should hold 1 nested SubEpic
          it should widen to span its nested SubEpic
        the nested SubEpic
          it should sit on the SubEpic row for depth 1
        the SubEpic row for depth 1
          it should sit directly below the depth 0 row
        the actor row
          it should shift down to sit below the depth 1 row
        the Story row
          it should shift down to sit below the actor row

      with the first SubEpic moved from the first Epic to the second Epic
        the first Epic
          it should hold 2 SubEpics
          it should narrow to span 2 SubEpics
        the second Epic
          it should hold one additional SubEpic
          it should widen to accommodate the additional SubEpic
        the moved SubEpic
          it should sit within the second Epic's span
          it should keep its Stories and their Scenarios at the new X

      with the first SubEpic of the first Epic holding 2 Stories
        every Story
          it should sit on the Story row
          it should sit at the X of its parent SubEpic

        with a Story appended to the first SubEpic
          the first SubEpic of the first Epic
            it should hold 3 Stories
          the appended Story
            it should sit on the Story row at the parent SubEpic's X

        with the first Story of the first SubEpic renamed
          the first Story of the first SubEpic
            it should carry the new name
            it should stay at its previous X on the Story row

        with the first Story typed as system
          the first Story of the first SubEpic
            it should carry the style for StoryType system

        with the first Story moved from the first SubEpic to the second SubEpic
          the moved Story
            it should sit at the second SubEpic's X on the Story row
            it should keep its Scenarios

  that has been asked to place a SubEpic as a parent of an Epic
    it should reject the placement

  that has been asked to place a Story as a parent of a SubEpic
    it should reject the placement

  that has been asked to give an Epic any parent
    it should reject the parent

### Scenario view

a diagram Story Map in the scenario view
<!-- Renders Story cells with a scenario divider cell and Given/When/Then clause cells stacked beneath each Scenario. Authoritative on sync for Story.scenarios only — leaves epics/subepics/increments untouched. -->

  that holds a Story with 2 Scenarios
    the Story cell
      it should sit on the Story row
    every Scenario of the Story
      it should render a divider cell labelled with the scenario name below its Story
      it should render its given clauses as cells stacked directly below the divider
      it should render each interaction as when-cells followed by then-cells beneath the given cells
    the divider between the first and second Scenario
      it should be visually distinct from the story / clause styles
      it should make the boundary between the two Scenarios obvious

    with a Scenario appended to the Story
      the Story
        it should hold 3 Scenarios
      the appended Scenario
        it should render a divider cell and its clause cells below the previous Scenario's clause block

    with the first Scenario of the Story removed
      the diagram
        it should no longer contain the removed Scenario's divider or its clause cells
      the second Scenario
        it should shift up to close the gap

    with the given clauses of the first Scenario updated
      the given cells beneath the first Scenario's divider
        it should reflect the new given clauses in order

    with the interactions of the first Scenario replaced
      the when and then cells beneath the first Scenario's divider
        it should reflect the new interactions

  that is synced back after a Scenario is added in the diagram
    the reconstructed Story
      it should hold the new Scenario with its parsed given / interactions
    the underlying StoryMap.epics and StoryMap.increments
      it should be untouched (view-scoped sync — the scenario view does not own the epic tree or the increment list)

  that is synced back after a Scenario name is changed in the diagram
    the returned UpdateReport
      it should record the rename on Story.scenarios only

### Thin-slice view

a diagram Story Map in the thin-slice view
<!-- Renders Increments as header cells with story-name cells stacked below each. Authoritative on sync for StoryMap.increments only. -->

  that holds 2 Increments
    every Increment
      it should render a header cell in the `increment` style
      it should render one story-name cell per entry in stories, stacked directly below the header
    the second Increment's header
      it should sit directly below the first Increment's last story-name cell

    with an Increment appended
      the diagram
        it should hold 3 Increment blocks stacked vertically

    with the first Increment removed
      the diagram
        it should no longer contain the removed Increment's header or its story-name cells
      the second Increment
        it should shift up to close the gap

    with a story name added to the first Increment
      the first Increment's story-name column
        it should hold one additional story-name cell at the bottom

  that is synced back after a story name is renamed inside an Increment
    the reconstructed Increment.stories list
      it should carry the renamed value
    the underlying StoryMap.epics and any Story.scenarios
      it should be untouched (view-scoped sync — the thin-slice view does not own the epic tree or story scenarios)

### View isolation

a workspace holding all three diagram views (story-map, scenario, thin-slice)
  syncing the story-map view
    it should reconcile StoryMap.epics only
    it should leave Story.scenarios untouched
    it should leave StoryMap.increments untouched

  syncing the scenario view
    it should reconcile Story.scenarios only
    it should leave StoryMap.epics untouched
    it should leave StoryMap.increments untouched

  syncing the thin-slice view
    it should reconcile StoryMap.increments only
    it should leave StoryMap.epics untouched
    it should leave Story.scenarios untouched

### DrawIO backend

a DrawIO Story Map
<!-- Every "a diagram Story Map" behavior in the corresponding view applies. The observations here only verify that operations on the Story Map surface externally in the DrawIO document — new shapes appear, renamed shapes carry the new label, deleted shapes are gone. Positioning is already proven above; do not repeat it. -->

  that holds a rendered story-map view with 4 Epics and 3 SubEpics under the first Epic
    it should serialize as a valid DrawIO document named `story-map.drawio`
    every node
      it should appear as an mxCell in the document

    with an Epic appended and the DrawIO document re-rendered
      the document
        it should contain one additional Epic shape carrying the new Epic's name

    with the first Epic renamed and the DrawIO document re-rendered
      the shape for the first Epic
        it should carry the new name as its label

    with a SubEpic deleted and the DrawIO document re-rendered
      the document
        it should no longer contain the shape for the deleted SubEpic or any of its descendants

  that holds a rendered scenario view
    it should serialize as a valid DrawIO document named `scenarios.drawio`
    every Scenario
      it should appear as a divider mxCell and one clause mxCell per Given / When / Then step

  that holds a rendered thin-slice view
    it should serialize as a valid DrawIO document named `thin-slicing.drawio`
    every Increment
      it should appear as a header mxCell and one story-name mxCell per entry in stories

  that has been edited in the DrawIO document and synced back
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
    the reconstructed diagram Story Map for the corresponding view
      it should reflect every edit made to the document

  that is not a valid DrawIO document being synced
    the sync
      it should be rejected

### Miro backend

a Miro Story Map
<!-- Every "a diagram Story Map" behavior in the corresponding view applies. The observations here only verify that operations on the Story Map surface externally on the Miro board. Positioning is already proven above; do not repeat it. -->

  that holds a rendered story-map view with 4 Epics and 3 SubEpics under the first Epic
    it should post as a valid set of Miro items via the Miro API
    every node
      it should appear as an item on the board

    with an Epic appended and the Miro board re-rendered
      the board
        it should contain one additional Epic item carrying the new Epic's name

    with the first Epic renamed and the Miro board re-rendered
      the item for the first Epic
        it should carry the new name as its label

    with a SubEpic deleted and the Miro board re-rendered
      the board
        it should no longer contain the item for the deleted SubEpic or any of its descendants

  that holds a rendered scenario view
    every Scenario
      it should appear as a divider item and one clause item per Given / When / Then step

  that holds a rendered thin-slice view
    every Increment
      it should appear as a header item and one story-name item per entry in stories

  that has been edited on the Miro board and synced back
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the board
    the reconstructed diagram Story Map for the corresponding view
      it should reflect every edit made to the board

  that does not respond as a valid Miro story map when synced
    the sync
      it should be rejected

## Code
<!-- The subject is a Story Map that renders to a source-code tree. -->
<!-- Every language backend (TypeScript, Python, Java, JavaScript) renders the SAME domain tree: `StoryMap → Epic → SubEpic → Story → Scenario`. -->
<!-- Folder structure and the "one leaf file per lowest-level SubEpic" rule are identical across languages. Only the leaf-file syntax differs — Story constants and Scenario definitions are emitted in each language's native form (TypeScript `as const satisfies`, Python `TypedDict` / dataclass, Java static record, JavaScript object literal). -->
<!-- Every operation on `a code Story Map` is observed for BOTH the domain change AND the file-tree consequence. Backend subjects add ONLY the backend-specific leaf-file shape. -->
<!-- Increment has no code implementation — the code format delegates increments to Markdown's `thin-slicing.md`. -->
<!-- Test suites, test cases, and tests are NOT part of the code format's translation tree. They are language-native implementation code populated by scanners (see § Test Suite). -->

a code Story Map
  it should hold no Epics
  it should produce no folders under the tests root

  with 4 Epics in sequential order
    it should hold 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root
      the folders for the first four Epics
        it should be byte-identical to before

    with the first Epic removed
      the folder for the removed Epic and everything under it
        it should be gone
      the folders for the remaining Epics
        it should be byte-identical to before

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug
        its contents
          it should be byte-identical to before

    with the first Epic holding 3 leaf SubEpics
      the folder for the first Epic
        it should contain 3 sub-folders (one per leaf SubEpic)
      every leaf SubEpic of the first Epic
        it should produce a sub-folder under the first Epic's folder, named after the SubEpic slug
        it should produce exactly one leaf file inside its own sub-folder, named after the SubEpic slug and carrying the language-specific extension

      with a leaf SubEpic appended to the first Epic
        the folder for the first Epic
          it should contain 4 sub-folders
        the appended SubEpic
          it should produce a new sub-folder holding a new leaf file
        the leaf files for the first three SubEpics
          it should be byte-identical to before

      with the first SubEpic of the first Epic renamed
        the sub-folder for the first SubEpic
          it should carry the new slug
        the leaf file inside it
          it should carry the new slug in its filename
          its Story constants and Scenario definitions
            it should be unchanged

      with a nested SubEpic added under the first (previously leaf) SubEpic
        the sub-folder for the first SubEpic
          it should hold a further sub-folder for the nested SubEpic
          the nested sub-folder
            it should hold a leaf file for the nested SubEpic
        the leaf file that previously sat at the first SubEpic level
          it should be gone, because the first SubEpic is no longer a leaf

      with the first SubEpic moved from the first Epic to the second Epic
        the folder for the first Epic
          it should no longer contain the sub-folder for the moved SubEpic
        the folder for the second Epic
          it should contain the sub-folder for the moved SubEpic
        the moved leaf file
          its Story constants and their Scenario definitions
            it should be unchanged

      with the first SubEpic of the first Epic holding 2 Stories
        the leaf file for the first SubEpic
          it should contain 2 Story constants
        every Story
          it should produce one Story constant inside its SubEpic's leaf file, named after the Story

        with a Story appended to the first SubEpic
          the leaf file for the first SubEpic
            it should contain 3 Story constants
          the appended Story
            it should produce a new Story constant

        with the first Story of the first SubEpic renamed
          the Story constant for the first Story
            it should carry the new Story name

        with the first Story moved from the first SubEpic to the second SubEpic
          the leaf file for the first SubEpic
            it should no longer contain the Story constant for the moved Story
          the leaf file for the second SubEpic
            it should contain the Story constant for the moved Story

        with the first Story of the first SubEpic holding 3 Scenarios
          the Story constant for the first Story
            it should expose 3 Scenario definitions (one per Scenario) in the Scenarios' declared order
          every Scenario
            it should produce one Scenario definition inside its Story constant, holding the Scenario's name, given clauses, and interactions

          with a Scenario appended to the first Story
            the Story constant for the first Story
              it should expose 4 Scenario definitions
            the appended Scenario
              it should produce a new Scenario definition at the end

          with the first Scenario of the first Story removed
            the Story constant for the first Story
              it should expose 2 Scenario definitions
              it should no longer expose the removed Scenario

          with the given clauses of the first Scenario updated
            the Scenario definition for the first Scenario
              it should carry the updated given clauses

          with the interactions of the first Scenario replaced
            the Scenario definition for the first Scenario
              it should carry the new when and then clauses in its interactions

          with the Scenarios of the first Story reordered
            the Story constant for the first Story
              it should expose its Scenario definitions in the new order

  that holds hand-written regions in a leaf file outside the generated Story constants and Scenario definitions
    with the leaf file regenerated
      the leaf file
        it should preserve every hand-written region byte-for-byte
      the generated Story constants and Scenario definitions
        it should be the only regions rewritten

  that is asked to render Increments
    it should delegate to the Markdown thin-slicing document — no code leaf file should carry Increment definitions
    the workspace's `thin-slicing.md`
      it should receive the Increment renderings

  that is asked to render Increments when `thin-slicing.md` is absent from the workspace
    the render
      it should not raise
    the reconstructed StoryMap.increments
      it should be empty

  that has been asked to render into a folder that is not a valid code Story Map tree
    the render
      it should be rejected

### TypeScript backend

a TypeScript story-spec Story Map
<!-- A concrete backend of "a code Story Map". Every "a code Story Map" behavior applies. Only observe the TypeScript declarations that make a Story constant or a Scenario definition. -->
<!-- The shape matches the eval `story-types.ts` + `route-transfer-before-cutoff-stories.ts`: keyed Scenario properties on the Story constant. NO acceptance_criteria array. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<sub-epic-slug>-stories.ts`
      it should import `Interaction`, `Scenario`, and `Story` types from the shared `story-types.ts` module using a relative path matching its folder depth
      it should parse as valid TypeScript and typecheck against the story-types module

    every Story constant
      it should be an exported const named after the Story in PascalCase, closed with `as const satisfies Story`
      it should carry a `story` field holding the Story name as a template-string literal
      it should carry an `actor` field holding the Story's actor as a template-string literal
      it should carry `domainTerms` and `evidence` fields, empty arrays when the Story declares none
      it should expose one keyed Scenario property per Scenario, keyed by a camelCased slug derived from the Scenario's name
      it should NOT carry an `acceptance_criteria` array — that field is legacy and does not appear in the current schema

    every Scenario property inside a Story constant
      it should hold a `name` field carrying the human-readable Scenario name
      it should hold a `given` field carrying a readonly array of clause strings
      it should hold an `interactions` field carrying a readonly array of `{ when: readonly string[], then: readonly string[] }` records, one per Interaction in declared order

    with the given clauses of the first Scenario updated
      the Scenario property for the first Scenario
        its `given` field
          it should carry the updated clause strings verbatim

    with the interactions of the first Scenario replaced
      the Scenario property for the first Scenario
        its `interactions` field
          it should reflect the new when / then clause arrays in declared order

    with a Scenario appended to the first Story
      the Story constant for the first Story
        it should expose one additional keyed Scenario property at the end

  that has been edited in the TypeScript source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid TypeScript story-spec tree
    the sync
      it should be rejected

### Python backend

a Python story-spec Story Map
<!-- A concrete backend of "a code Story Map". Every "a code Story Map" behavior applies. Only observe the Python declarations that make a Story constant or a Scenario definition. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<sub_epic_snake>_stories.py`
      it should import the shared story-types module using a relative import matching its folder depth
      it should parse as a valid Python module

    every Epic folder
      it should hold an `__init__.py` helper file exposing any shared story-type re-exports needed by leaf files

    every Story constant
      it should be a module-level assignment named after the Story in UPPER_SNAKE_CASE
      it should be typed as `Story` (a TypedDict or dataclass defined in story-types)
      it should carry `story`, `actor`, `domainTerms`, and `evidence` fields matching the domain values
      it should expose one keyed Scenario entry per Scenario, keyed by the Scenario's snake_case slug

    every Scenario entry inside a Story constant
      it should hold `name`, `given`, and `interactions` fields
      its `interactions`
        it should be a list of records carrying `when` and `then` string lists in declared order

    with a Scenario appended to the first Story
      the Story constant for the first Story
        it should expose one additional Scenario entry at the end

    with the given clauses of the first Scenario updated
      the Scenario entry for the first Scenario
        its `given` list
          it should carry the updated clauses verbatim

  that has been edited in the Python source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid Python story-spec tree
    the sync
      it should be rejected

### Java backend

a Java story-spec Story Map
<!-- A concrete backend of "a code Story Map". Every "a code Story Map" behavior applies. Only observe the Java declarations that make a Story constant or a Scenario definition. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<SubEpicPascalCase>Stories.java`
      it should open with a `package` declaration matching its folder path under the tests root
      it should import the shared story-types package
      it should parse and compile as a valid Java source file

    every Epic folder
      it should hold a shared helper class of type re-exports needed by leaf files

    every leaf file's outer class
      it should be a `class <SubEpicPascalCase>Stories`
      it should hold one `public static final Story` field per Story in the SubEpic, named after the Story in UPPER_SNAKE_CASE

    every Story field
      it should carry the Story's name, actor, domainTerms, and evidence via record constructors
      it should expose one Scenario field (as a nested static record) per Scenario, named after the Scenario in camelCase

    every Scenario field inside a Story
      it should carry its name, given clauses, and interactions via nested Interaction records

    with a Scenario appended to the first Story
      the Story field for the first Story
        it should carry one additional Scenario field at the end

    with the given clauses of the first Scenario updated
      the Scenario field for the first Scenario
        its given clause list
          it should carry the updated clauses verbatim

  that has been edited in the Java source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid Java story-spec tree
    the sync
      it should be rejected

### JavaScript backend

a JavaScript story-spec Story Map
<!-- A concrete backend of "a code Story Map". Every "a code Story Map" behavior applies. Only observe the JavaScript declarations that make a Story constant or a Scenario definition. Mirrors TypeScript minus the type annotations and `satisfies` clause. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<sub-epic-slug>-stories.js`
      it should carry a JSDoc `@type {import('../story-types.js').Story}` annotation on each Story constant
      it should parse as valid JavaScript

    every Story constant
      it should be an exported const named after the Story in PascalCase
      it should carry `story`, `actor`, `domainTerms`, and `evidence` fields
      it should expose one keyed Scenario property per Scenario, keyed by a camelCased slug

    every Scenario property inside a Story constant
      it should hold `name`, `given`, and `interactions` fields carrying plain JS arrays and objects

    with the given clauses of the first Scenario updated
      the Scenario property for the first Scenario
        its `given` array
          it should carry the updated clause strings verbatim

    with a Scenario appended to the first Story
      the Story constant for the first Story
        it should expose one additional keyed Scenario property at the end

  that has been edited in the JavaScript source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid JavaScript story-spec tree
    the sync
      it should be rejected

## Cross-Format Round-Trips

<!-- Every format renders the same domain tree. A canonical Story Map should survive a round-trip through any pair of formats with no information loss on the tree's shape, Story fields, Scenario fields, or Increment fields. -->

a canonical Story Map with epics, sub-epics, stories, scenarios, and increments

  rendered to JSON and read back
    the reconstructed Story Map
      it should be equal to the canonical Story Map by every field

  rendered to Markdown and read back
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story, Scenario, and Increment (Markdown carries scenarios inline; Increments live in `thin-slicing.md`)

  rendered to TypeScript and read back
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story, and Scenario
      its increments
      <!-- Code delegates Increment to Markdown; when read back alone, increments are empty. Combined with a sibling `thin-slicing.md`, increments are populated. -->
        it should be empty if no `thin-slicing.md` accompanies the code tree

  rendered to DrawIO (story-map + scenarios + thin-slicing views) and read back together
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story from `story-map.drawio`
      it should hold every Scenario from `scenarios.drawio`
      it should hold every Increment from `thin-slicing.drawio`

  translated from JSON to TypeScript
    every Scenario
      it should appear as a keyed property on the corresponding Story constant, NOT as an entry in a legacy `acceptance_criteria` array

  translated from JSON to any diagram view
    the target view
      it should reconcile only the child pair it owns (story-map view owns epics; scenario view owns Story.scenarios; thin-slice view owns increments)

## Workspace and Loader

a workspace loaded from a directory

  when no story-map source is present
    the workspace
      it should carry an empty StoryMap
      it should report hasStoryMap as false

  when a `story-graph.json` is present
    the loader
      it should pick `story-graph.json` as the primary source
      it should populate epics, sub-epics, stories, and scenarios in one pass from the JSON

  when both `story-graph.json` and `story-map.drawio` are present
    the loader
      it should prefer `story-graph.json` per the detection order (json → drawio → md → code)

  when only `story-map.drawio` is present as the primary source
    the loader
      it should load structure from `story-map.drawio`
      it should invoke the loose-scenario path against a sibling `scenarios.drawio` when present
      it should populate Story.scenarios via _attachLooseScenariosToStoryMap

  when `story-map.md` is the primary source with inline scenarios
    the loader
      it should embed scenarios during parse
      it should NOT invoke the loose-scenario path

  when the primary source is a language code tree
    the loader
      it should pick the tree it finds under the tests root (TypeScript, Python, Java, or JavaScript)
      it should embed scenarios during parse from the leaf files

  when `thin-slicing.md` is present
    the loader
      it should populate `StoryMap.increments` via reconciliation through the increment child pair
      the workspace
        it should report hasIncrements as true

  when `thin-slicing.md` is absent but `thin-slicing.drawio` is present
    the loader
      it should populate `StoryMap.increments` from the DrawIO thin-slice view

  when no thin-slicing document is present
    the workspace
      it should hold `StoryMap.increments` as an empty list
      it should report hasIncrements as false

  when tier test files are present
    the loader
      it should discover the workspace's Tier set from file-name segments
      it should discover the workspace's Language set from file extensions
      every SubEpic with matching test files
        it should carry one TestSuite per (Tier, Language) pair with a matching sibling `*-stories.<ext>`
      every Story with matching test cases in a suite
        it should carry one TestCase per tier where a case was found
      the workspace
        it should report hasTestSuites as true when at least one TestSuite exists

  when a tier test file has no sibling `*-stories.<ext>` in the same language
    the loader
      it should raise a loader error naming the missing stories file

  when `story-context.md` files are present in epic or sub-epic folders
    the workspace
      it should carry one StoryContext per file
      it should report hasStoryContexts as true

  after `load_workspace` completes
    scanners receiving the Workspace
      it should see StoryMap already populated with Epic, SubEpic, Story, Scenario, TestSuite, TestCase, Test, and Increment
      it should never invoke a sub-loader themselves
      it should traverse the model to detect orphans (unmatched scenarios, unmatched test cases, story-name references in Increments that don't match any Story)
