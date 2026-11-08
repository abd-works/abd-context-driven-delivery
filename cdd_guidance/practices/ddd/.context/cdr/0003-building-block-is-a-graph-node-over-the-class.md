# The graph's building block holds the class Clean Engineering read

**Status:** decided, round 6 (finding M4).

## Decision

In the knowledge graph a DDD building block is a *BuildingBlock*: a graph node of DDD's practice that holds the *OoadClass* Clean Engineering read (through *TacticalClass*). Its own facts are the tactical ones DDD's rules read; every other fact is the class's, answered by asking the class.

## Why

- The class is Clean Engineering's node in the graph, with its edges to its module, members, and dependencies. A building block that subclassed *OoadClass* would be a second class node for the same source class, so every Clean Engineering rule would run on it twice and its edges would have to be copied; that is the duplicated shape the guardrails forbid.
- Holding the class keeps one object per class: the building block adds DDD's view of it (its kind and tactical facts) and stays on DDD's practice, so DDD's rules find DDD's nodes and Clean Engineering's rules find Clean Engineering's.
- The document formats' *Entity*, *ValueObject*, and *Repository* are classes of a map read from a document, which holds no graph facts; the graph reads code, where the class already exists. The two meet at *TacticalClass*, the one reading of a class's DDD kind and naming convention.

## Consequences

A tactical fact is a property on *BuildingBlock* listed in its `graph_facts`, such as `named_for_its_kind`; a fact about the class itself is added to the class, in Clean Engineering.
