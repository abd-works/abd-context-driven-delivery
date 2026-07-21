<!-- @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only. -->
<!-- invoke-edit: action satisfy | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering -->

# OoadNode

OoadNode(name: str, sequential_order: int)
------
name: str
sequential_order: int
----
translate_from(source: OoadNode): UpdateReport
update_self(source: OoadNode): None
child_collections(source: OoadNode): list[ChildCollectionPair]
- _reconcile_collection(pair: ChildCollectionPair, report: UpdateReport): None
- _find_match(source: OoadNode, candidates: list[OoadNode], consumed_ids: set): OoadNode | None

# OoadClass : OoadNode

OoadClass(name: str, sequential_order: int, intent: str)
------
intent: str
properties: list[Property]
operations: list[Operation]
relationships: list[Relationship]
collaborators: list[str]
----
update_self(source: OoadNode): None
child_collections(source: OoadNode): list[ChildCollectionPair]

# OoadModel : OoadNode

OoadModel(name: str, sequential_order: int)
------
classes: list[OoadClass]
----
update_self(source: OoadNode): None
child_collections(source: OoadNode): list[ChildCollectionPair]

# Property

Property(name: str, type_hint: str, description: str)
------
name: str
type_hint: str
description: str
----

# Operation

Operation(name: str, parameters: list[str], return_type: str, description: str)
------
name: str
parameters: list[str]
return_type: str
description: str
----

# Relationship

Relationship(target: str, kind: str, cardinality: str, description: str)
------
target: str
kind: str
cardinality: str
description: str
----

# UpdateReport

UpdateReport()
------
changes: list[Change]
----
add_exact_match(name: str): None
add_new(node: OoadNode, parent_name: str): None
add_removed(node: OoadNode, parent_name: str): None
adds(): list[Change]
removes(): list[Change]

# ChildCollectionPair

ChildCollectionPair(self_children: list[OoadNode], source_children: list[OoadNode], create_child: Callable)
------
self_children: list[OoadNode]
source_children: list[OoadNode]
create_child: Callable[[OoadNode], OoadNode]
----

# Change

Change(kind: ChangeKind, from_name: str | None, to_name: str | None, node_name: str | None, parent_name: str | None)
------
kind: ChangeKind
from_name: str | None
to_name: str | None
node_name: str | None
parent_name: str | None
----
