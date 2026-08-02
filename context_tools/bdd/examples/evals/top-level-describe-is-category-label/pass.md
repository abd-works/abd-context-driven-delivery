# HIERARCHY: story-graph-ops — categories as markdown headings

<!--
Passes: category-headings-not-subjects, state-oriented-hierarchy,
domain-practice-alignment.

`Story Model`, `Documents`, `Diagrams`, `Code` are `##` markdown headings.
Every top-level describe is a domain-concept subject noun phrase.
-->

## Story Model

a Story Map
  it should hold no Epics
  with 4 Epics in sequential order
    it should hold 4 Epics
    with a fifth Epic appended
      it should hold 5 Epics

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics
    it should contain 4 top-level headings

a JSON document
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic entries in declared order

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row
    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug
