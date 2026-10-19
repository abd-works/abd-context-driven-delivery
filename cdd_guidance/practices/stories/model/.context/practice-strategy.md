# Practice model

`story-model.md` in this folder is the pattern. Clean Engineering, UX, and any other practice model use the same shape. The node names change. The walk does not.

A practice model reads a path into its tree. The path is one file, or a folder of files. A folder uses nested folders for nested nodes, with one file per epic or per story. Every channel uses the same walk. A channel only differs in how the next node is taken out of that path: the next part of a file, or the next folder or file in the tree.

## Key points

- **Callers use the base nodes.** `{Model}Factory.load(path)` takes a file or a folder, chooses the channel from the file type or the files in the folder, and returns the base root. The channel map loads itself.

- **The channel class is the model.** `MarkdownStoryMap` is a `StoryMap`. The tree is not wrapped in a second object for a file format. There is no scanner beside the root, and there is no `parse` / `render` pair that builds a separate canonical tree.

- **The base types own the walk.** `load` stores the path, the channel prepares its cursor (`load_*_content`), then the same child walk runs. A single file stores that file. A folder stores the path-to-content map of the tree: epic folders, then nested epic folders, then one story file per story. A channel does not reimplement that walk.

- **Each node loads its own children.** The owner of a collection walks `while has_more_child: append load_next_child()`. `load_next` takes the shell with `get_next_*_from_file()` in that node's `*_type`, then calls the child's load methods. That read is the next node in the path: a heading in one file, or the next folder or file in the tree. The walk method stays on the node that owns the children.

- **A channel overrides only those reads.** For each node its path contains, the channel implements `has_more_*` and `get_next_*_from_file`. Shared format behavior sits on one channel node (`MarkdownStoryNode`, `JsonStoryNode`, `DiagramStoryNode`, `DrawIOStoryNode`, `MiroStoryNode`, `CodeStoryNode`). Channel classes inherit the domain node and that channel node.

- **A channel stops where its path stops.** If the path has no deeper nodes, that channel's `load_next` returns the node and does not call the deeper loads. Draw.io and Miro stop at stories. A code folder continues through the story file.

- **The copy constructor rebuilds children in this channel.** `Node(source: Node)` copies the node's own fields. Each source child becomes this channel's child type, named by a type slot on the parent (`epic_type`, `story_type`). The new object does not keep the source's channel types.

- **The same concept stays the same type at every depth.** A nested epic is an epic whose parent is an epic. Depth is parentage. A second class for a deeper copy of the same node splits the walk.

- **Channels that share a file shape share a base.** Diagram channels extend the diagram root and the diagram node (`place`, `add`, `stretch`, `role`). Draw.io and Miro add only how a node is written and matched. Code languages extend the code types and override only the reads their language spells differently. A language does not add a type for a node the parent already reads.

- **Every channel saves through the same operation.** The root implements `save(): str`.

## How to write the model context

Write the context in the order the walk visits the nodes, the way `story-model.md` does.

1. One opening paragraph: what the root reads, which channels continue and which stop, and that every channel uses the same walk.
2. The module header: Purpose, Seam (the factory and the base type names), Dependencies.
3. The base types, in walk order. Each type shows the copy constructor, the fields, the public operations, then the private walk: `load_*`, `has_more_*`, `load_next_*`, `get_next_*_from_file`.
4. The channel families. A shared channel node comes first, then the channel root, then each node that overrides a read or a layout. A channel section lists only what that channel adds.
5. A closing paragraph: which family extends which base, where each family stops, and that a channel overrides only `has_more_*` and `get_next_*_from_file` for the nodes its path contains. Name whether that path is one file or a folder of files.

## How to apply it to another practice

1. Name the base root and the nodes in walk order. One type per concept.
2. Put `load`, the child walks, and `save` on those base types. Put `*_type` slots on the parent that builds the child.
3. Add the factory. `load(path)` selects the channel and returns the base root.
4. For each channel, subclass the base nodes. Add one channel node for the helpers every node in that channel uses. Override `load_*_content`, `has_more_*`, and `get_next_*_from_file`. Override `load_next` only to stop the walk.
5. Where several channels share layout or a folder walk, put that on an intermediate base. Languages extend that base.
6. Replace a channel `parse` / `render` pair with the subclass walk. Delete a scanner or a wrapper whose only job was to walk the path beside the model.
7. Write the model context in the shape above before changing the next channel, so the walk stays the contract.
