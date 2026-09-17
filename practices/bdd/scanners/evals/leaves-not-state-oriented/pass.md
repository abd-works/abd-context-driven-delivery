# HIERARCHY: story-graph-ops (excerpt — Story Model)

<!--
Passes: state-oriented-hierarchy, category-headings-not-subjects.

Every non-leaf describe is a subject noun phrase or a state elaboration opened
with `with` / `that`. Every leaf is `it should …` observing an outside-verifiable
result. Organizational scaffolding is a `##` heading, not a describe.
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
