# HIERARCHY: story-graph-ops — section labels used as top-level describes

<!--
Violates: category-headings-not-subjects.

`Story Model`, `Documents`, `Diagrams`, `Code` are organizational category labels,
not domain subjects. Read any one of them in isolation — none names an observable
thing whose state can be narrowed and observed. They belong as `##` markdown
headings, not as top-level describes.

Everything nested underneath is otherwise well-formed state-oriented BDD, so the
other rules cannot catch this — the shape is broken at the top level, before the
first real subject describe.
-->

Story Model

  a Story Map
    it should hold no Epics
    with 4 Epics in sequential order
      it should hold 4 Epics
      with a fifth Epic appended
        it should hold 5 Epics

Documents

  a Markdown document
    that holds a rendered Story Map with 4 Epics
      it should contain 4 top-level headings

  a JSON document
    that holds a rendered Story Map with 4 Epics
      it should contain 4 Epic entries in declared order

Diagrams

  a diagram Story Map
    that holds a rendered Story Map with 4 Epics
      it should contain 4 Epic elements on the Epic row
      with a fifth Epic appended
        it should contain 5 Epic elements on the Epic row

Code

  a code Story Map
    that holds a rendered Story Map with 4 Epics
      every Epic
        it should produce a folder under the tests root, named after the Epic slug
