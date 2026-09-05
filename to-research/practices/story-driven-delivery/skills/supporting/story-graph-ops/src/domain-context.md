---
generating-skill: abd-domain-specification
---

# Module: Story Map Diagram Sync

Scope: Three-layer class hierarchy enabling any StoryNode to translate to/from any
representation (Markdown, JSON, DrawIO, Miro) via a common interface, with reversible
change recording.

---

# Core Domain

## **Story Hierarchy**

The fixed translation algorithm lives entirely on `StoryNode`. Every subclass extends
two abstract methods — `updateSelf` and `childCollections` — and one factory method per
child type it produces. `translateFrom` itself is never overridden.

### **StoryNode** << abstract >>

+ StoryNode(name: NodeName, sequentialOrder: Integer)
------
+ name: NodeName
+ sequentialOrder: Integer
+ behavior: FreeText
+ << composition >> snapshot: NodeSnapshot
----
+ translateFrom(source: StoryNode): UpdateReport
	Invariant: source must be the same semantic type as self
	Interaction:
		report: UpdateReport = new UpdateReport()
		report.captureSnapshot(self)
		self.updateSelf(source)
		pairs: List<ChildCollectionPair> = self.childCollections(source)
		for pair in pairs:
			self.reconcileCollection(pair, report)
		return report

- reconcileCollection(pair: ChildCollectionPair, report: UpdateReport): void
	Interaction:
		for sourceChild in pair.sourceChildren:
			match: StoryNode = self.findMatch(sourceChild.name, sourceChild.sequentialOrder, pair.selfChildren)
			if match exists:
				match.translateFrom(sourceChild)
				report.addExactMatch(match.name, sourceChild.name)
			else:
				newChild: StoryNode = pair.createChild(sourceChild)
				pair.selfChildren.add(newChild)
				newChild.translateFrom(sourceChild)
				report.addNew(newChild)
		for selfChild in pair.selfChildren not matched:
			pair.selfChildren.remove(selfChild)
			report.addRemoved(selfChild)

- findMatch(name: NodeName, order: Integer, candidates: List<StoryNode>): StoryNode
	Invariant: returns the candidate whose name or sequentialOrder matches; returns null if none match

+ updateSelf(source: StoryNode): void
	Invariant: abstract — reads type-specific properties from source and writes them to self

+ childCollections(source: StoryNode): List<ChildCollectionPair>
	Invariant: abstract — returns ordered list of ChildCollectionPair instances to reconcile; order of pairs determines recursion order

+ reverse(report: UpdateReport): void
	Invariant: must be called on the node that produced the report
	Interaction:
		report.reverseOn(self)

### **Epic : StoryNode** << Entity >>

+ Epic(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> domainConcepts: List<DomainConcept>
+ << composition >> subEpics: List<SubEpic>
----
+ updateSelf(source: Epic): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.domainConcepts = source.domainConcepts

+ childCollections(source: Epic): List<ChildCollectionPair>
	Interaction:
		subEpicPair: ChildCollectionPair = new ChildCollectionPair(
			selfChildren: self.subEpics,
			sourceChildren: source.subEpics,
			createChild: self.createChildSubEpic
		)
		return [subEpicPair]

+ createChildSubEpic(source: SubEpic): SubEpic
	Invariant: returns a new SubEpic instance of the correct concrete type for this node's format

### **SubEpic : StoryNode** << Entity >>

+ SubEpic(name: NodeName, sequentialOrder: Integer)
------
+ hasSubEpics: Boolean
+ testFile: FilePath
+ << composition >> domainConcepts: List<DomainConcept>
+ << composition >> subEpics: List<SubEpic>
+ << composition >> stories: List<Story>
----
+ updateSelf(source: SubEpic): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.hasSubEpics = source.hasSubEpics
		self.testFile = source.testFile
		self.domainConcepts = source.domainConcepts

+ childCollections(source: SubEpic): List<ChildCollectionPair>
	Invariant: sub-epics reconciled before stories so depth is known before story rows are positioned
	Interaction:
		subEpicPair: ChildCollectionPair = new ChildCollectionPair(
			selfChildren: self.subEpics,
			sourceChildren: source.subEpics,
			createChild: self.createChildSubEpic
		)
		storyPair: ChildCollectionPair = new ChildCollectionPair(
			selfChildren: self.stories,
			sourceChildren: source.stories,
			createChild: self.createChildStory
		)
		return [subEpicPair, storyPair]

+ createChildSubEpic(source: SubEpic): SubEpic
	Invariant: returns a new SubEpic instance of the correct concrete type for this node's format

+ createChildStory(source: Story): Story
	Invariant: returns a new Story instance of the correct concrete type for this node's format

+ allStoriesRecursive(): List<Story>
	Interaction:
		result: List<Story> = []
		for subEpic in self.subEpics:
			result.addAll(subEpic.allStoriesRecursive())
		result.addAll(self.stories)
		return result

### **Story : StoryNode** << Entity >>

+ Story(name: NodeName, sequentialOrder: Integer, storyType: StoryType)
------
+ storyType: StoryType
	Invariant: one of user | system | technical; affects styling only, not structure
+ << composition >> users: List<StoryUser>
+ << composition >> acceptanceCriteria: List<AcceptanceCriteria>
----
+ updateSelf(source: Story): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.storyType = source.storyType
		self.users = source.users

+ childCollections(source: Story): List<ChildCollectionPair>
	Interaction:
		acPair: ChildCollectionPair = new ChildCollectionPair(
			selfChildren: self.acceptanceCriteria,
			sourceChildren: source.acceptanceCriteria,
			createChild: self.createChildAcceptanceCriteria
		)
		return [acPair]

+ createChildAcceptanceCriteria(source: AcceptanceCriteria): AcceptanceCriteria
	Invariant: returns a new AcceptanceCriteria instance of the correct concrete type for this node's format

### **AcceptanceCriteria : StoryNode** << Entity >>

+ AcceptanceCriteria(criteriaText: CriteriaText, sequentialOrder: Integer)
------
+ criteriaText: CriteriaText
----
+ updateSelf(source: AcceptanceCriteria): void
	Interaction:
		self.criteriaText = source.criteriaText
		self.sequentialOrder = source.sequentialOrder

+ childCollections(source: AcceptanceCriteria): List<ChildCollectionPair>
	Interaction:
		return []

### **ChildCollectionPair** << ValueObject >>

Initialisation: constructed inline inside each node's `childCollections` call
------
+ selfChildren: List<StoryNode>
+ sourceChildren: List<StoryNode>
+ createChild: Callable<StoryNode, StoryNode>
	Invariant: bound to the parent node's createChildXxx method for this child type

### references

**Ref — story_graph_ops/nodes.py**
Source: `skills/supporting/story-graph-ops/scripts/story_graph_ops/nodes.py`
Locator: StoryNode, Epic, SubEpic, Story
Extract: whole

### decisions made

- `translateFrom` algorithm is fixed on `StoryNode` and never overridden — only `updateSelf`, `childCollections`, and `createChildXxx` are extension points
- `NodeSnapshot` is captured at the start of `translateFrom` before `updateSelf` runs — this preserves the complete before-state for reversal; the snapshot recurses into children so a full tree snapshot is available
- `ChildCollectionPair.createChild` is bound to `self.createChildXxx` at the call site inside `childCollections` — the reconcile loop stays generic; type resolution lives entirely in the factory methods
- Each concrete class overrides `createChildXxx` per child type it produces; the domain layer returns plain subtypes; the backend layer returns format-specific subtypes (e.g. `DrawIOEpic.createChildSubEpic` returns `DrawIOSubEpic`)
- `StoryType` is not a subtype candidate — it is a constrained enum (`user | system | technical`) that affects styling rules only

---

## **Format: Diagram**

Diagram backends need two sub-layers: `DiagramStoryNode` computes positioning from
declarative layout rules; `DrawIOStoryNode` and `MiroStoryNode` hold the backend element
and serialize to it. All three layers stack via multiple inheritance (Python MRO /
TypeScript mixins). Non-diagram formats skip both sub-layers entirely.

### Diagram Layer (shared across all diagram backends)

`DiagramStoryNode` extends the `updateSelf` extension point to add positioning — all
other parts of the `translateFrom` algorithm are inherited unchanged. `childCollections`
and `createChildXxx` are re-overridden by each concrete diagram class to return
diagram-typed children.

### **DiagramStoryNode : StoryNode** << abstract >>

+ DiagramStoryNode(name: NodeName, sequentialOrder: Integer)
------
----
+ position(): Position
	Interaction:
		return self.element.position()

+ boundary(): Boundary
	Interaction:
		return self.element.boundary()

+ containmentRules(): ContainmentRule
	Invariant: abstract — subclass declares allowed parents and allowed child types

+ placementRules(): PlacementRule
	Invariant: abstract — subclass declares y-offset strategy, height, and width strategy

+ formattingRules(): FormattingRule
	Invariant: abstract — subclass declares fill, stroke, font, and shape key

+ updateSelf(source: StoryNode): void
	Invariant: extends super.updateSelf — also updates position and boundary
	Interaction:
		super.updateSelf(source)
		rows: RowPositions = new RowPositions(self.maxSubEpicDepth(source))
		placement: PlacementRule = self.placementRules()
		self.setPosition(placement.x, rows.yFor(self))
		self.setSize(placement.width, placement.height)
		self.applyFormatting(self.formattingRules())

- maxSubEpicDepth(root: StoryNode): Integer
	Invariant: counts the maximum nesting depth of SubEpic nodes under root; used to compute RowPositions

+ setPosition(x: Float, y: Float): void
	Invariant: abstract — delegates to backend element

+ setSize(width: Float, height: Float): void
	Invariant: abstract — delegates to backend element

+ applyFormatting(rules: FormattingRule): void
	Invariant: abstract — delegates to backend element

### **DiagramEpic : Epic, DiagramStoryNode** << abstract >>

------
+ containmentRules(): ContainmentRule
	Invariant: no allowed parents; contains sub-epics only; does not directly contain stories

+ placementRules(): PlacementRule
	Invariant: y fixed at EPIC_Y; height fixed at EPIC_HEIGHT; width spans all child sub-epics

+ formattingRules(): FormattingRule

+ createChildSubEpic(source: SubEpic): DiagramSubEpic
	Invariant: abstract — concrete diagram class returns the correct DiagramSubEpic subtype

### **DiagramSubEpic : SubEpic, DiagramStoryNode** << abstract >>

------
+ containmentRules(): ContainmentRule
	Invariant: parent must be DiagramEpic or DiagramSubEpic; may contain sub-epics and stories

+ placementRules(): PlacementRule
	Invariant: y = RowPositions.subEpicY(depth); height fixed at SUB_EPIC_HEIGHT; width spans children

+ createChildSubEpic(source: SubEpic): DiagramSubEpic
	Invariant: abstract — concrete diagram class returns the correct DiagramSubEpic subtype

+ createChildStory(source: Story): DiagramStory
	Invariant: abstract — concrete diagram class returns the correct DiagramStory subtype

### **DiagramStory : Story, DiagramStoryNode** << abstract >>

------
+ containmentRules(): ContainmentRule
	Invariant: parent must be DiagramSubEpic; contains nothing; leaf node

+ placementRules(): PlacementRule
	Invariant: fixed CELL_SIZE × CELL_SIZE; stories laid out left-to-right within sub-epic column

+ createChildAcceptanceCriteria(source: AcceptanceCriteria): AcceptanceCriteria
	Invariant: abstract — concrete diagram class returns the correct AcceptanceCriteria subtype

### **RowPositions** << ValueObject >>

+ RowPositions(maxDepth: Integer)
------
+ maxDepth: Integer
----
+ subEpicY(depth: Integer): Float
	Interaction:
		return EPIC_Y + EPIC_HEIGHT + ROW_GAP + (depth * (SUB_EPIC_HEIGHT + ROW_GAP))

+ actorY(): Float
	Interaction:
		return self.subEpicY(self.maxDepth) + SUB_EPIC_HEIGHT + ACTOR_GAP

+ storyY(): Float
	Interaction:
		return self.actorY() + CELL_SIZE + ROW_GAP

+ yFor(node: DiagramStoryNode): Float
	Invariant: dispatches to the correct row based on node type (epic → EPIC_Y, sub-epic → subEpicY, story → storyY)
	Interaction:
		if node is DiagramEpic: return EPIC_Y
		if node is DiagramSubEpic: return self.subEpicY(node.depth)
		if node is DiagramStory: return self.storyY()

### references

**Ref — lib/diagram_story_sync**
Source: `lib/diagram_story_sync/diagram_story_node.py`, `layout_constants.py`
Locator: DiagramStoryNode, DiagramEpic, DiagramSubEpic, DiagramStory, RowPositions
Extract: whole

### decisions made

- `DiagramStoryNode.updateSelf` calls `super.updateSelf(source)` first, then adds positioning — this ensures name and type-specific fields are written before geometry is computed
- `RowPositions` is a `ValueObject` — it has no identity; two `RowPositions` with the same `maxDepth` are interchangeable; it is constructed fresh inside each `DiagramStoryNode.updateSelf` call
- `yFor(node)` dispatches by node type rather than carrying depth as a property on every node — depth is computed on demand from the tree structure via `maxSubEpicDepth`

---

### Backend Mixins + Concrete Classes (DrawIO and Miro)

`DrawIOStoryNode` and `MiroStoryNode` each hold their backend element by composition,
implement the three abstract geometry methods from `DiagramStoryNode` by delegating to
the element, and extend `updateSelf` to serialize after positioning.

### **DrawIOStoryNode : DiagramStoryNode** << abstract >>

Mixin — combined with a concrete `DiagramXxx` class via multiple inheritance.

+ DrawIOStoryNode(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> element: DrawIOElement
	Invariant: created in the concrete constructor (e.g. DrawIOEpic); never replaced
+ cellId: CellId
----
+ position(): Position
	Interaction: return self.element.position()

+ boundary(): Boundary
	Interaction: return self.element.boundary()

+ setPosition(x: Float, y: Float): void
	Interaction: self.element.setPosition(x, y)

+ setSize(width: Float, height: Float): void
	Interaction: self.element.setSize(width, height)

+ applyFormatting(rules: FormattingRule): void
	Interaction: self.element.applyStyleForType(rules.styleKey)

+ updateSelf(source: StoryNode): void
	Invariant: extends super.updateSelf — adds serialization to element after positioning
	Interaction:
		super.updateSelf(source)
		self.element.setValue(self.name.value)
		self.element.applyStyleForType(self.formattingRules().styleKey)

+ collectAllNodes(): List<DrawIOStoryNode>
	Interaction:
		result = [self]
		for pair in self.childCollections(self):
			for child in pair.selfChildren:
				result.addAll(child.collectAllNodes())
		return result

### **MiroStoryNode : DiagramStoryNode** << abstract >>

Mixin — combined with a concrete `DiagramXxx` class via multiple inheritance.
Identical pattern to `DrawIOStoryNode`; element is `MiroElement` instead of `DrawIOElement`.

+ MiroStoryNode(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> element: MiroElement
	Invariant: created in the concrete constructor; never replaced
+ cellId: CellId
----
+ position(): Position
	Interaction: return self.element.position()

+ boundary(): Boundary
	Interaction: return self.element.boundary()

+ setPosition(x: Float, y: Float): void
	Interaction: self.element.setPosition(x, y)

+ setSize(width: Float, height: Float): void
	Interaction: self.element.setSize(width, height)

+ applyFormatting(rules: FormattingRule): void
	Interaction: self.element.applyStyleForType(rules.styleKey)

+ updateSelf(source: StoryNode): void
	Invariant: extends super.updateSelf — adds serialization to element after positioning
	Interaction:
		super.updateSelf(source)
		self.element.setValue(self.name.value)
		self.element.applyStyleForType(self.formattingRules().styleKey)

### **DrawIOEpic : DiagramEpic, DrawIOStoryNode** << Entity >>

+ DrawIOEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): DrawIOSubEpic
	Interaction:
		return new DrawIOSubEpic(name: source.name, sequentialOrder: source.sequentialOrder)

### **DrawIOSubEpic : DiagramSubEpic, DrawIOStoryNode** << Entity >>

+ DrawIOSubEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): DrawIOSubEpic
	Interaction:
		return new DrawIOSubEpic(name: source.name, sequentialOrder: source.sequentialOrder)

+ createChildStory(source: Story): DrawIOStory
	Interaction:
		return new DrawIOStory(name: source.name, sequentialOrder: source.sequentialOrder, storyType: source.storyType)

### **DrawIOStory : DiagramStory, DrawIOStoryNode** << Entity >>

+ DrawIOStory(name: NodeName, sequentialOrder: Integer, storyType: StoryType)
------
----
+ createChildAcceptanceCriteria(source: AcceptanceCriteria): DrawIOAcceptanceCriteria
	Interaction:
		return new DrawIOAcceptanceCriteria(criteriaText: source.criteriaText, sequentialOrder: source.sequentialOrder)

### **MiroEpic : DiagramEpic, MiroStoryNode** << Entity >>

+ MiroEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): MiroSubEpic
	Interaction:
		return new MiroSubEpic(name: source.name, sequentialOrder: source.sequentialOrder)

### **MiroSubEpic : DiagramSubEpic, MiroStoryNode** << Entity >>

+ MiroSubEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): MiroSubEpic
	Interaction:
		return new MiroSubEpic(name: source.name, sequentialOrder: source.sequentialOrder)

+ createChildStory(source: Story): MiroStory
	Interaction:
		return new MiroStory(name: source.name, sequentialOrder: source.sequentialOrder, storyType: source.storyType)

### **MiroStory : DiagramStory, MiroStoryNode** << Entity >>

+ MiroStory(name: NodeName, sequentialOrder: Integer, storyType: StoryType)
------
----
+ createChildAcceptanceCriteria(source: AcceptanceCriteria): MiroAcceptanceCriteria
	Interaction:
		return new MiroAcceptanceCriteria(criteriaText: source.criteriaText, sequentialOrder: source.sequentialOrder)

### references

**Ref — DrawIO backend**
Source: `skills/supporting/drawio-story-sync/scripts/drawio_story_sync/drawio_story_node.py`
Locator: DrawIOStoryNode, DrawIOEpic, DrawIOSubEpic, DrawIOStory
Extract: whole

**Ref — Miro backend**
Source: `skills/supporting/miro-story-sync/scripts/miro_story_sync/miro_story_node.py`
Locator: MiroStoryNode, MiroEpic, MiroSubEpic, MiroStory
Extract: whole

### decisions made

- There is no `BackendStoryNode` class — `DrawIOStoryNode` and `MiroStoryNode` are the real Layer 3 mixins; they share the same delegation pattern but not a common superclass
- `DrawIOStoryNode.updateSelf` and `MiroStoryNode.updateSelf` both call `super.updateSelf` (which handles domain fields + positioning) then serialize to their element — three layers stack cleanly: field copy → positioning → serialization
- `createChildXxx` on each concrete backend class constructs the new child with only the data available from `source` at creation time; `translateFrom` is called on the new child immediately after, filling in all remaining fields via `updateSelf`
- `DrawIOElement` and `MiroElement` are created inside the concrete node's constructor — the node owns the element's lifecycle (composition)

---

## **Format: Documents**

Document formats (Markdown, JSON) read or write story structure as text or data.
They do **not** need positioning — there is no canvas — so they extend `StoryNode`
directly, skipping `DiagramStoryNode` entirely.

### Pattern

```
DocumentStoryNode : StoryNode   (abstract mixin per format)
  updateSelf(source)
    → reads/writes format-specific text or data fields
    → no setPosition / setSize / applyFormatting
```

### **MarkdownStoryNode : StoryNode** << abstract >>

Mixin for Markdown source adapter. Parses heading hierarchy into story nodes.

+ updateSelf(source: StoryNode): void
	Invariant: reads source.name and source.sequentialOrder; writes Markdown heading line

### **MarkdownEpic : Epic, MarkdownStoryNode** << Entity >>
### **MarkdownSubEpic : SubEpic, MarkdownStoryNode** << Entity >>
### **MarkdownStory : Story, MarkdownStoryNode** << Entity >>

### **JsonStoryNode : StoryNode** << abstract >>

Mixin for JSON (story-graph.json) serialization and deserialization.

+ updateSelf(source: StoryNode): void
	Invariant: reads source fields; writes to JSON node representation

### **JsonEpic : Epic, JsonStoryNode** << Entity >>
### **JsonSubEpic : SubEpic, JsonStoryNode** << Entity >>
### **JsonStory : Story, JsonStoryNode** << Entity >>

---

## **Format: Code**

Code formats (TypeScript, Java, Python) generate or parse typed source files from the
story structure. Like document formats, they extend `StoryNode` directly — no positioning
layer needed. Unlike document formats, all code backends share a common abstract sub-layer
(`CodeStoryNode`) that loads and wraps a language-specific AST. Language-specific mixins
then provide the concrete AST implementation.

### Pattern

```
CodeStoryNode : StoryNode          ← shared abstract; holds LanguageAst by composition
  ast: LanguageAst                 ← abstract; provided by language mixin constructor
  updateSelf(source)
    → reads source fields
    → writes to / reads from ast via common AstNode interface

TypeScriptStoryNode : CodeStoryNode   ← mixin; ast = TypeScriptAst
JavaStoryNode       : CodeStoryNode   ← mixin; ast = JavaAst
PythonStoryNode     : CodeStoryNode   ← mixin; ast = PythonAst

TypeScriptEpic : Epic, TypeScriptStoryNode   ← concrete
```

### **CodeStoryNode : StoryNode** << abstract >>

Shared sub-layer for all code backends. Parallel to `DiagramStoryNode` — adds AST
loading and wrapping without knowing which language is in use.

+ CodeStoryNode(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> ast: LanguageAst
	Invariant: abstract — provided by the language mixin at construction time; never replaced
----
+ updateSelf(source: StoryNode): void
	Invariant: abstract — reads source fields; reads/writes language-agnostic structure via ast

### **TypeScriptStoryNode : CodeStoryNode** << abstract >>

+ TypeScriptStoryNode(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> ast: TypeScriptAst
----
+ updateSelf(source: StoryNode): void
	Invariant: extends super — also writes TypeScript-specific node structure (interfaces, describe blocks)

### **TypeScriptEpic : Epic, TypeScriptStoryNode** << Entity >>
### **TypeScriptSubEpic : SubEpic, TypeScriptStoryNode** << Entity >>
### **TypeScriptStory : Story, TypeScriptStoryNode** << Entity >>

### **JavaStoryNode : CodeStoryNode** << abstract >>
### **PythonStoryNode : CodeStoryNode** << abstract >>

---

## **Translation Result**

### **UpdateReport** << Entity >>

+ UpdateReport()
------
+ << composition >> changes: List<Change>
+ << composition >> snapshot: NodeSnapshot
----
+ captureSnapshot(node: StoryNode): void
	Invariant: must be called before any updateSelf or reconcileCollection runs
	Interaction:
		self.snapshot = NodeSnapshot.of(node)

+ addExactMatch(selfName: NodeName, sourceName: NodeName): void
+ addRename(fromName: NodeName, toName: NodeName, confidence: Float): void
+ addNew(node: StoryNode): void
+ addRemoved(node: StoryNode): void
+ addSubEpicSiblingReorder(a: NodeName, b: NodeName): void
+ addStoryGroupReorder(a: NodeName, b: NodeName): void

+ reverseOn(node: StoryNode): void
	Invariant: restores node to the state captured in snapshot; must be called on the node that produced this report
	Interaction:
		self.snapshot.restoreInto(node)

### **NodeSnapshot** << ValueObject >>

+ NodeSnapshot(name: NodeName, sequentialOrder: Integer, childSnapshots: List<NodeSnapshot>)
------
+ name: NodeName
+ sequentialOrder: Integer
+ << composition >> childSnapshots: List<NodeSnapshot>
----
+ restoreInto(node: StoryNode): void
	Invariant: writes snapshot values back to node; recurses into child nodes by position
	Interaction:
		node.name = self.name
		node.sequentialOrder = self.sequentialOrder
		for i, childSnapshot in enumerate(self.childSnapshots):
			childSnapshot.restoreInto(node.children()[i])

+ of(node: StoryNode): NodeSnapshot
	Invariant: static factory — captures current state of node and all descendants recursively
	Interaction:
		childSnapshots: List<NodeSnapshot> = [NodeSnapshot.of(child) for child in node.children()]
		return new NodeSnapshot(name: node.name, sequentialOrder: node.sequentialOrder, childSnapshots: childSnapshots)

### references

**Ref — story_graph_ops/update_report.py**
Source: `skills/supporting/story-graph-ops/scripts/story_graph_ops/update_report.py`
Locator: UpdateReport and associated entry types
Extract: whole

### decisions made

- `UpdateReport` is an Entity — it has identity (the specific translation run that produced it); two reports over the same node are not interchangeable
- `NodeSnapshot` is a ValueObject — it is defined entirely by its captured values; immutable once created
- `captureSnapshot` must be the first call inside `translateFrom` to guarantee the before-state is clean; any write before snapshot risks losing reversal fidelity

---

# Boundary Domain

### **LanguageAst** << abstract >>

Holds a parsed or generated AST for one language. Owned by composition inside
`CodeStoryNode`; the node delegates all language-specific read/write operations to it.

------
----
+ parse(source: CodeString): void
	Invariant: populates the internal AST from raw source code
+ generate(): CodeString
	Invariant: serializes the internal AST back to source code
+ nodeFor(name: NodeName): AstNode
	Invariant: returns the AST node matching the given story node name; null if not found

### **TypeScriptAst : LanguageAst** << Entity >>

+ toInterface(): CodeString
+ toDescribeBlock(): CodeString

### **JavaAst : LanguageAst** << Entity >>
### **PythonAst : LanguageAst** << Entity >>

---

### **BackendElement** << abstract >>

Initialisation: constructed inside the owning BackendStoryNode constructor; never replaced
------
+ cellId: CellId
+ value: FreeText
----
+ position(): Position
+ boundary(): Boundary
+ setPosition(x: Float, y: Float): void
+ setSize(width: Float, height: Float): void
+ setValue(text: FreeText): void
+ applyStyleForType(styleKey: StyleKey): void

### **DrawIOElement : BackendElement** << Entity >>

------
+ toXml(): XmlString
	Invariant: must produce valid DrawIO mxCell XML

### **MiroElement : BackendElement** << Entity >>

------
+ toApiPayload(): JsonPayload
	Invariant: must produce valid Miro v2 items API JSON

### references

**Ref — DrawIO element**
Source: `skills/supporting/drawio-story-sync/scripts/drawio_story_sync/drawio_element.py`
Locator: DrawIOElement
Extract: whole

**Ref — Miro element**
Source: `skills/supporting/miro-story-sync/scripts/miro_story_sync/miro_element.py`
Locator: MiroElement
Extract: whole

### decisions made

- `BackendElement` is Boundary Domain — it knows about XML attributes and Miro API shapes; it knows nothing about story hierarchy rules or positioning logic
- `BackendElement` is held by composition inside `BackendStoryNode` — the element's lifecycle is owned by the node; the element is never shared between nodes
