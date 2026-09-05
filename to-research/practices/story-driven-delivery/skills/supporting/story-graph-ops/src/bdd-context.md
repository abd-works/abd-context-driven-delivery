# HIERARCHY: story-graph-ops
<!-- Section headings (##) group subjects by mechanism from src/architecture-context.md. They are navigation only — not describes. -->
<!-- Every non-leaf describe is a subject noun phrase (a X, the X) or a state elaboration opened with "with" or "that" — never a bare category, an action verb, or a when/if/given keyword. -->
<!-- Every leaf is "it should ..." — if "it" would be ambiguous, add a nested describe naming the intended subject and observe under that. -->

## Story Model

a Story Map
  it should hold no Epics

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
          it should keep its Stories and AcceptanceCriteria

      with the first SubEpic of the first Epic holding 2 Stories
        the first SubEpic of the first Epic
          it should hold 2 Stories

        with a Story appended to the first SubEpic
          the first SubEpic of the first Epic
            it should hold 3 Stories

        with the first Story of the first SubEpic removed
          the first SubEpic of the first Epic
            it should hold 1 Story
            it should discard the AcceptanceCriteria that lived under the removed Story

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
            it should keep its AcceptanceCriteria

        with the first Story of the first SubEpic holding 3 AcceptanceCriteria
          the first Story of the first SubEpic
            it should hold 3 AcceptanceCriteria

          with an AcceptanceCriteria appended to the first Story
            the first Story of the first SubEpic
              it should hold 4 AcceptanceCriteria
            the last AcceptanceCriteria in sequential order
              it should be the appended AcceptanceCriteria

          with the first AcceptanceCriteria of the first Story removed
            the first Story of the first SubEpic
              it should hold 2 AcceptanceCriteria
              it should renumber the remaining AcceptanceCriteria

          with the text of the first AcceptanceCriteria updated
            the first AcceptanceCriteria of the first Story
              it should carry the new text
            the first Story of the first SubEpic
              it should preserve the sequential order of the AcceptanceCriteria

          with the AcceptanceCriteria reordered
            the first Story of the first SubEpic
              it should list the AcceptanceCriteria in the new order

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

## Documents

a Markdown document
  it should contain no headings

  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 top-level headings
    it should contain 3 second-level headings under the first top-level heading
    it should list every Story as a bullet under its SubEpic
    it should list every AcceptanceCriteria as an indented bullet under its Story
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

  that is being read back into a MarkdownStoryMap
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story, and AcceptanceCriteria in sequential order

  that has been edited and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document

  that is not a valid Markdown story map
    the read
      it should be rejected

a story-graph.json document
  it should contain no Epics

  that holds a serialized Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic entries
    the first Epic entry
      it should contain 3 SubEpic entries
    every Story
      it should be nested under its SubEpic entry
    every AcceptanceCriteria
      it should be nested under its Story entry
    every Story entry
      it should preserve its StoryType field
    it should preserve the sequential order of every node

    with a fifth Epic appended and the document re-serialized
      it should contain 5 Epic entries

    with the first Epic removed and the document re-serialized
      it should contain 3 Epic entries
      it should hold no orphan SubEpic entries

  that is being read back into a JsonStoryMap
    the reconstructed Story Map
      it should hold every Epic, SubEpic, Story, and AcceptanceCriteria in sequential order

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

a diagram Story Map
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
          it should keep its Stories and AcceptanceCriteria at the new X

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
            it should keep its AcceptanceCriteria

  that has been asked to place a SubEpic as a parent of an Epic
    it should reject the placement

  that has been asked to place a Story as a parent of a SubEpic
    it should reject the placement

  that has been asked to place any child under a Story
    it should reject the placement

  that has been asked to give an Epic any parent
    it should reject the parent

a DrawIO Story Map
<!-- Every "a diagram Story Map" behavior above applies. The observations here only verify that operations on the Story Map surface externally in the DrawIO document — new shapes appear, renamed shapes carry the new label, deleted shapes are gone. Positioning is already proven above; do not repeat it. -->
  that holds a rendered diagram Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should serialize as a valid DrawIO document
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

  that has been edited in the DrawIO document and synced back
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
    the reconstructed diagram Story Map
      it should reflect every edit made to the document

  that is not a valid DrawIO document being synced
    the sync
      it should be rejected

a Miro Story Map
<!-- Every "a diagram Story Map" behavior above applies. The observations here only verify that operations on the Story Map surface externally on the Miro board. Positioning is already proven above; do not repeat it. -->
  that holds a rendered diagram Story Map with 4 Epics and 3 SubEpics under the first Epic
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

  that has been edited on the Miro board and synced back
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the board
    the reconstructed diagram Story Map
      it should reflect every edit made to the board

  that does not respond as a valid Miro story map when synced
    the sync
      it should be rejected

## Code
<!-- The subject is a Story Map that renders to a source-code tree. -->
<!-- Vocabulary comes from what the legacy generators actually produce: -->
<!--   - pml-domain/tests/generate-stories.py produces `<epic>/<sub-epic>/<sub-epic>-stories.ts` spec-data files with one exported constant per Story and one camelCased scenario property per AcceptanceCriteria. -->
<!--   - abd-story-acceptance-test templates produce `<epic>/<sub-epic>/<sub-epic>.py` (or .js/.java) test files with one class per Story and one test method per AcceptanceCriteria. -->
<!-- Both share the same folder tree, the same "one leaf file per lowest-level SubEpic" rule, and the same "one Story block per Story, one Scenario per AcceptanceCriteria" rule. Only the leaf-file syntax differs. -->
<!-- Every operation on `a code Story Map` is observed for BOTH the domain change AND the file-tree consequence. Backend subjects add ONLY the backend-specific leaf-file shape. -->

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
        it should produce exactly one leaf file inside its own sub-folder, named after the SubEpic slug

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
          its Story blocks
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
          its Story blocks and their Scenarios
            it should be unchanged

      with the first SubEpic of the first Epic holding 2 Stories
        the leaf file for the first SubEpic
          it should contain 2 Story blocks
        every Story
          it should produce one Story block inside its SubEpic's leaf file, named after the Story

        with a Story appended to the first SubEpic
          the leaf file for the first SubEpic
            it should contain 3 Story blocks
          the appended Story
            it should produce a new Story block

        with the first Story of the first SubEpic renamed
          the Story block for the first Story
            it should carry the new Story name

        with the first Story moved from the first SubEpic to the second SubEpic
          the leaf file for the first SubEpic
            it should no longer contain the Story block for the moved Story
          the leaf file for the second SubEpic
            it should contain the Story block for the moved Story

        with the first Story of the first SubEpic holding 3 AcceptanceCriteria
          the Story block for the first Story
            it should expose 3 Scenarios (one per AcceptanceCriteria) in the AcceptanceCriteria's declared order
          every AcceptanceCriteria
            it should produce one Scenario inside its Story block, holding the AcceptanceCriteria's Gherkin steps in order

          with an AcceptanceCriteria appended to the first Story
            the Story block for the first Story
              it should expose 4 Scenarios
            the appended AcceptanceCriteria
              it should produce a new Scenario at the end

          with the first AcceptanceCriteria of the first Story removed
            the Story block for the first Story
              it should expose 2 Scenarios
              it should no longer expose the Scenario for the removed AcceptanceCriteria

          with the text of the first AcceptanceCriteria updated
            the Scenario derived from the first AcceptanceCriteria
              it should carry the updated step text

          with the AcceptanceCriteria of the first Story reordered
            the Story block for the first Story
              it should expose its Scenarios in the new order

  that holds hand-written regions in a leaf file outside the generated Story blocks
    with the leaf file regenerated
      the leaf file
        it should preserve every hand-written region byte-for-byte
      the generated Story blocks
        it should be the only regions rewritten

  that has been asked to render into a folder that is not a valid code Story Map tree
    the render
      it should be rejected

a TypeScript story-spec Story Map
<!-- A concrete backend of "a code Story Map" that renders each leaf SubEpic to a `<sub-epic>-stories.ts` file matching the pml-domain/tests/ shape. -->
<!-- Every "a code Story Map" behavior applies. Do not restate folder or Story-block structure here. Only observe the TypeScript declarations that make a Story block or a Scenario. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<sub-epic-slug>-stories.ts`
      it should import the Step, AcceptanceCriterion, and Background types from the shared story-types module using a relative path matching its folder depth
      it should parse as valid TypeScript and typecheck against the story-types module

    every Story block
      it should be an exported const named after the Story in UPPER_SNAKE_CASE, initialised with `as const`
      it should carry a `story` field holding the Story name as a template-string literal
      it should carry an `actor` field holding the Story's actor as a template-string literal
      it should carry an `acceptance_criteria` field holding a readonly array of Step arrays, one array per AcceptanceCriteria in declared order
      it should carry `domain_terms` and `evidence` fields, empty when the Story declares none
      it should expose one Scenario property per AcceptanceCriteria, keyed by a camelCased slug derived from the AcceptanceCriteria's when/then text and truncated to at most 10 words

    every Scenario property inside a Story block
      it should hold a `name` field carrying the human-readable Scenario name
      it should hold a `steps` field carrying the same Step array as the corresponding entry in `acceptance_criteria`, typed as `readonly Step[]`

    every Step within a Scenario
      it should be a single-keyed object using one of `given`, `when`, `then`, `and`, or `but`, whose value is a template-string literal

    with the first AcceptanceCriteria of the first Story updated
      the `acceptance_criteria` entry for the first AcceptanceCriteria
        it should carry the updated Step array
      the Scenario property derived from the first AcceptanceCriteria
        its `steps` field
          it should carry the same updated Step array

  that has been edited in the TypeScript source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid TypeScript story-spec tree
    the sync
      it should be rejected

a Python acceptance-test Story Map
<!-- A concrete backend of "a code Story Map" that renders each leaf SubEpic to a `<sub-epic>.py` file of executable pytest tests matching the abd-story-acceptance-test Python template. -->
<!-- Every "a code Story Map" behavior applies. Do not restate folder or Story-block structure here. Only observe the Python declarations that make a Story block or a Scenario. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<sub_epic_snake>.py`
      it should import pytest and expose no module-level test statements
      it should parse as a valid Python module

    every Epic folder
      it should hold an `<epic_snake>_helper.py` file exposing an `<Epic>Helper` class of shared `given_*`, `when_*`, and `then_*` methods, and no test classes

    every Story block
      it should be a `class Test<StoryPascalCase>` inheriting from its Epic's `<Epic>Helper` class
      it should carry a docstring holding the Story name and its one-line description

    every Scenario derived from an AcceptanceCriteria
      it should be a `def test_<scenario_snake>(self)` method on its Story class, in the AcceptanceCriteria's declared order
      its docstring
        it should hold `SCENARIO:`, `GIVEN:`, `WHEN:`, and `THEN:` lines quoting the AcceptanceCriteria's Gherkin steps
      its body
        it should be an orchestrator of `# Given` / `# When` / `# Then` comment sections, each calling `self.given_*`, `self.when_*`, or `self.then_*` helpers rather than inlining setup or assertions

    with an AcceptanceCriteria added to the first Story
      the `Test<Story>` class for the first Story
        it should carry one additional `test_<scenario>` method at the end
      the Epic helper class
        it should carry any newly referenced `given_*`, `when_*`, or `then_*` helpers required by the new method

  that has been edited in the Python source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid Python acceptance-test tree
    the sync
      it should be rejected

a Java acceptance-test Story Map
<!-- A concrete backend of "a code Story Map" that renders each leaf SubEpic to a `<SubEpicPascalCase>Test.java` file of executable JUnit 5 tests matching the abd-story-acceptance-test Java template. -->
<!-- Every "a code Story Map" behavior applies. Do not restate folder or Story-block structure here. Only observe the Java declarations that make a Story block or a Scenario. -->

  that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic
    every leaf file
      it should be named `<SubEpicPascalCase>Test.java`
      it should open with a `package` declaration matching its folder path under the tests root
      it should import JUnit 5 (`org.junit.jupiter.api.Test`, `DisplayName`, `Nested`, `BeforeEach`, `AfterEach`, and the static `Assertions`)
      it should parse and compile as a valid Java source file

    every leaf file's outer class
      it should be a `class <SubEpicPascalCase>Test` carrying `@DisplayName` set to the SubEpic's human-readable name
      it should hold the shared `given*`, `when*`, and `then*` helpers as `private static` methods, and no `@Test` methods of its own

    every Story block
      it should be an `@Nested class <StoryPascalCase>Tests` inside its SubEpic's outer class, carrying `@DisplayName` set to the Story name

    every Scenario derived from an AcceptanceCriteria
      it should be a `@Test`-annotated `void <scenarioNameCamelCase>()` method on its Story's `@Nested` class, in the AcceptanceCriteria's declared order
      it should carry `@DisplayName` set to the Scenario's outcome in plain English
      its body
        it should be an orchestrator of `// Given` / `// When` / `// Then` comment sections, each calling one of the outer class's `given*` / `when*` / `then*` helpers rather than inlining setup or assertions

    with an AcceptanceCriteria added to the first Story
      the `@Nested` class for the first Story
        it should carry one additional `@Test` method at the end
      the outer class's private static helpers
        it should carry any newly referenced `given*` / `when*` / `then*` helpers required by the new method

  that has been edited in the Java source and synced back against a canonical code Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the source
    the reconstructed code Story Map
      it should reflect every edit made to the source

  that is not a valid Java acceptance-test tree
    the sync
      it should be rejected
