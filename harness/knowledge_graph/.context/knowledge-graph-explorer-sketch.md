Fidelity: ia / exploration

Corrections from review:
- one tree; rules is a property on Nodes that can have rules
- filters sit top-left in the header strip, not a side column
- left pane is the PracticeGraph tree; right pane is the source file
- selecting a file Node opens that file and highlights the Node's range; a folder Node does not change the right pane
- filters include violations (Nodes with failing rules) and a specific rule
- story map lives at harness/knowledge_graph/app/tests/explore-knowledge-graph/explore-knowledge-graph-story-map.md

Source: harness/knowledge_graph/.context/backlog.txt (lines 9–35).
PracticeGraph is the existing seam (module-context.md). Node, Relationship, property, node.rules, violations, and source location (file + range) are the surface terms.

═══════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════

Explore Knowledge Graph
  ├─ [action] selects repo folder ────────→ Explore Knowledge Graph (load Knowledge Graph)
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
  │ folder [ Repo folder ]                                   │  native folder picker
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
  Stories: Select Working Folder · Browse Practice Graphs · Indent Practice Graph · Name Node Type · Nest Class Folder · Show Disk Packages · Collapse Node Rules · Open Node Source · Follow Relationship · Filter Graph
  Domain terms: KnowledgeGraph · PracticeGraph · Node · Relationship · property · rules · violations · source file · range
  key:
    filters live in the top strip, left side — not a left column
    practice · connector kind · node · violations · rule
    violations = only Nodes with failing rules, plus ancestors so the path stays visible; passing siblings drop out
    rule = only Nodes that have that named rule
    opening rules on a filtered Node lists only the violating rule
    the right pane uses that same filter — only violating rules, including nested operations under a class and nested classes under a folder
    selected Node is blue, distinct from violating red
    a Node with a violating rule is red; every parent is red too
    (failed / total) sits beside the name at every level — subtree rollup
    left = PracticeGraph tree (each child indented under its parent; classes live in their file/subfolder; a Node's rules sit under a collapsed rules child; hover the icon or name for the Node type: Package · Module · File · Class · Operation · Rule)
    right = source for the selected Node (the function, class, or file range); rule problems sit below that excerpt
    folder Node: the right pane lists nested Nodes (classes, operations) and their rules
    operation / class / file Node: open the corresponding source range, then list its rules, then nested children and their rules
    class Node: the whole class body, not only the header line
    operation Node: the whole operation body
    disk Package folders under a Module show even when they are not themselves Modules; classes stay inside those folders
    ›sel‹ selected Node / highlighted range
    on follow Relationship → same screen; if the target is a file, its source opens

═══════════════════════════════════════════════════
  STORY MAP
═══════════════════════════════════════════════════

Explore Knowledge Graph
    Engineer --> Select Working Folder
        selecting a repo folder loads the Knowledge Graph
            given a folder whose source includes a Node that passes keep-operations-small-focused
                and whose source includes a Node that fails keep-operations-small-focused
            when the Engineer selects that folder
            then the passing Node lists keep-operations-small-focused as passing
                and the failing Node lists keep-operations-small-focused as violating
    Browse Practice Graph
        Engineer --> Browse Practice Graphs
            KnowledgeGraph lists PracticeGraphs and Nodes
                given a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused
                    and whose source includes a Node that fails keep-operations-small-focused
                when the Engineer browses the KnowledgeGraph
                then the passing Node lists keep-operations-small-focused as passing
                    and the failing Node lists keep-operations-small-focused as violating
        Engineer --> Indent Practice Graph
            children sit one indent level under their parent
                given a KnowledgeGraph with a parent Node and a child Node
                when the Engineer browses the KnowledgeGraph
                then the child sits one indent level under the parent
        Engineer --> Name Node Type
            hover names the Node type
                given a Package and a Module on the PracticeGraph
                when the Engineer points at the Node icon or name
                then the tooltip names Package
                    and names Module
        Engineer --> Nest Class Folder
            classes sit in their subfolder, not the parent Module
                given Module harness that owns class Guidance under harness/guidance
                when the Engineer opens harness
                then harness children include the guidance folder
                    and do not list Guidance as a direct child
            classless members sit on the package, not a File
                given a package whose file owns a class and a classless operation
                when the Engineer opens that package
                then the package children include the class and the classless operation
                    and do not list the file
                    and do not list a module variable as a Property
        Engineer --> Show Disk Packages
            disk folders show under a Module even when they are only Packages
                given harness with disk folders guidance and mcp
                when the Engineer opens harness
                then those folders are listed
                    and classes stay inside them
        Engineer --> Collapse Node Rules
            rules stay collapsed until the rules Node is opened
                given a Node with applicable rules
                when the Engineer expands that Node without opening rules
                then rule slugs are not listed
                when the Engineer opens the rules child
                then those rules are listed
    Engineer --> Open Node Source
        file Node opens source and highlights range
            given a KnowledgeGraph with a file Node that has a source file and range
            when the Engineer selects the file Node
            then the source file is shown
                and the Node range is highlighted
        class Node shows the whole class
            given a class Node whose graph source is missing or only the header
            when the Engineer selects the class Node
            then the source pane shows the whole class body
                and rule problems sit below that excerpt
        a class pane lists nested operations
            given a class Node that owns operations
            when the Engineer selects the class Node
            then the source pane lists those operations under the class
        operation Node shows the whole operation
            given an operation Node whose graph source is missing or only the header
            when the Engineer selects the operation Node
            then the source pane shows the whole operation
                and not the enclosing class
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
        keep ancestors of a violating Node
            given the same KnowledgeGraph
            when the Engineer filters using violations
            then ancestors of the failing Node remain
                and passing siblings drop out
        then the Node rules list only the violating rule
            given a violating Node with more than one applicable rule
            when the Engineer filters using violations
            then the Node rules list only the violating rule
                and the right pane lists only violating rules
        a folder pane lists nested violating Nodes
            given a violating Node under a parent folder
            when the Engineer filters using violations
            then selecting the folder lists the violating operations underneath
        parents show failed over total and stay red
            given a violating Node under a parent
            when the Engineer filters using violations
            then the failing Node and its parents are red
                and (failed / total) sits beside the name
~> Increment 1: Engineer can explore a KnowledgeGraph: Select Working Folder, Browse Practice Graphs, Open Node Source, Follow Relationship, Filter Graph
~> Increment 2: Engineer can read the tree: Indent Practice Graph, Name Node Type, Nest Class Folder, Show Disk Packages, Collapse Node Rules; class and operation Nodes open whole bodies then rules; violations keep ancestors, list only failing rules, and roll up (failed / total) in red
