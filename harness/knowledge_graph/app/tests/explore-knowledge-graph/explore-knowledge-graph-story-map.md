---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Explore Knowledge Graph

**Sources / context:** harness/knowledge_graph/.context/knowledge-graph-explorer-sketch.md (site map, screens, story map)

---

(E) Explore Knowledge Graph
    (S) Engineer --> Select Working Folder
    (E) Browse Practice Graph
        (S) Engineer --> Browse Practice Graphs
        (S) Engineer --> Indent Practice Graph
        (S) Engineer --> Name Node Type
        (S) Engineer --> Nest Class Folder
        (S) Engineer --> Show Disk Packages
        (S) Engineer --> Collapse Node Rules
    (S) Engineer --> Open Node Source
    (S) Engineer --> Follow Relationship
    (S) Engineer --> Filter Graph

---

## Scope boundary

**In scope:** Engineer loads a repo folder into a KnowledgeGraph, browses the PracticeGraph tree, opens Node source, follows a Relationship, and filters by practice · connector · node · violations · rule.

**Out of scope:** writing or repairing rules, CodeQL database build UX, branding besides the explorer chrome already on the screen.
