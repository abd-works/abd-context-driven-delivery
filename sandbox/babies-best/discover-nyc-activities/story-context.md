---
fidelity: [scenarios]
artifact: [story-context]
format: md
---

# Discover Nyc Activities

**Status:** fully expanded for scenarios generation

**Stories in scope:**

Browse Activities Catalog:
- *Browse Activities For Age And Place*
- *Choose Place On First Visit*
- *Filter By Borough Then Neighborhood*
- *Include Citywide Activities*
- *Filter Activities By Kind*
- *Override Age Band On Activities*
- *Show Empty Place Results*

Inspect Activity:
- *Open Evergreen Activity Detail*
- *Open Dated Event Detail*
- *Save Activity To List From Detail*

**Context / notes:** Editorial catalog of evergreen places/experiences and dated events. Activity stores optional Neighborhood only (`null` = citywide); borough derived from `neighborhood.borough` (CDR 0001). PlaceFilter narrows borough → neighborhood for browse and is remembered across visits; first visit requires choosing place. Age defaults from BabyProfile with manual override on the catalog. Save-to-list hands off to Personal Lists (CRUD out of scope this increment).

**Sources / context:** `.context/babies-best-sketch.md`; `.context/sessions/babies-best/grill-answers.md`; `.context/cdr/0001-activity-links-neighborhood-only.md`
