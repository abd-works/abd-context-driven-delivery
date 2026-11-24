# cdd_guidance/patterns

Each pattern is a *PracticeGuidance* that adds rules for one kind of solution, and its *GraphOverlay*, kept as `graph_overlay`, adds the nodes and facts those rules read; *DomainDrivenStack* is the base for a domain-organized TypeScript stack such as *LernDomainDriven* and *MernDomainDriven*. Importing the package registers the patterns with harness/graph's *PatternOverlays*, after registering the practices they build on.

- **Purpose:** Add the guidance and the graph rules one kind of solution needs on top of the practices, without changing a practice.
- **Seam (terms):** DomainDrivenStack, LernDomainDriven, MernDomainDriven, CddWebDomainAccess, CddClaudeMod, LernOverlay, WebDomainAccessOverlay
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/graph, cdd_guidance/practices (the package, which registers the practices), cdd_guidance/practices/stories, cdd_guidance/practices/ddd, cdd_guidance/practices/bdd, cdd_guidance/practices/clean_engineering (*SourceText*, to read facts)

## DomainDrivenStack : PracticeGuidance

Implementation fidelity for a domain-module-organized TypeScript stack on an already-designed vertical slice: acceptance tests first, with Stories at acceptance_tests in TypeScript, then the production code they drive.

+ DomainDrivenStack()
------
----

## LernDomainDriven : DomainDrivenStack

The LERN stack: lowdb JSON files, Express, React, and Node, in TypeScript, organized by domain module.

------
+ << composition >> graph_overlay: LernOverlay
----
+ test_setup_text(root: Path): str
---<<creates>>--> LernOverlay

## LernOverlay : GraphOverlay

Reads the LERN tiers of a working copy onto the practices the graph holds: behavior files on BDD, tier files on DDD's aggregates, and story files on Stories.

------
+ direct_kinds: frozenset[str]
----
+ read(graph: Graph): None
---<<finds a practice with>>--> Ddd
---<<finds a practice with>>--> Stories
---<<finds a practice with>>--> Bdd
---<<reads facts with>>--> SourceText

## MernDomainDriven : DomainDrivenStack

The MERN stack: MongoDB, Express, React, and Node, in TypeScript, organized by domain module.

------
----

## CddWebDomainAccess : PracticeGuidance

How code outside Python reaches the CDD domain: through MCP tools, by a language adapter the installer deploys.

+ CddWebDomainAccess()
------
+ << composition >> graph_overlay: WebDomainAccessOverlay
----
---<<creates>>--> WebDomainAccessOverlay

## WebDomainAccessOverlay : GraphOverlay

Adds each access tier file of a working copy to DDD's part of the graph, with the facts its access rules read.

------
----
+ read(graph: Graph): None
---<<finds a practice with>>--> Ddd
---<<reads facts with>>--> SourceText

## CddClaudeMod : PracticeGuidance

A Claude Code mod that is a view of the CDD domain: each component runs view, client, MCP tool, domain.

+ CddClaudeMod()
------
+ << composition >> graph_overlay: GraphOverlay
----
