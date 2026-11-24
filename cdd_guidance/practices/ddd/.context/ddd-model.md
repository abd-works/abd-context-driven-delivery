# cdd_guidance/practices/ddd

*Ddd* is the practice: bounded contexts, the aggregate model, and tactics. *DddReading* is its part in the knowledge graph: it reads DDD's nodes after the Clean Engineering classes it extends. The whole model of this module, internals included, is `cdd_guidance/practices/ddd/model/.context/ddd-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep the software in the business's language, with each rule held in the aggregate that owns it, before any technical detail is added.
- **Seam (terms):** Ddd, DddReading
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices/sketch_document, cdd_guidance/practices/clean_engineering

## Ddd : PracticeGuidance

The DDD practice: bounded context, model, and tactics. Its python and typescript formats are Clean Engineering's class models.

+ Ddd(fidelity: str = 'bounded_context', format: str | None = None)
------
+ formats_type: type
	// DddFormats
+ reading_type: type
	// DddReading
+ extends: str
	// clean_engineering
+ shows_every_fidelity: bool
----
---<<reads the graph with>>--> DddReading
---<<writes code with>>--> PythonCleanEngineeringModel
---<<writes code with>>--> TypeScriptCleanEngineeringModel
---<<registers with>>--> DomainNode

## DddReading : PracticeReading

DDD's nodes, read after Clean Engineering's classes, and its graph checks with Clean Engineering's.

------
+ reads_after: tuple[str, ...]
+ class_types: tuple[str, ...]
+ root: Path
----
+ own_graph_checks(): dict
+ read_working_copy(): None
---<<reads classes of>>--> CleanEngineeringModel
