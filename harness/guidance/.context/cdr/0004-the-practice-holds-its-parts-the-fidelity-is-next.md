# A practice holds its formats, its graph reading and its schema; the fidelity's parts are the next step

The round-9 review (harness core, row 2) found *PracticeGuidance* held five jobs in one class: 70 methods, total complexity 199. Its section comments already marked where the jobs divide. The same review found *FidelityGuidance* at 54 methods and total complexity 138 (row 5).

## What round 9 changed

- **The practice holds three parts, each made once in its constructor.**
  - *PracticeFormats* (`practice.formats`, `practice_formats.py`) makes each adapter once and keeps it, picks the format that reads a file, reads the files a render converts, and turns a *RenderRequest* into output. The cache that was hidden in `vars(self)` is the part's own field, and the disk walk the practice did to render its own code is now a question to the session's files (`session.session_files.find` and `document_named`). A practice whose formats convert in a way of their own names its kind (`formats_type`): DDD's *DddFormats* and Stories' *StoriesFormats*. A model that holds only the classes of the practice a practice extends is read by that practice's formats (`PracticeFormats.parse`).
  - *PracticeReading* (`practice.reading`, `practice_reading.py`) is what the graph talks to: the node-type declarations, `rule_types`, `reads_after`, the graph rules (`graph_checks`, read once in a cached property instead of a field made with `getattr`), and `read()`. The graph hands it the graph and the practice's *PracticeNodes* (`held_in`). Each practice names its kind in `model/graph_reading.py`: Clean Engineering's *GraphReading*, BDD's *BddGraphReading*, DDD's *DddReading*, Stories' *StoriesReading*, UX's *UxReading*. A practice links its nodes to other practices at the end of its own read, after the practices it names in `reads_after`, so the separate link and align hooks are gone: Stories aligns the nodes it records where it records them.
  - *Schema* (`practice.schema`) is read once, and answers its text, its guide, its node fidelities and its errors against the practice's fidelities. The file has one reader.
- **The practice's session output.** The practice's `files()` and `output_paths()` had no caller and only forwarded to its fidelities, which each hold their own *FidelitySessionOutput*; they are deleted. A fidelity's reports and the path of a new report are its session output's (`session_output.reports()`, `new_report_path()`), since that object owns the reports folder.
- *PracticeGuidance* keeps its identity, its words, its fidelities and its set: 29 methods, total complexity 80.

## What stays, and the next step

*FidelityGuidance* is still over the limits (51 methods, total complexity 131). It holds four jobs: its settings and identity; the format it works in and its Clean Engineering companion; its words (templates, examples, instructions, rules); and the files it declares (`outputs`, `declares`, `_declared_files`, `output_paths`, `files`, `has_declared_output`). Round 9 removed its report job and its render request building. The next round takes the declared files into a part the fidelity holds, made from its `outputs`, which *FidelitySessionOutput* already asks for its matches, and the template lookup (`templates`, `templates_in`, `template_file`, `_template_markdown`) into a part held beside it. Round 9 did not do both: they reshape space/session's session output at the same time as the practice split reshaped every graph reader, and the two together could not be merged safely with the other areas' round-9 work.

## Consequences

- Code holding a practice asks `practice.reading.in_graph` for its nodes, `practice.formats` for a format, and `practice.schema` for its schema. Nothing else on the practice answers those.
- A new practice that reads files names a *PracticeReading* subclass; one that only checks rules names none.
