Fidelity: ia / exploration

Corrections from review:
- one tree; rules is a property on Nodes that can have rules
- filters sit top-left in the header strip, not a side column
- left pane is the PracticeGraph tree; right pane is the source file
- selecting a file Node opens that file and highlights the Node's range; a folder Node does not change the right pane
- filters include violations (Nodes with failing rules) and a specific rule
- story map lives in this file, not a second sketch

Source: harness/knowledge_graph/.context/backlog.txt (lines 9–35).
PracticeGraph is the existing seam (module-context.md). Node, Relationship, property, node.rules, violations, and source location (file + range) are the surface terms.

═══════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════

Explore Knowledge Graph
  ├─ [action] selects working folder ────→ Explore Knowledge Graph (scan folder, load tree)
  ├─ [action] selects PracticeGraph ──────→ Explore Knowledge Graph (same screen)
  ├─ [action] selects folder Node ───────→ Explore Knowledge Graph (tree only)
  ├─ [action] selects file Node ─────────→ Explore Knowledge Graph (open source, highlight range)
  ├─ [action] follows Relationship ───────→ Explore Knowledge Graph (focus target Node; open file if the target is a file)
  ├─ [action] opens Node rules property ──→ Explore Knowledge Graph (same screen, rules list on the tree Node)
  └─ [action] filters tree ──────────────→ Explore Knowledge Graph (same screen; practice · connector · node · violations · rule)

Nav tags: [action]

═══════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════

[ Explore Knowledge Graph ]                    top-header + split-screen
  ┌──────────────────────────────────────────────────────────┐
  │ KnowledgeGraph                                           │
  │ folder [ Choose folder ]                                 │  native folder picker
  │ practice · connector · node · violations · rule          │  filters top-left, not a column
  ├────────────────────────────┬─────────────────────────────┤
  │ PracticeGraph tree         │ source file                 │
  │   PracticeGraph A          │ path/to/Customer.ts         │
  │     root Node              │                             │
  │       folder Node          │   export class Customer {   │
  │       › file Node ‹        │   ›   load(id) { … } ‹      │  highlighted range
  │         property : value   │   }                         │
  │         rules              │                             │
  │           slug  passing    │                             │
  │           slug  violating  │                             │
  │         ── Relationship ── │                             │  connector to another Node
  │   PracticeGraph B          │                             │
  │     root Node              │                             │
  └────────────────────────────┴─────────────────────────────┘
  Stories (~4): Browse Practice Graphs · Open Node Source · Follow Relationship · Filter Graph
  Domain terms: KnowledgeGraph · PracticeGraph · Node · Relationship · property · rules · violations · source file · range
  key:
    filters live in the top strip, left side — not a left column
    practice · connector kind · node · violations · rule
    violations = only Nodes with failing rules, plus ancestors so the path stays visible; passing siblings drop out
    rule = only Nodes that have that named rule
    opening rules on a filtered Node lists only the violating rule
    a Node with a violating rule is red; every parent is red too
    (failed / total) sits beside the name at every level — subtree rollup
    left = PracticeGraph tree (each child indented under its parent; classes live in their file/subfolder; a Node's rules sit under a collapsed rules child; hover the icon or name for the Node type: Package · Module · File · Class · Operation · Rule)
    right = source file for the selected file Node; range highlighted
    folder Node: tree selection only; right pane unchanged
    file Node: open file + highlight the Node's selected area
    ›sel‹ selected Node / highlighted range
    on follow Relationship → same screen; if the target is a file, its source opens

═══════════════════════════════════════════════════
  STORY MAP
═══════════════════════════════════════════════════

Explore Knowledge Graph
    Engineer --> Select Working Folder
        selecting a folder scans it into the KnowledgeGraph
            given a folder whose source includes a Node that passes keep-operations-small-focused
                and whose source includes a Node that fails keep-operations-small-focused
            when the Engineer selects that folder
            then the passing Node lists keep-operations-small-focused as passing
                and the failing Node lists keep-operations-small-focused as violating
    Engineer --> Browse Practice Graphs
        KnowledgeGraph lists PracticeGraphs and Nodes
            given a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused
                and whose source includes a Node that fails keep-operations-small-focused
            when the Engineer browses the KnowledgeGraph
            then the passing Node lists keep-operations-small-focused as passing
                and the failing Node lists keep-operations-small-focused as violating
    Engineer --> Open Node Source
        file Node opens source and highlights range
            given a KnowledgeGraph with a file Node that has a source file and range
            when the Engineer selects the file Node
            then the source file is shown
                and the Node range is highlighted
    Engineer --> Follow Relationship
        following a Relationship focuses the target Node
            given a Node with a Relationship to a target Node
            when the Engineer follows the Relationship
            then the target Node is selected
                and the target source file is shown when the target is a file
    Engineer --> Filter Graph
        tree lists only Nodes that match the filters
            given a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused
                and whose source includes a Node that fails keep-operations-small-focused
            when the Engineer filters the KnowledgeGraph using violations
                and using keep-operations-small-focused
            then the failing Node is listed
                and the passing Node is not listed
~> Increment 1: Engineer can explore a KnowledgeGraph: Select Working Folder, Browse Practice Graphs, Open Node Source, Follow Relationship, Filter Graph
