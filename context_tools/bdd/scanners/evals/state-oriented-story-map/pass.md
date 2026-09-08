# HIERARCHY: story-graph-ops (canonical excerpt)

<!--
This excerpt is the canonical passing shape. It demonstrates every rule in
this skill applied to a single domain:

- state-oriented-hierarchy: every non-leaf describe is a subject noun phrase
  or a state elaboration opened with `with` / `that`; every leaf is `it should …`.
- observations-are-results-not-mechanics: leaves observe outcomes an outsider
  could verify — no super calls, no factory names, no private helper names,
  no call-order facts.
- subjects-are-domain-concepts: every top-level describe is a domain concept
  a domain expert would recognise ("a Story Map", "a Markdown document",
  "a diagram Story Map", "a code Story Map", "a DrawIO Story Map",
  "a TypeScript story-spec Story Map"). No ast, node, synchronizer,
  positions, or service-class stereotype.
- category-headings-not-subjects: organizational scaffolding (Story Model,
  Documents, Diagrams, Code) is `##` markdown, not describes.
- abstract-subject-then-concrete-backends: for Diagrams and Code the shared
  behavior lives on an abstract subject (`a diagram Story Map`, `a code Story Map`);
  concrete backends are thin and add only backend-specific proofs.
-->

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

    with the first Epic renamed
      it should preserve the sequential order of the Epics
      the first Epic
        it should carry the new name

    with the first Epic holding 3 SubEpics
      the first Epic
        it should hold 3 SubEpics

      with the first SubEpic moved from the first Epic to the second Epic
        the first Epic
          it should hold 2 SubEpics
        the second Epic
          it should hold one additional SubEpic
        the moved SubEpic
          it should keep its Stories and AcceptanceCriteria

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 top-level headings in sequential order

    with the first Epic renamed in the source Story Map and re-rendered
      the first heading
        it should carry the new name

    with the first Epic removed in the source Story Map and re-rendered
      it should contain 3 top-level headings

  that has been edited in place and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, and reorder applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic elements on the Epic row in sequential order
    it should contain 3 SubEpic elements on the SubEpic row, directly under the first Epic

    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row
      the first 4 Epic elements
        it should be unchanged in position and identity

    with the first Epic removed
      it should contain 3 Epic elements
      the SubEpic elements that lived under the removed Epic
        it should be gone

a DrawIO Story Map
  <!-- Every "a diagram Story Map" behavior applies. Only DrawIO-specific
       serialization proofs live here. -->
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch
    the serialized diagram
      it should parse as valid draw.io XML

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root
      the folders for the first four Epics
        it should be byte-identical to before

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug
        its contents
          it should be byte-identical to before

    with the first Epic holding 3 leaf SubEpics
      every leaf SubEpic of the first Epic
        it should produce a sub-folder under the first Epic's folder, named after the SubEpic slug
        it should produce exactly one leaf file inside its own sub-folder, named after the SubEpic slug

      with the first SubEpic of the first Epic holding 2 Stories
        the leaf file for the first SubEpic
          it should contain 2 Story blocks
        every Story
          it should produce one Story block inside its SubEpic's leaf file, named after the Story

        with the first Story of the first SubEpic holding 3 AcceptanceCriteria
          the Story block for the first Story
            it should expose 3 Scenarios (one per AcceptanceCriteria) in the AcceptanceCriteria's declared order
          every AcceptanceCriteria
            it should produce one Scenario inside its Story block, holding the AcceptanceCriteria's Gherkin steps in order

a TypeScript story-spec Story Map
  <!-- Every "a code Story Map" behavior applies. Only TypeScript-specific
       spec-data proofs live here. -->
  that holds a rendered code Story Map with 4 Epics
    every leaf file
      it should be named `<sub-epic-slug>-stories.ts`
      it should parse as valid TypeScript and typecheck against the story-types module
    every Story block
      it should be an exported const named after the Story in UPPER_SNAKE_CASE, initialised with `as const`
    every Scenario property inside a Story block
      it should be a single-keyed object whose value carries `name` and `steps` fields
