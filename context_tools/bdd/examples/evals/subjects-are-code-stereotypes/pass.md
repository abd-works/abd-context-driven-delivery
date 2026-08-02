# HIERARCHY: story-graph-ops (excerpt — domain-concept subjects)

<!--
Passes: subjects-are-domain-concepts, domain-practice-alignment.

Every top-level describe is a domain concept a domain expert would recognise.
No LanguageAst, CodeStoryNode, RowPositions, Synchronizer, or other
compiler-/service-class stereotypes.
-->

## Story Model

a Story Map
  it should hold no Epics
  with 4 Epics in sequential order
    it should hold 4 Epics

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics
    it should contain 4 top-level headings in sequential order

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row

a DrawIO Story Map
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

a TypeScript story-spec Story Map
  that holds a rendered code Story Map with 4 Epics
    every leaf file
      it should parse as valid TypeScript and typecheck against the story-types module
