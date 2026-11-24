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

6. **Which fidelity is right when two disagree.** In general the fidelity with the most detail is the source of truth: code over a model, a model over a module description. People still often edit a fidelity with less detail first, such as a module description or a story's scenarios in drawio or markdown, and then write the tests and the code to match. So neither direction of change is wrong, and a difference between two fidelities is something to report, not something a load refuses.
7. **Differences are reported by the repository's e2e test, not by a load.** As part of the e2e test of a repository, compare the graph across its fidelities and report where they disagree: an operation the code has that the model lacks, a scenario the story test lacks, a module the code has that the module description lacks. That keeps a load simple, in one format with no crossing, and still tells the team when a lower fidelity has fallen behind the code or the code has not yet caught up with an edited model.

## What the fix removes

- the second node for a thing written in two formats
- the `implements` edges that exist only to join the two
- any rule or reading that works by comparing one format's node with another format's node of the same thing

## To settle when the fix starts

- how the seven unjoined pairs come about today, and whether each is a class that really differs or a join the reader missed
- what a node's identity is, so the same class read from two formats lands on one node (the rule of change 10, join by identity, applies: file, class and language decide, and the name is used only inside that)
- how the saved graph records a node's place in each format

## Settled when the fix started (2026-11-24)

**How the unjoined pairs come about.** The saved graph of 2026-11-21 that counted seven is gone; the graph is rebuilt on every load. The same count on the repository at `a6ea950f5`, after the class model was split into one model per module, found 100 model-document classes whose name code declares and no `implements` edge reached, out of 587 names with both. None was a join the reader missed by accident; each is one of four kinds:

- A model describes a class of another module, drawn on its card as a collaborator: `space/kanban/.context/kanban-model.md` describes *Session*, *Repo*, *Violation*, *PracticeGuidance* and *Rule*, which live in `space/session`, `space/repo`, `harness/graph` and `harness/guidance`; `harness/guidance`'s models describe *PracticeReading*, which lives in `harness/graph`.
- The code moved out of the module the model describes, and the model still describes it: *CodeBody*, *SourceText*, *ScriptImports* and eleven more moved to `cdd_guidance/practices/source_code`, and the measures classes sit in `clean_engineering/measures`, while `clean_engineering/model/.context/ooad-model.md` and `clean_engineering/.context/clean_engineering-model.md` still describe them.
- Two different classes share a name: the graph model's *Rules* is not `harness/installation/files.py`'s *Rules*.
- Two files of the module declare the name, in two languages: *PromptQueue* in `prompt_queue.py` and `queue-order.ts`, *TicketWork* in `ticket.py` and `ticket-work.ts`.

The first two are differences between fidelities, which decision 7 gives to the repository's e2e test; the last two are classes the module and the language tell apart, so they stay apart. A fifth kind, test support such as `harness/graph/rule_fixture.py`'s *RuleFixture* that a model describes, was a missed join and is now joined.

**What a node's identity is.** A class is identified by the module that holds its file, its file, its language and its name; the name decides only inside the module. A model document names no file and no language: it describes the module whose folder holds its `.context`, so the class it describes is the one class of that name in a file under that folder, production code before test support, and a document of a folder nearer the file wins over one further up. Where the module declares the name in two files, the document cannot say which it means and its class stays a node of its own, at its card. A member is identified by its class and its name; a model's constructor written as the class's name (`+ Ledger(owner)`) is the code's `__init__` or `constructor`. A DDD aggregate is identified by its folder, and a building block by its aggregate and its name.

**How the saved graph records a node's place in each format.** The node's `source` is the place in the format with the most detail (the code's), and the fact `written_in` keeps each other format's place by the format's name: `{"markdown": [file, first line, last line]}`. A node keeps one place for each format: the first one given, which the reader gives from the document nearest the code, moved only when that same file gives it again, as a refresh of it does. `Node.places` answers every place, its own first, and the graph's `NodeSource.files` answers each file for the file view.
