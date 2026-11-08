# Practice model

`story-model.md` in this folder is the pattern for a practice model: one tree of graph nodes, and one subclass of the root per format. Clean Engineering (`clean_engineering/model/.context/ooad-model.md`) and UX (`ux/model/.context/ux-model.md`) use the same shape with their own node names.

## Key points

- **The format class is the model.** `MarkdownStoryModel` is a `StoryModel`; `JsonUxMap` is a `UxMap`. The tree is not wrapped in a second object for a file format, and there is no scanner beside the root. Each practice lists its format classes under `formats` on its `PracticeGuidance` (`Stories`, `Ux`), so `render(format, content)` finds them by name.

- **Every format reads and writes through the same operations.** `parse(text)` reads text in that format into a new model of its class; `render(model)` writes a model in that format. Stories formats also take the previous text, so a code format keeps the code already written for nodes that did not change. A format that is drawn from the model and edited elsewhere — the Claude Design canvas and screens — raises from `parse` instead of guessing.

- **Callers reach a format by name.** `render(format, content)` on the practice finds the format class among its `formats` and reads or writes through it, so there is no second way to pick a format from a file's type. `Stories.read_folder(folder)` and `Stories.read_files(files, project)` read story maps and story tests through the practice's own formats. A UX format reads its own file from a folder with `from_workspace(root)`.

- **The copy constructor rebuilds children in this format.** `StoryModel(source)` copies the source's epics and increments into this format's node types, named by a type field on the parent (`epic_type`, `story_type`, `increment_type`, and `scenario_type` on a story). The new model does not keep the source's format types. That is how `render(canonical)` converts: it copies the canonical model into its own class, then writes.

- **The same concept stays the same type at every depth.** A nested epic is an epic whose parent is an epic. Depth is parentage. A second class for a deeper copy of the same node splits every walk over the tree.

- **A format stops where its file stops.** Draw.io and Miro story maps stop at stories and still read increments. A code folder continues through scenarios, steps, and their code. A draw.io UX map stops at regions; markdown UX carries only the scope and the context.

- **Formats that share a file shape share a base.** Diagram story formats extend `DiagramStoryModel` and the diagram node (`place`, `add`, `stretch`, `role`); draw.io and Miro add only how a node is written and matched. Code languages extend `CodeStoryModel` and override only the spelling their language writes differently; TypeScript and JavaScript share `BraceStoryModel`.

- **A file walk lives on the node that owns the children.** Clean Engineering reads a file node by node: the owner of a collection runs `while has_more_*: append(load_next_*())`, and a format overrides only `has_more_*` and `get_next_*_from_file` for the nodes its file contains. Stories and UX read a whole file in `parse`, with a reader class beside the format (`JsonUxMapReader`, `StoryReader`) when the reading takes several steps.

## How to write the model context

Write the context in the order the tree is read, the way `story-model.md` does.

1. One opening paragraph: what the root holds, which formats carry the whole tree and which stop early.
2. The module header: Purpose, Seam (the factory and the base type names), Dependencies.
3. The base types, root first. Each type shows its constructor, its fields, then its public operations.
4. The formats. A shared base comes first (diagram, code), then each format root, then each node a format adds. A format section lists only what that format adds.
