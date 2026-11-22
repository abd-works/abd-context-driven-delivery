# One Thing Is One Node In The Graph

A serious defect, decided by the person on 2026-11-22. To be fixed after every robot working on the release 1.2 fixes is done and its work is committed, because the fix changes how every practice reads itself into the knowledge graph.

## The defect

A thing written in two formats is two nodes in the graph. A class written in a model document and in Python is one class node read from the markdown and another read from the code, joined by an `implements` edge. In this repository's saved graph of 2026-11-21, 290 class names have both a markdown node and a Python node, 283 `implements` edges join such pairs, seven pairs have no joining edge, and the graph counts 2,988 class nodes for about 1,990 classes. The exploratory testers raised the same shape in round 3 as a question: one class can be up to eight nodes across DDD, Clean Engineering, languages and folders. Stories has it too: a scenario in markdown and its story test in Python are two sets of nodes.

What it costs: a class's facts are split between two nodes, counts are doubled, the graph tree shows the class twice, and a rule that wants the whole class has to follow the joining edge and sees two unrelated classes where that edge is missing.

## The decisions

1. **One thing is one node.** A class, a story, a scenario or a step written in more than one format is one node. This holds for every practice.
2. **A graph is loaded in the format selected and does not cross formats.** Loading markdown gives the nodes as the markdown has them; loading Python gives them as the code has them. The loader does not read one format and go looking in another to join or compare.
3. **Several formats selected in the graph view.** A node written in more than one of the selected formats is still one node in the tree, and selecting it shows each of its files in the file view, one for each format.
4. **Facts with several formats selected.** The one node carries the facts of each selected format, each fact from the format that supplies it: the code's measures and the model document's description sit together on the one class.
5. **"Model" means the model fidelity, not the markdown format.** A model is written at the model fidelity in code, in markdown or as a diagram. The rule that the code must not break the model's shape is a rule between two fidelities, model and code, whatever format each is written in. It is kept by the order of work, not by a comparison across formats: render the code from the markdown or the diagram, which gives it the model's shape, then generate the implementation into that shape. No graph rule compares a markdown node with a code node of the same class.

## What the fix removes

- the second node for a thing written in two formats
- the `implements` edges that exist only to join the two
- any rule or reading that works by comparing one format's node with another format's node of the same thing

## To settle when the fix starts

- how the seven unjoined pairs come about today, and whether each is a class that really differs or a join the reader missed
- what a node's identity is, so the same class read from two formats lands on one node (the rule of change 10, join by identity, applies: file, class and language decide, and the name is used only inside that)
- how the saved graph records a node's place in each format
