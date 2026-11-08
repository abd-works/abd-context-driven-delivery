# Every graph reader reads saved facts and edges, never a parsed object's attributes

A worker refresh (CDR 0001) starts from the graph the server holds, which is a *SavedGraph* read back as plain *Node*s: each holds its id, name, type, source lines, saved facts (`node.get_fact`), and edges, and nothing else. Only the nodes of the files the refresh reads again are the objects a practice's parser built. A reader that took an attribute only a parsed object has off one of the others failed or quietly found less:

- Stories' `StoryLinks` read `step.body.text`, and every validate that refreshed a graph holding Stories failed with `'Node' object has no attribute 'body'` (round 8). Its epic for a step was found with `isinstance(node, Epic)`, and an example's text came only from the files read now.
- Clean Engineering's `ClassGraph.fields`, the near-copy and pass-through rules, and the static-factory check read `operation.body`, `class.properties`, and `operation.return_type` through `getattr` with an empty default, so a refreshed graph lost violations, or gained them, without failing.
- Clean Engineering linked a property to the class its type names only when that class's file had been read first, so a fresh build missed links a refresh then made.
- UX's `StoryLink` asked a Stories node for `semantic_type()` and `text`, which a node read back from a saved graph has not.
- Step ids and the near-copy rule used `hash`, which Python salts per process, so the worker and the server named one step two ways.
- Reading a saved graph back recorded every edge between two practices a second time, reversed, so a graph read back held edges no build made.
- A Clean Engineering property's `owner` was worked out from its parent, which the explorer tree changes to the group it hangs the property under, so the graph saved it as empty and BDD linked observations to members a fresh build had ruled out as shared by several classes.
- A refresh held the nodes it read again after those it kept, so a rule that reports the first of two nodes (the original of two duplicate bodies) reported the other one.
- A refresh named classes by a text match over every file it did not read again, and kept the imports of those files on the practice's root, which a fresh build never does.

Whether a validate failed depended on which practices other chats had loaded into the shared session graph first.

## Decision

Every reader works from what it read now plus facts that survive a save. A reader of the graph (a practice's `link_to_other_practices`, the reading that links a practice's own nodes, a *PracticeGraphRule*, a pattern's *GraphOverlay*, UX's story links) reads a node only through what every node has:

- its `node_id`, `name`, `type`, and `source`;
- its facts, through `node.get_fact(key)`;
- the graph's edges (`graph.edges_from`, `graph.direct_parent`, `practice.in_graph.edges(kind)`).

Anything a reader needs from the parsed object is a saved fact: the model class lists it in its `graph_facts`, so a parsed object answers it from its own attribute and a node read back answers it from what was saved. This round adds `body_text` to *Operation* and *Step*, `return_type` and `value_type` to *Operation*, `value_type` to *Property*, `held_fields` to *OoadClass*, and `source_names` and `source_reads` to a story's *Example* (recorded from the source of the function that declares it). Because readers read every node the same way, a reader links or checks the nodes held from before and those read now in one pass: a refresh drops the edges of the files it reads again, and the reader links the nodes it kept to the nodes it read now from their facts.

A practice that builds its own nodes from another practice's parsed objects, as DDD builds a building block from each Clean Engineering class, builds them only from `practice.in_graph.nodes_read_now(type)` and keeps the nodes it built before (CDR 0001); that is the one reader of parsed objects, and it reads only objects the load in progress parsed.

Any id or checksum that a saved graph keeps or that decides a finding is computed with `zlib.crc32`, never `hash`. A saved graph is read back exactly: each edge as it was saved, no other way. Every build puts each practice's nodes in source order before the rules run (`put_in_source_order`). A member keeps the class that declares it as its owner (`keep_owner`) before the tree regroups it. Clean Engineering links property types and return types in one pass after every class is added, over every member it holds, and a refresh reads no file of a folder the practice already holds. The saved shape is now 3, so a graph saved without the new facts is read from the folder again.

## Considered options

- **Restore a saved graph into the same objects a fresh read makes.** Rejected: a plain node keeps only its facts, so making a parsed object again means parsing its file again, which is the whole build the refresh exists to avoid. Saving every attribute of every model object instead would carry each object's whole state (bodies, call graphs, child lists) into every build order and answer, several times the graph's size, which is the opposite of what B10 needs.
- **Guard each reader with `getattr` or an `isinstance` check and skip the nodes it cannot read.** Rejected: it drops data silently, which is how the Clean Engineering rules already went wrong.
- **Read the body back from the source file by the node's lines.** Rejected for bodies: a node's lines include its signature and docstring, which the rules leave out, and a file changed since the graph was built would give a reader text the graph does not describe. DDD's foreign-key comments are still read from a block's lines (CDR 0001), since a block's whole span is what they search.

## Consequences

- A rule or linker that needs something new from a parsed object adds it to that model class's `graph_facts` and reads it with `get_fact`; reading an attribute off a node, or `getattr` with a default, is a defect.
- `graph.json` is larger by the operation and step bodies, about five percent on this repository.
- `harness/graph/graph_build_spec.py` checks, for every practice, that a worker refresh of a graph opened from its saved graph gives what a fresh build gives, whichever practice's file it refreshes; and that a graph read back from its saved file holds what the build that saved it held.
