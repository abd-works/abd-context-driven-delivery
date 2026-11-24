# cdd_guidance/practices/bdd

*Bdd* is the practice: behavior, realization, and development. *BddGraphReading* is its part in the knowledge graph: it reads each spec file's describe tree after Clean Engineering's code, and links each observation to the Clean Engineering members it drives. The whole model of this module, internals included, is `cdd_guidance/practices/bdd/model/.context/bdd-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Turn domain vocabulary into passing tests, locking what is observed before how it is built.
- **Seam (terms):** Bdd, BddGraphReading
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices/sketch_document, cdd_guidance/practices/clean_engineering

## Bdd : PracticeGuidance

The BDD practice: behavior, realization, and development.

+ Bdd(fidelity: str = 'behavior', format: str | None = None)
------
+ reading_type: type
	// BddGraphReading
----
---<<reads the graph with>>--> BddGraphReading
---<<registers with>>--> BddModel
---<<registers with>>--> BehaviorNode

## BddGraphReading : PracticeReading

BDD's describe trees, read after Clean Engineering's code and linked to the Clean Engineering members each observation drives.

------
+ reads_after: tuple[type[PracticeGuidance], ...]
+ node_types: tuple[str, ...]
+ clean_engineering_reading: PracticeReading | None
----
+ read_working_copy(): None
---<<finds a reading with>>--> CleanEngineering
---<<links with>>--> ObservationLinks
