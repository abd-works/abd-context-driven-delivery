---
generating-skill: abd-domain-specification
---

# Module: Story Model

Scope: Story Model — `StoryNode` hierarchy enabling any node to translate to/from any
representation (Markdown, JSON, DrawIO, Miro, TypeScript, Python, Java, JavaScript) via
a common interface, with reversible change recording. The full tree hierarchy is
`StoryMap → Epic → SubEpic → Story → Scenario`, with `Increment` sitting alongside
`Epic` as a second direct child of `StoryMap`. Every format implements seven concrete
StoryNode subtypes: `<Format>StoryMap`, `<Format>Epic`, `<Format>SubEpic`,
`<Format>Story`, `<Format>Scenario`, `<Format>Increment` (Code delegates Increment to
Markdown), plus one abstract `<Format>StoryNode` mixin. The model is self-contained:
`Story` composes `Scenario` (reconciled as tree children); `SubEpic` owns
`testSuites: List<TestSuite>` (one per tier, tagged with `Tier` and `Language`);
`StoryMap` owns `increments: List<Increment>`. Test suites, test cases, and tests are
populated by scanners and never transformed across languages. Scanners receive a
`Workspace` that is a thin facade over the already-populated model.

---

# Core Domain

## **Story Map**

The fixed translation algorithm lives entirely on `StoryNode`. Every subclass extends
two abstract methods — `updateSelf` and `childCollections` — and one factory method per
child type it produces. `translateFrom` itself is never overridden.

The full tree is `StoryMap → Epic → SubEpic → Story → Scenario`, with `Increment` as a
second direct child of `StoryMap` alongside `Epic`. `Scenario` and `Increment` are
`StoryNode` leaves — their clauses / interactions (Scenario) and story-name lists
(Increment) are value fields copied in `updateSelf`, not reconciled as tree children.
All formats — Markdown, JSON, DrawIO, Miro, and every code language — implement the
full tree; diagram formats scope which child pair a view walks via `DiagramView` rather
than overriding `childCollections` at the node level.

### **StoryNode** << abstract >>

Class variable `_semanticTypeName: String` — declared on every concrete class; guards
cross-format translation inside `translateFrom`.

+ StoryNode(name: NodeName, sequentialOrder: Integer)
------
+ name: NodeName
+ sequentialOrder: Integer
+ source: Optional<SourceLocation>
	Invariant: set by format loaders after parsing; null during construction
----
+ semanticType(): String
	Interaction:
		return self._semanticTypeName

+ translateFrom(source: StoryNode): UpdateReport
	Invariant: source must have the same semanticType as self; raises TranslationError otherwise
	Interaction:
		if self.semanticType() != source.semanticType():
			raise TranslationError
		report: UpdateReport = new UpdateReport()
		report.captureSnapshot(self)
		self.updateSelf(source)
		pairs: List<ChildCollectionPair> = self.childCollections(source)
		for pair in pairs:
			self._reconcileCollection(pair, report)
		return report

- _reconcileCollection(pair: ChildCollectionPair, report: UpdateReport): void
	Invariant: mutates pair.selfChildren in-place via slice assignment so changes persist on the owning node
	Interaction:
		consumedIds: Set<ObjectId> = {}
		reconciled: List<StoryNode> = []
		for sourceChild in pair.sourceChildren:
			match = self._findMatch(sourceChild, pair.selfChildren, consumedIds)
			if match exists:
				oldName = match.name
				consumedIds.add(id(match))
				match.translateFrom(sourceChild)
				reconciled.add(match)
				if oldName == sourceChild.name:
					report.addExactMatch(match.name, sourceChild.name)
				else:
					report.addRename(oldName, sourceChild.name, confidence=1.0)
			else:
				newChild = pair.createChild(sourceChild)
				newChild.translateFrom(sourceChild)
				reconciled.add(newChild)
				report.addNew(newChild, parentName=self.name)
		for existing in pair.selfChildren not in consumedIds:
			report.addRemoved(existing, parentName=self.name)
		detect first position change between reconciled and prior kept order → report.addReorder
		pair.selfChildren[:] = reconciled

- _findMatch(sourceChild: StoryNode, candidates: List<StoryNode>, consumedIds: Set<ObjectId>): StoryNode
	Invariant: name match takes priority over sequentialOrder; excludes already-consumed candidates; returns null if none match
	Interaction:
		pass 1 — scan candidates for name == sourceChild.name (skip consumed)
		pass 2 — scan candidates for sequentialOrder == sourceChild.sequentialOrder (skip consumed)
		return null

+ updateSelf(source: StoryNode): void
	Invariant: abstract — reads type-specific properties from source and writes them to self

+ childCollections(source: StoryNode): List<ChildCollectionPair>
	Invariant: abstract — returns ordered list of ChildCollectionPair instances; order determines recursion order

+ children(): List<StoryNode>
	Invariant: returns all direct children by calling childCollections(self); used by NodeSnapshot to walk the tree
	Interaction:
		result: List<StoryNode> = []
		for pair in self.childCollections(self):
			result.addAll(pair.selfChildren)
		return result

+ snapshotFields(): dict
	Invariant: returns type-specific fields to include in NodeSnapshot; base returns {}; leaf subclasses override

+ restoreSnapshotFields(fields: dict): void
	Invariant: writes each field back onto self via attribute assignment; base handles all overrides generically

+ reverse(report: UpdateReport): void
	Invariant: delegates to report; report guards against foreign calls via owningNodeId
	Interaction:
		report.reverseOn(self)

### **Epic : StoryNode** << Entity >>

+ Epic(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> domainConcepts: List<String>
+ << composition >> subEpics: List<SubEpic>
----
+ updateSelf(source: Epic): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.domainConcepts = copy(source.domainConcepts)

+ childCollections(source: Epic): List<ChildCollectionPair>
	Interaction:
		return [ChildCollectionPair(self.subEpics, source.subEpics, self.createChildSubEpic)]

+ createChildSubEpic(source: SubEpic): SubEpic
	Invariant: returns a new SubEpic instance of the correct concrete type for this node's format

+ snapshotFields(): dict
	Interaction: return {"domainConcepts": copy(self.domainConcepts)}

### **SubEpic : StoryNode** << Entity >>

`testSuites` are the parsed test suites for this sub-epic, one per implementation tier.
Populated at load time; empty when no test files exist. Test suites can only exist after
the sub-epic's story representation has been rendered in the corresponding language
(`*-stories.<ext>` — `.ts`, `.py`, `.java`, `.js`) — the tier implementations derive
from the story constants and scenario definitions declared there.

+ SubEpic(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> domainConcepts: List<String>
+ << composition >> subEpics: List<SubEpic>
+ << composition >> stories: List<Story>
+ testSuites: List<TestSuite>
	Invariant: set by loader from matching tier test files; empty when none exist; one entry per tier found
----
+ hasSubEpics: Boolean
	Invariant: computed — returns len(self.subEpics) > 0; not a stored field; not copied in updateSelf

+ updateSelf(source: SubEpic): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.domainConcepts = copy(source.domainConcepts)
		self.testSuites = copy(source.testSuites)

+ childCollections(source: SubEpic): List<ChildCollectionPair>
	Invariant: sub-epics reconciled before stories so depth is known before diagram rows are positioned
	Interaction:
		return [
			ChildCollectionPair(self.subEpics, source.subEpics, self.createChildSubEpic),
			ChildCollectionPair(self.stories,   source.stories,   self.createChildStory)
		]

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

+ snapshotFields(): dict
	Interaction: return {"domainConcepts": copy(self.domainConcepts)}

### **Story : StoryNode** << Entity >>

`testCases` holds one matched `TestCase` per tier. Scenarios are reconciled as tree
children via `_reconcileCollection`; `testCases` are values copied through `updateSelf`.

+ Story(name: NodeName, sequentialOrder: Integer, storyType: StoryType)
------
+ storyType: StoryType
	Invariant: one of user | system | technical; affects styling only, not structure
+ users: List<String>
+ << composition >> scenarios: List<Scenario>
+ testCases: List<TestCase>
	Invariant: one entry per tier where a matching test case exists; empty until loader attaches them
+ domainTerms: List<String>
+ evidence: List<String>
----
+ updateSelf(source: Story): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.storyType = source.storyType
		self.users = copy(source.users)
		self.domainTerms = copy(source.domainTerms)
		self.evidence = copy(source.evidence)
		self.testCases = copy(source.testCases)

+ childCollections(source: Story): List<ChildCollectionPair>
	Interaction:
		return [ChildCollectionPair(self.scenarios, source.scenarios, self.createChildScenario)]

+ createChildScenario(source: Scenario): Scenario
	Invariant: returns a new Scenario instance of the correct concrete type for this node's format

+ snapshotFields(): dict
	Interaction: return {"storyType": self.storyType, "users": copy(self.users)}

### **StoryMap : StoryNode** << Entity >>

Root container. Extends `StoryNode` so `translateFrom` works uniformly at the map level.
`name` is fixed to `"StoryMap"`, `sequentialOrder` to `0`. `epics` and `increments` are
both reconciled tree children — the thin-slice view syncs increments the same way the
story-map view syncs epics.

+ StoryMap()
------
+ << composition >> epics: List<Epic>
+ << composition >> increments: List<Increment>
----
+ appendEpic(epic: Epic): void
	Interaction:
		self.epics.add(epic)
		self._renumberEpics()

+ removeEpic(epicName: NodeName): Epic
	Invariant: raises KeyError if no epic with that name exists
	Interaction:
		remove first epic whose name matches → _renumberEpics → return removed

+ reorderEpics(newNameOrder: List<NodeName>): void
	Invariant: newNameOrder must be a permutation of current epic names; raises ValueError otherwise

+ findEpic(name: NodeName): Epic
	Invariant: raises KeyError if not found

+ updateSelf(source: StoryMap): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder

+ childCollections(source: StoryMap): List<ChildCollectionPair>
	Interaction:
		return [
			ChildCollectionPair(self.epics,      source.epics,      self.createChildEpic),
			ChildCollectionPair(self.increments, source.increments, self.createChildIncrement)
		]

+ createChildEpic(source: Epic): Epic
	Invariant: abstract — concrete map class returns the correct Epic subtype (JsonEpic, DrawIOEpic, ...)

+ createChildIncrement(source: Increment): Increment
	Invariant: abstract — concrete map class returns the correct Increment subtype

- _renumberEpics(): void
	Invariant: sets sequentialOrder = i+1 for each epic after any structural mutation

### **ChildCollectionPair** << structural helper >>

Bundles a live self-children list, a source-children list, and the factory that creates
fresh children. `selfChildren` is a **live reference** to the owning node's child list —
`_reconcileCollection` mutates it via in-place slice assignment (`[:] = reconciled`) so
the change persists on the owner without a reference back to the parent. 

Initialisation: constructed inline inside each node's `childCollections` call

------
+ selfChildren: List<StoryNode>
	Invariant: live reference to the owning node's child list; slice-assigned in place by _reconcileCollection
+ sourceChildren: List<StoryNode>
+ createChild: Callable<StoryNode, StoryNode>
	Invariant: bound to the parent node's createChildXxx method for this child type

### references

**Ref — story_graph_ops/nodes.py**
Source: `skills/supporting/story-graph-ops/scripts/story_graph_ops/nodes.py`
Locator: StoryNode, Epic, SubEpic, Story, StoryMap
Extract: whole

### decisions made

- `translateFrom` algorithm is fixed on `StoryNode` and never overridden — only `updateSelf`, `childCollections`, and `createChildXxx` are extension points
- `_semanticTypeName` class variable guards cross-format translation — `DrawIOEpic.translateFrom(JsonSubEpic)` raises `TranslationError` immediately
- `_reconcileCollection` uses `consumedIds: Set<ObjectId>` to prevent one source child matching two self children
- `_findMatch` tries name first, then sequentialOrder — name is the stable semantic key; sequentialOrder catches renames
- `_reconcileCollection` replaces `pair.selfChildren` via in-place slice assignment — the list object reference on the parent is preserved
- `Story` is NOT a leaf — `childCollections` returns a scenario pair; scenarios are reconciled via `_reconcileCollection` the same way SubEpics reconcile Stories; `testCases` are values copied in `updateSelf` only
- `AcceptanceCriteria` is removed — a `Scenario` with Given/When/Then structure is the behavioral contract; the eval (`story-types.ts`) confirms: story constants have named scenario keys with `given/interactions`, no `acceptance_criteria` arrays
- `SubEpic.testSuites` is a list of `TestSuite` objects — the loader resolves paths, infers tier from file name suffix, and attaches all matching suites
- `StoryMap.increments` holds the ordered increment collection directly — thin slices describe how stories are ordered into marketable increments, which is a property of the map
- `SubEpic.hasSubEpics` is computed from `len(self.subEpics) > 0` — storing it would create a mutable flag that desync from the actual child list
- `ChildCollectionPair` is **not** a value object — its `selfChildren` is a live mutable reference; it is a structural helper scoped to one reconciliation call

---

## **Scenario**

`Scenario` extends `StoryNode` and is the **direct child of `Story`** in the translation
hierarchy. Scenarios are reconciled by name — the same `_reconcileCollection` loop that
reconciles SubEpics and Stories handles scenarios. When you translate JSON → TypeScript,
scenarios flow through format-specific `createChildScenario` factories and render as
named keyed properties on the story constant (eval: `story-types.ts` + `*-stories.ts`).

`Clause` and `Interaction` are value objects — they carry no identity and are not
reconciled as tree nodes; they are copied through `Scenario.updateSelf`.

### **Scenario : StoryNode** << Entity >> << leaf >>

Leaf node in the translation hierarchy. `childCollections` returns `[]` — clauses and
interactions are copied as values through `updateSelf`, not reconciled as tree children.

+ Scenario(name: NodeName, sequentialOrder: Integer)
------
+ storyName: String
	Invariant: the Story.name this scenario belongs to; used by the loader when attaching from separate BDD files
+ given: List<Clause>
+ << composition >> interactions: List<Interaction>
+ isOutline: Boolean
+ exampleRows: List<dict>
+ background: List<Clause>
+ evidence: List<String>
----
+ updateSelf(source: Scenario): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.storyName = source.storyName
		self.given = copy(source.given)
		self.interactions = copy(source.interactions)
		self.isOutline = source.isOutline
		self.exampleRows = copy(source.exampleRows)
		self.background = copy(source.background)
		self.evidence = copy(source.evidence)

+ childCollections(source: Scenario): List<ChildCollectionPair>
	Interaction:
		return []

+ snapshotFields(): dict
	Interaction:
		return {
			"storyName": self.storyName,
			"given": copy(self.given),
			"interactions": copy(self.interactions),
			"isOutline": self.isOutline,
			"exampleRows": copy(self.exampleRows),
			"background": copy(self.background),
			"evidence": copy(self.evidence)
		}

+ whenClauses(): List<Clause>
	Interaction: return [c for i in self.interactions for c in i.when]

+ thenClauses(): List<Clause>
	Interaction: return [c for i in self.interactions for c in i.then]

+ allClauses(): List<Clause>
	Interaction: given + all when and then from interactions in order

+ clauseCount(): Integer


### **Phase** << Enum >>

GIVEN | WHEN | THEN — which phase a clause belongs to; cached on `Clause` for reporting

### **Clause** << ValueObject >>

One step string in a scenario.

+ Clause(text: String, phase: Phase, isContinuation: Boolean, concepts: List<String>, values: List<String>, actor: String, source: SourceLocation)
------
+ text: String
	Invariant: verbatim step string; continuation clauses carry their `And ` / `But ` prefix intact — that prefix is the step dispatch key in the tier-class runner
+ phase: Phase
+ isContinuation: Boolean
	Invariant: true when text starts with `And ` or `But `
+ concepts: List<String>
	Invariant: bold-marked concept names (**X**) extracted from text
+ values: List<String>
	Invariant: italic-marked values (*v*) extracted from text
+ actor: String
	Invariant: first bold concept treated as actor (heuristic; empty if unclear)

### **Interaction** << ValueObject >>

A when-then block. One action, one set of observed outcomes. Most scenarios have exactly
one interaction; multiple interactions model sequential when-then chains (a smell to flag
for review).

+ Interaction(when: List<Clause>, then: List<Clause>)
------
+ when: List<Clause>
+ then: List<Clause>


### decisions made

- `Scenario` implements `StoryNode` — scenarios translate across all formats (JSON, Markdown, TypeScript, DrawIO) the same way SubEpics and Stories do; the eval confirms: `*-stories.ts` keys are camelCase scenario names with `given`, `interactions[].when`, `interactions[].then` — no `acceptance_criteria` arrays
- `Clause` and `Interaction` are ValueObjects, not StoryNodes — they have no identity; two clauses with the same text and phase are interchangeable within a scenario; reconciliation at the clause level would be meaningless
- `Clause.text` preserves the `And ` / `But ` prefix verbatim — that string is the dispatch key in the tier-class runner; stripping it would break runtime wiring
- `storyName` is preserved on `Scenario` for formats that load scenarios from separate BDD files — the loader matches by storyName to find the correct parent Story; formats that embed scenarios (TypeScript, JSON, DrawIO) don't need this field for loading but it remains for cross-format consistency
- Multiple interactions in one scenario are a design smell to flag, not a hard error — the BDD loader accepts them so scanners can report them

---

## **Increment**

A story map has a collection of increments — marketable slices of work. `Increment` is
a `StoryNode` leaf, sitting alongside `Epic` as a direct child of `StoryMap`. The
thin-slice diagram view renders and reconciles increments the same way the story-map
view renders and reconciles epics.

### **Increment : StoryNode** << Entity >> << leaf >>

Leaf node. `childCollections` returns `[]` — the story-name list, outcome sentence, and
prompt are value fields copied through `updateSelf`, not reconciled as tree children.

+ Increment(name: NodeName, sequentialOrder: Integer)
------
+ outcome: String
+ slicingNotes: String
+ stories: List<String>
	Invariant: verb-noun story names; must match StoryMap story names; cross-checked by scanner rules, not enforced at construction
+ decisionPrompt: String
----
+ updateSelf(source: Increment): void
	Interaction:
		self.name = source.name
		self.sequentialOrder = source.sequentialOrder
		self.outcome = source.outcome
		self.slicingNotes = source.slicingNotes
		self.stories = copy(source.stories)
		self.decisionPrompt = source.decisionPrompt

+ childCollections(source: Increment): List<ChildCollectionPair>
	Interaction:
		return []

+ snapshotFields(): dict
	Interaction:
		return {
			"outcome": self.outcome,
			"slicingNotes": self.slicingNotes,
			"stories": copy(self.stories),
			"decisionPrompt": self.decisionPrompt
		}

### decisions made

- `Increment` is a `StoryNode`, not a `ValueObject` — the thin-slice diagram view is syncable, and every view uses the same `_reconcileCollection` mechanism; `Increment` mirrors `Scenario` in this respect
- `ThinSlice` as a wrapper type is removed — it modelled the document, not the information; `StoryMap.increments` holds the collection directly; metadata fields that lived on `ThinSlice` (`product`, `slicingIntent`, `spineNote`) were document front-matter, not domain state
- `stories: List<String>` is a name reference, not an object reference — thin-slice files are authored independently of story maps; the loader does not resolve them to `Story` objects; scanners detect mismatches
- `Increment` is a **leaf** — `stories` is a name list (values), not `StoryNode` children; increments never contain other increments or reconcile stories as tree nodes
- `increments` defaults to `[]` — callers check `storyMap.increments` being empty rather than null-checking

---

## **Test Suite**

A `SubEpic` owns a list of `TestSuite` objects — one per implementation tier (domain,
server, client, e2e, ...). A `TestSuite` can only exist after the SubEpic's story
representation has been rendered in the corresponding language (`*-stories.<ext>` —
`.ts`, `.py`, `.java`, `.js`); the tier implementations derive from the story constants
and scenario step keys defined there.

A `Story` owns a list of `TestCase` objects — one per tier where a matching case was found.

### **Tier** << ValueObject >>

The implementation layer a test suite targets — e.g. `domain`, `server`, `client`, `e2e`,
`contract`. Tiers are project-specific: a bank might use `domain/server/client/e2e`, a
CLI tool might use `domain/cli`, a data pipeline might use `domain/etl/contract`. The
set of valid tiers for a workspace is discovered at load time from the file names
present under the tests root and/or an architecture config file; it is not a fixed
enum defined by the model.

+ Tier(name: String)
------
+ name: String
	Invariant: lowercase kebab or snake token matching the file-name segment (e.g. `domain` from `*-domain.test.ts`)

### **Language** << ValueObject >>

The programming language a test suite is written in — e.g. `typescript`, `python`,
`java`, `javascript`. Discovered at load time from the file extension. Tests are never
transformed between languages, so `Language` is a tag on the model rather than a
transformation target.

+ Language(name: String)
------
+ name: String
	Invariant: lowercase token derived from the file extension (`.ts` → `typescript`, `.py` → `python`, `.java` → `java`, `.js` → `javascript`)

### **TestSuite** << ValueObject >>

+ TestSuite(tier: Tier, language: Language, name: String, cases: List<TestCase>, importsReal: Boolean, source: SourceLocation)
------
+ tier: Tier
	Invariant: which implementation layer this suite covers; discovered from the file name segment
+ language: Language
	Invariant: the language the tests are written in; discovered from the file extension; tests are terminal artifacts, never transformed between languages
+ name: String
	Invariant: the describe / class label wrapping all cases
+ << composition >> cases: List<TestCase>
+ importsReal: Boolean
	Invariant: true if the suite imports the real implementation (not only mocks/stubs)
+ source: SourceLocation
	Invariant: points at the backing test file; the corresponding `*-stories.<ext>` path is derivable by naming convention and validated at load time — a suite whose stories file does not exist is a loader error

### **TestCase** << ValueObject >>

One test case inside a `TestSuite`. Maps to one `Story`. Contains `Test` objects — one per Scenario the case exercises.

+ TestCase(tier: Tier, name: String, tests: List<Test>, assertionsCount: Integer, hasRealAssertion: Boolean, referencesBugId: String, storySource: SourceLocation)
------
+ tier: Tier
	Invariant: inherited from the containing TestSuite; stored here so Story.testCases can be filtered by tier without navigating back to the suite
+ name: String
	Invariant: matched against Story.name to attach to the correct Story
+ << composition >> tests: List<Test>
+ assertionsCount: Integer
+ hasRealAssertion: Boolean
	Invariant: true if body has any expect/assert call (not just mock calls)
+ referencesBugId: String
+ storySource: SourceLocation
	Invariant: points at the Story constant in the sibling `*-stories.<ext>` file this case implements (same language as the containing TestSuite)

### **Test** << ValueObject >>

One test inside a `TestCase`. Maps to one `Scenario`.

+ Test(scenarioSource: SourceLocation)
------
+ scenarioSource: SourceLocation
	Invariant: points at the Scenario key in the sibling `*-stories.<ext>` file this test exercises (same language as the containing TestSuite)

### decisions made

- `TestFile` is removed — a file is provenance, not the model object; `TestSuite` is the collection of test cases, backed by a file via `source`
- The hierarchy is complete at every level: `TestSuite → TestCase → Test` mirrors `SubEpic → Story → Scenario`; each level is a proper object, not a list of source references
- `TestCase.storySource` and `Test.scenarioSource` are named after the domain objects they point at — a case tests a Story, a test exercises a Scenario
- Only `TestSuite` carries `source` — the case's file is the parent suite's file; the test's file is the parent case's suite's file; the method / step-block location within that file is derivable by name-matching, so `TestCase.source` and `Test.source` would be redundant
- The only stored source pointers besides `TestSuite.source` are `TestCase.storySource` and `Test.scenarioSource` — these point at positions inside a *different* file (`*-stories.<ext>`) that cannot be derived from the parent structure
- `SubEpic.testSuites` is a list — one entry per tier found on disk; empty when no tier files exist; scanners check for missing tiers
- `Story.testCases` is a list — one entry per tier where a matching case was found; a story with no entries in any tier has no test coverage
- `Tier` and `Language` are both project-specific values discovered at load time — the tier set from file-name segments, the language set from file extensions; neither is a fixed enum baked into the model
- `Language` is a **tag**, not a transformation axis — the model records what language a suite is written in so callers know how to read it, but tests are never transformed between languages; there is no `CodeTierTree` or equivalent
- `Story.testCases` matched from `SubEpic.testSuites[*].cases` by story name during loading — a test case with no matching story is an orphan flagged by scanners

---

## **Format: Diagram**

Diagram backends need two sub-layers: `DiagramStoryNode` computes positioning from
declarative layout rules; `DrawIOStoryNode` and `MiroStoryNode` hold the backend element
and serialize to it. All three layers stack via multiple inheritance (Python MRO /
TypeScript mixins). Non-diagram formats skip both sub-layers entirely.

The DrawIO format produces three views. Each view is a separate `.drawio` file, and
each supports the full uniform surface (`parse` / `render` / `sync`). A view is a slice
of the model rendered as diagram cells; parsing walks the cells back into the model
objects the view is responsible for.

| View | File | Renders | Owns on sync |
|------|------|---------|--------------|
| story-map | `story-map.drawio` | Epic → SubEpic → Story cells | structure: `StoryMap.epics`, sub-epics, stories |
| scenario | `scenarios.drawio` | Story → scenario divider → Given/When/Then clause cells | behavior: `Story.scenarios` (Scenario objects with clauses/interactions) |
| thin-slice | `thin-slicing.drawio` | Increment cells with story-name children | prioritization: `StoryMap.increments` |

### View-scoped sync

Each view is authoritative for its own slice. Syncing `story-map.drawio` reconciles
structure; syncing `scenarios.drawio` reconciles Story→Scenario children; syncing
`thin-slicing.drawio` reconciles StoryMap→Increment children. A view never wipes a
slice it did not render — `story-map.drawio` does not touch scenarios or increments
during sync, even though the underlying `StoryMap` and `Story` nodes carry those
collections. This is enforced at the view level, not the node level: nodes always
expose all their child collections; the view chooses which pairs to feed through
`_reconcileCollection`.

The scenario view renders the full behavioral walkthrough as visual clause blocks. Each
scenario starts with a divider cell labelled with the scenario name, followed by clause
cells grouped by phase. Stories with no scenarios are skipped on render; on sync,
scenarios present in the diagram are reconciled by name against the canonical model.

### Diagram Layer (shared across all diagram backends)

`DiagramStoryNode` extends the `updateSelf` extension point to add positioning — all
other parts of the `translateFrom` algorithm are inherited unchanged.

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
	Invariant: counts maximum nesting depth of SubEpic nodes under root; used to compute RowPositions

+ setPosition(x: Float, y: Float): void
	Invariant: abstract — delegates to backend element

+ setSize(width: Float, height: Float): void
	Invariant: abstract — delegates to backend element

+ applyFormatting(rules: FormattingRule): void
	Invariant: abstract — delegates to backend element

### **DiagramEpic : Epic, DiagramStoryNode** << abstract >>

------
+ containmentRules(): ContainmentRule
	Invariant: no allowed parents; contains sub-epics only

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

`DiagramStory` inherits `Story.childCollections` — the scenario pair is always present.
Which children are actually rendered and reconciled depends on the view:

- **story-map view** — renders the Story cell only; on sync, the view's parse yields a
  Story with an empty scenario list, so `_reconcileCollection` for scenarios is skipped
  in this view's sync path (view-scoped, not a node-level override)
- **scenario view** — renders the Story cell followed by scenario divider cells and
  clause cells; on sync, parses the diagram back into `Story.scenarios` with full
  Given / When / Then structure, which `_reconcileCollection` then reconciles by name

Both views operate on the same `DiagramStory` class; the view controls which slice of
`childCollections` it renders and parses, not the node.

------
+ containmentRules(): ContainmentRule
	Invariant: parent must be DiagramSubEpic; may hold scenario divider and clause cells beneath it in the scenario view

+ placementRules(): PlacementRule
	Invariant: fixed CELL_SIZE × CELL_SIZE; stories laid out left-to-right within sub-epic column; scenario blocks stack vertically below in the scenario view

+ createChildScenario(source: Scenario): DiagramScenario
	Invariant: abstract — concrete diagram class returns the correct DiagramScenario subtype

### **DiagramScenario : Scenario, DiagramStoryNode** << abstract >>

Scenario as a diagram node. The scenario view renders it as a divider cell (labelled
with the scenario name) followed by clause cells stacked below. `updateSelf` copies the
scenario's value fields (given / interactions / etc.) from `Scenario.updateSelf`, then
positions the divider from `DiagramStoryNode.updateSelf`.

------
+ containmentRules(): ContainmentRule
	Invariant: parent must be DiagramStory; contains clause cells only in the scenario view

+ placementRules(): PlacementRule
	Invariant: divider height = DIVIDER_HEIGHT; y stacks under the parent Story's scenario block

+ formattingRules(): FormattingRule
	Invariant: divider style key — distinct from story / clause styles so it is visually obvious where one scenario ends and the next begins

### **DiagramIncrement : Increment, DiagramStoryNode** << abstract >>

Increment as a diagram node. The thin-slice view renders it as a header cell
(`increment` style) followed by one story-name cell per entry in `stories`.

------
+ containmentRules(): ContainmentRule
	Invariant: parent must be a diagram StoryMap; contains story-name cells only in the thin-slice view

+ placementRules(): PlacementRule
	Invariant: increments stack vertically top-to-bottom; each carries a header row followed by its story-name rows

+ formattingRules(): FormattingRule
	Invariant: `increment` style key — distinct from epic / sub-epic / story styles

### **DiagramView** << Enum >>

`story-map` | `scenario` | `thin-slice` — one enum shared across all diagram backends
(DrawIO and Miro). Identifies which view slice a diagram document represents.

### **DiagramStoryMap : StoryMap, DiagramStoryNode** << abstract >>

Root of a diagram document. Which children (`epics` vs `increments`) it actually
renders and reconciles depends on `view` — the story-map and scenario views own the
epic tree, the thin-slice view owns the increment list. `childCollections` is
inherited unchanged; view-scoped sync (see § decisions) decides which pair to walk
based on `view`.

+ DiagramStoryMap(view: DiagramView)
------
+ view: DiagramView
	Invariant: one of `story-map` | `scenario` | `thin-slice`; determines which child pair is authoritative on sync
----
+ createChildEpic(source: Epic): DiagramEpic
	Invariant: abstract — concrete diagram class returns the correct DiagramEpic subtype
+ createChildIncrement(source: Increment): DiagramIncrement
	Invariant: abstract — concrete diagram class returns the correct DiagramIncrement subtype

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
	Invariant: dispatches to the correct row based on node type
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

- `DiagramStoryNode.updateSelf` calls `super.updateSelf(source)` first, then adds positioning — name and type-specific fields are written before geometry is computed
- `RowPositions` is a ValueObject — two instances with the same `maxDepth` are interchangeable; constructed fresh inside each `DiagramStoryNode.updateSelf` call
- `yFor(node)` dispatches by node type rather than carrying depth as a property on every node
- `DiagramStory` does NOT override `childCollections` — the scenario pair is always present on the node; which pair-half a view chooses to render and parse is a view-level concern, not a node-level one
- All three DrawIO views (story-map, scenario, thin-slice) support the full `parse` / `render` / `sync` surface — the earlier "render-only" designation was arbitrary; each view is authoritative for its own slice of the model and reconciles that slice on sync

---

### Backend Mixins + Concrete Classes (DrawIO and Miro)

`DrawIOStoryNode` and `MiroStoryNode` hold their backend element by composition,
implement the three abstract geometry methods from `DiagramStoryNode` by delegating to
the element, and extend `updateSelf` to serialize after positioning.

### **DrawIOStoryNode : DiagramStoryNode** << abstract >>

Mixin — combined with a concrete `DiagramXxx` class via multiple inheritance.

+ DrawIOStoryNode(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> element: DrawIOElement
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

+ collectAllNodes(): List<DrawIOStoryNode>
	Interaction:
		result = [self]
		for pair in self.childCollections(self):
			for child in pair.selfChildren:
				result.addAll(child.collectAllNodes())
		return result

### **MiroStoryNode : DiagramStoryNode** << abstract >>

Mixin — identical pattern to `DrawIOStoryNode`; element is `MiroElement`.

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
	Interaction: return new DrawIOSubEpic(source.name, source.sequentialOrder)

### **DrawIOSubEpic : DiagramSubEpic, DrawIOStoryNode** << Entity >>

+ DrawIOSubEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): DrawIOSubEpic
	Interaction: return new DrawIOSubEpic(source.name, source.sequentialOrder)

+ createChildStory(source: Story): DrawIOStory
	Interaction: return new DrawIOStory(source.name, source.sequentialOrder, source.storyType)

### **DrawIOStory : DiagramStory, DrawIOStoryNode** << Entity >>

+ DrawIOStory(name: NodeName, sequentialOrder: Integer, storyType: StoryType)
------
----
+ createChildScenario(source: Scenario): DrawIOScenario
	Interaction: return new DrawIOScenario(source.name, source.sequentialOrder)

### **DrawIOScenario : DiagramScenario, DrawIOStoryNode** << Entity >>

+ DrawIOScenario(name: NodeName, sequentialOrder: Integer)
------
----

### **DrawIOIncrement : DiagramIncrement, DrawIOStoryNode** << Entity >>

+ DrawIOIncrement(name: NodeName, sequentialOrder: Integer)
------
----

### **DrawIOStoryMap : DiagramStoryMap, DrawIOStoryNode** << Entity >>

Root of one DrawIO document (one view). `view` is inherited from `DiagramStoryMap`.

+ DrawIOStoryMap(view: DiagramView)
------
----
+ createChildEpic(source: Epic): DrawIOEpic
	Interaction: return new DrawIOEpic(source.name, source.sequentialOrder)

+ createChildIncrement(source: Increment): DrawIOIncrement
	Interaction: return new DrawIOIncrement(source.name, source.sequentialOrder)

### **MiroEpic : DiagramEpic, MiroStoryNode** << Entity >>

+ MiroEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): MiroSubEpic
	Interaction: return new MiroSubEpic(source.name, source.sequentialOrder)

### **MiroSubEpic : DiagramSubEpic, MiroStoryNode** << Entity >>

+ MiroSubEpic(name: NodeName, sequentialOrder: Integer)
------
----
+ createChildSubEpic(source: SubEpic): MiroSubEpic
	Interaction: return new MiroSubEpic(source.name, source.sequentialOrder)

+ createChildStory(source: Story): MiroStory
	Interaction: return new MiroStory(source.name, source.sequentialOrder, source.storyType)

### **MiroStory : DiagramStory, MiroStoryNode** << Entity >>

+ MiroStory(name: NodeName, sequentialOrder: Integer, storyType: StoryType)
------
----
+ createChildScenario(source: Scenario): MiroScenario
	Interaction: return new MiroScenario(source.name, source.sequentialOrder)

### **MiroScenario : DiagramScenario, MiroStoryNode** << Entity >>

+ MiroScenario(name: NodeName, sequentialOrder: Integer)
------
----

### **MiroIncrement : DiagramIncrement, MiroStoryNode** << Entity >>

+ MiroIncrement(name: NodeName, sequentialOrder: Integer)
------
----

### **MiroStoryMap : DiagramStoryMap, MiroStoryNode** << Entity >>

Root of one Miro board (one view). `view` is inherited from `DiagramStoryMap`.

+ MiroStoryMap(view: DiagramView)
------
----
+ createChildEpic(source: Epic): MiroEpic
	Interaction: return new MiroEpic(source.name, source.sequentialOrder)

+ createChildIncrement(source: Increment): MiroIncrement
	Interaction: return new MiroIncrement(source.name, source.sequentialOrder)

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

- Every `StoryNode` type has a diagram subclass when it renders in diagrams — the full set for DrawIO is `DrawIOEpic`, `DrawIOSubEpic`, `DrawIOStory`, `DrawIOScenario`, `DrawIOIncrement`; Miro has the mirror set; each holds its own `DrawIOElement` / `MiroElement` for position, size, style, and serialization
- `DrawIOScenario` and `DrawIOIncrement` (and Miro equivalents) exist because both types render as diagram cells and both are reconciled during sync — treating them as plain non-diagram objects broke the pattern that every other node follows
- All three DrawIO views (story-map, scenario, thin-slice) render, parse, and sync — `DrawIOAcceptanceCriteria` / `MiroAcceptanceCriteria` are gone along with `AcceptanceCriteria`; the acceptance-criteria file is renamed `scenarios.drawio`
- Views are scoped: syncing `story-map.drawio` reconciles the epic tree only (scenarios and increments untouched); syncing `scenarios.drawio` walks stories and reconciles scenarios only; syncing `thin-slicing.drawio` reconciles increments only; a view never wipes a slice it did not render
- `DrawIOStoryNode.updateSelf` and `MiroStoryNode.updateSelf` call `super.updateSelf` then serialize — three layers stack: field copy → positioning → serialization
- `DrawIOElement` and `MiroElement` are created inside the concrete node's constructor — the node owns the element's lifecycle (composition)

---

## **Format: Documents**

Document formats (Markdown, JSON) read or write story structure as text or data.
No positioning layer needed — they extend `StoryNode` directly.

### Pattern

```
DocumentStoryNode : StoryNode   (abstract mixin per format)
  updateSelf(source)
    → reads/writes format-specific text or data fields
    → no setPosition / setSize / applyFormatting
```

### **MarkdownStoryNode : StoryNode** << abstract >>

Mixin for Markdown source adapter.

+ updateSelf(source: StoryNode): void
	Invariant: reads source.name and source.sequentialOrder; writes Markdown heading line

### **MarkdownEpic : Epic, MarkdownStoryNode** << Entity >>
### **MarkdownSubEpic : SubEpic, MarkdownStoryNode** << Entity >>
### **MarkdownStory : Story, MarkdownStoryNode** << Entity >>
### **MarkdownScenario : Scenario, MarkdownStoryNode** << Entity >>

Writes the scenario as a Markdown subsection under its Story — heading = scenario name,
followed by `**Given**` / `**When**` / `**Then**` bullet lists reconstructed from
`given` and `interactions`.

### **MarkdownIncrement : Increment, MarkdownStoryNode** << Entity >>

Writes the increment as a section in `thin-slicing.md` (or the workspace's thin-slice
document) — heading = increment name, followed by an ordered list of `stories` (name
references) and any narrative fields (`slicingIntent`, `spineNote`).

### **MarkdownStoryMap : StoryMap, MarkdownStoryNode** << Entity >>

Root of the Markdown document set — one `story-map.md` for the epic tree, one
`thin-slicing.md` for increments. Both files are reconciled through the same StoryMap
instance; parsing merges them into one canonical model.

+ MarkdownStoryMap(storyMapPath: FilePath, thinSlicingPath: Optional<FilePath>)
------
+ storyMapPath: FilePath
+ thinSlicingPath: Optional<FilePath>
	Invariant: null when the workspace has no thin-slicing document; parsing yields zero increments in that case
----
+ createChildEpic(source: Epic): MarkdownEpic
	Interaction: return new MarkdownEpic(source.name, source.sequentialOrder)

+ createChildIncrement(source: Increment): MarkdownIncrement
	Interaction: return new MarkdownIncrement(source.name, source.sequentialOrder)

### **JsonStoryNode : StoryNode** << abstract >>

Mixin for JSON (story-graph.json) serialization and deserialization.

+ updateSelf(source: StoryNode): void
	Invariant: reads source fields; writes to JSON node representation

### **JsonEpic : Epic, JsonStoryNode** << Entity >>
### **JsonSubEpic : SubEpic, JsonStoryNode** << Entity >>
### **JsonStory : Story, JsonStoryNode** << Entity >>
### **JsonScenario : Scenario, JsonStoryNode** << Entity >>

Writes the scenario as an object under `story.scenarios[]` — same fields as
`Scenario` in the canonical model (`name`, `given`, `interactions[]`).

### **JsonIncrement : Increment, JsonStoryNode** << Entity >>

Writes the increment as an object under `storyMap.increments[]` — `name`, ordered
`stories[]` name list, optional narrative fields.

### **JsonStoryMap : StoryMap, JsonStoryNode** << Entity >>

Root of the `story-graph.json` document. Serializes to a single JSON object with
`epics[]` and `increments[]` arrays at the top level.

+ JsonStoryMap(path: FilePath)
------
+ path: FilePath
----
+ createChildEpic(source: Epic): JsonEpic
	Interaction: return new JsonEpic(source.name, source.sequentialOrder)

+ createChildIncrement(source: Increment): JsonIncrement
	Interaction: return new JsonIncrement(source.name, source.sequentialOrder)

---

## **Format: Code**

Code formats (TypeScript, Python, Java, JavaScript) render, parse, and sync the same
`StoryMap → Epic → SubEpic → Story → Scenario` hierarchy that every other format does.
The tree structure is identical across languages; the **syntax** each node emits and
parses differs per language — most visibly at the `Scenario` level, where the shape of
`given` / `interactions` / `then` clauses is language-specific (TypeScript `as const
satisfies`, Python `TypedDict` literal, Java static record, JavaScript object literal).

Code follows the same node pattern as Diagram: an abstract format mixin (`CodeStoryNode`)
extends `StoryNode` with a code-writing extension point; language mixins
(`TypeScriptStoryNode`, `PythonStoryNode`, …) supply syntax; concrete classes combine
one of each per node type. `updateSelf` is where the per-language rendering of a given
node — including a `Scenario`'s clause block — actually lives.

`CodeStoryMap` is the workspace-level entry point that walks a folder tree, constructs
the right per-language nodes, and exposes the uniform `render / parse / sync` surface
callers use.

Test suites, test cases, and tests are **not** part of this hierarchy — they are
language-native implementation code populated on the model by scanners (see § Test
Suite) and tagged with a `Language`. You never generate a Java JUnit test from a Python
pytest test — tests are terminal artifacts, not transformed between languages.

`Increment` has **no Code implementation** — it is a product / delivery concept, not a
code artifact. There is no `CodeIncrement`, no `TypeScriptIncrement`, no equivalent per
language. When callers ask a Code adapter to render or parse increments, it delegates
to the sibling Markdown adapter for the workspace's `thin-slicing.md` file — the
Markdown format owns increments, and Code's `<Language>StoryMap.createChildIncrement`
returns a `MarkdownIncrement` bound to that file.

### Pattern

```
CodeStoryNode : StoryNode                      (abstract mixin per format)
  updateSelf(source)
    → writes format-specific code text
    → no setPosition / setSize / applyFormatting

CodeEpic     : Epic,     CodeStoryNode         (abstract)
CodeSubEpic  : SubEpic,  CodeStoryNode         (abstract)
CodeStory    : Story,    CodeStoryNode         (abstract)
CodeScenario : Scenario, CodeStoryNode         (abstract)

TypeScriptStoryNode : CodeStoryNode            (abstract language mixin)
  → shared TypeScript AST helpers, import layout, `story-types.ts` linkage

TypeScriptEpic     : CodeEpic,     TypeScriptStoryNode   (concrete)
TypeScriptSubEpic  : CodeSubEpic,  TypeScriptStoryNode   (concrete)
TypeScriptStory    : CodeStory,    TypeScriptStoryNode   (concrete)
TypeScriptScenario : CodeScenario, TypeScriptStoryNode   (concrete)

(same pattern for Python / Java / JavaScript)
```

### **CodeStoryNode : StoryNode** << abstract >>

Mixin for code source adapters. Extends `updateSelf` to emit language code text;
carries no positioning surface (no `setPosition` / `setSize` / `applyFormatting`).

+ CodeStoryNode(name: NodeName, sequentialOrder: Integer)
------
+ << composition >> renderer: LanguageAst
	Invariant: the language-specific AST writer used by `updateSelf` to serialize this node into code
----
+ updateSelf(source: StoryNode): void
	Invariant: extends super.updateSelf — also writes this node's code representation via `renderer`
	Interaction:
		super.updateSelf(source)
		self._writeCode(self.renderer)

- _writeCode(ast: LanguageAst): void
	Invariant: abstract — subclass writes its node-type-specific code (folder path, file header, story const, scenario clause block, etc.) into the AST

### **CodeEpic : Epic, CodeStoryNode** << abstract >>

Represents an Epic folder plus (optionally) an Epic-level helper file. Non-leaf: no
per-epic file emitted beyond the helper; children are rendered by their own nodes.

------
+ createChildSubEpic(source: SubEpic): CodeSubEpic
	Invariant: abstract — concrete language class returns the correct `<Language>SubEpic` subtype

- _writeCode(ast: LanguageAst): void
	Invariant: writes the epic folder path plus optional epic-level helper file (e.g. Python `__init__.py`, Java `<Epic>Helpers.java`); TypeScript / JavaScript emit no helper by default

### **CodeSubEpic : SubEpic, CodeStoryNode** << abstract >>

A non-leaf `CodeSubEpic` emits a folder only; a leaf `CodeSubEpic` emits one story-map
source file (e.g. `route-transfer-before-cutoff-stories.ts`). Leaf files aggregate this
sub-epic's Story constants and their embedded Scenario definitions.

------
+ createChildSubEpic(source: SubEpic): CodeSubEpic
+ createChildStory(source: Story): CodeStory

- _writeCode(ast: LanguageAst): void
	Invariant: leaf sub-epic writes a stories file with imports, then delegates to child `CodeStory` nodes; non-leaf writes a folder only

### **CodeStory : Story, CodeStoryNode** << abstract >>

Emits one Story constant (or equivalent declaration) into the parent sub-epic's stories
file. Delegates the Scenario clause block to child `CodeScenario` nodes so language-
specific scenario syntax is authored in one place.

------
+ createChildScenario(source: Scenario): CodeScenario

- _writeCode(ast: LanguageAst): void
	Invariant: writes the Story declaration header (name, actor, domainTerms, evidence) and opens the container that holds keyed scenario properties; each child `CodeScenario` writes itself into that container

### **CodeScenario : Scenario, CodeStoryNode** << abstract >>

The Scenario node. This is where language-specific rendering diverges most visibly —
`given` / `interactions.when` / `interactions.then` are laid out differently in each
language. Concrete language subclasses override `_writeCode` (via their language mixin)
to emit their native syntax.

------
- _writeCode(ast: LanguageAst): void
	Invariant: abstract — writes the scenario key + clause block in the target language's syntax; must round-trip parse: the same content the language parser reads back is what this method emits

### **TypeScriptStoryNode : CodeStoryNode** << abstract >>

TypeScript language mixin — shared AST writer configuration, import layout,
`story-types.ts` linkage, `satisfies` clause convention.

### **TypeScriptEpic : CodeEpic, TypeScriptStoryNode** << Entity >>
### **TypeScriptSubEpic : CodeSubEpic, TypeScriptStoryNode** << Entity >>
### **TypeScriptStory : CodeStory, TypeScriptStoryNode** << Entity >>

Writes:

```
export const StoryPascalCase = {
  story:       'Story name',
  actor:       'Actor',
  domainTerms: readonly string[],
  evidence:    readonly string[],
  // one keyed property per Scenario, emitted by TypeScriptScenario …
} as const satisfies Story
```

### **TypeScriptScenario : CodeScenario, TypeScriptStoryNode** << Entity >>

Writes one keyed property on the parent Story constant:

```
scenarioKeyCamelCase: {
  name:         'Scenario name',
  given:        readonly string[],
  interactions: readonly [{ when: readonly string[], then: readonly string[] }],
},
```

Parses the same shape back — exported const names → Stories, keyed properties on those
constants → Scenarios (given / interactions / then).

### **PythonStoryNode : CodeStoryNode** << abstract >>

Python language mixin — module docstring convention, `TypedDict` / `dataclass` choice,
`__init__.py` helper linkage.

### **PythonEpic : CodeEpic, PythonStoryNode** << Entity >>
### **PythonSubEpic : CodeSubEpic, PythonStoryNode** << Entity >>
### **PythonStory : CodeStory, PythonStoryNode** << Entity >>
### **PythonScenario : CodeScenario, PythonStoryNode** << Entity >>

`PythonScenario` writes a scenario as a typed-dict literal (or `dataclass` field
depending on project convention) — same fields as TypeScript (`name`, `given`,
`interactions`), rendered as Python syntax.

### **JavaStoryNode : CodeStoryNode** << abstract >>

Java language mixin — package declaration, static record convention, helper class
linkage.

### **JavaEpic : CodeEpic, JavaStoryNode** << Entity >>
### **JavaSubEpic : CodeSubEpic, JavaStoryNode** << Entity >>
### **JavaStory : CodeStory, JavaStoryNode** << Entity >>
### **JavaScenario : CodeScenario, JavaStoryNode** << Entity >>

`JavaScenario` writes each scenario as a `static final` record field on the Story class,
with nested records for `Interaction`.

### **JavaScriptStoryNode : CodeStoryNode** << abstract >>

JavaScript language mixin — mirrors TypeScript minus type annotations and the
`satisfies` clause; shared modules are `story-types.js` and `story-runner.js`.

### **JavaScriptEpic : CodeEpic, JavaScriptStoryNode** << Entity >>
### **JavaScriptSubEpic : CodeSubEpic, JavaScriptStoryNode** << Entity >>
### **JavaScriptStory : CodeStory, JavaScriptStoryNode** << Entity >>
### **JavaScriptScenario : CodeScenario, JavaScriptStoryNode** << Entity >>

Mirrors `TypeScriptScenario` without types.

---

### **CodeStoryMap : StoryMap, CodeStoryNode** << abstract >>

Root of a code source tree — inherits `render / parse / sync` behaviour from
`StoryMap.translateFrom` (via `StoryNode`) and adds file-tree read/write on top.
`createChildEpic` returns the language's Epic subtype; `createChildIncrement` delegates
to `MarkdownIncrement` bound to the workspace's `thin-slicing.md` (Increment has no
code implementation — see § decisions).

+ CodeStoryMap(testsRoot: String, thinSlicingPath: Optional<FilePath>)
------
+ LEAF_EXTENSION: String
	Invariant: language-specific stories-file extension (e.g. `-stories.ts`, `_stories.py`)
+ LANGUAGE_LINE_COMMENT: String
+ testsRoot: String
+ thinSlicingPath: Optional<FilePath>
	Invariant: workspace `thin-slicing.md` path; when null, zero increments are parsed
----
+ createChildEpic(source: Epic): CodeEpic
	Invariant: abstract — concrete language subclass returns its `<Language>Epic` subtype

+ createChildIncrement(source: Increment): MarkdownIncrement
	Interaction:
		return new MarkdownIncrement(source.name, source.sequentialOrder)
	Invariant: Increment has no code implementation; delegates to Markdown for the workspace's `thin-slicing.md`

+ render(canonical: StoryMap, previous: Dict<FilePath, String>): Dict<FilePath, String>
	Invariant: HAND-WRITTEN regions in matching existing files are preserved byte-for-byte
	Interaction:
		self.translateFrom(canonical)                                    ← reconciles Epics/SubEpics/Stories/Scenarios
		tree = {}
		for filePath, generated in self._emitFiles():
			tree[filePath] = self._preserveHandWritten(previous.get(filePath, ''), generated)
		return tree

+ parse(external: Dict<FilePath, String>): StoryMap
	Invariant: reconstructs Epic/SubEpic hierarchy from folder structure; leaf files yield `CodeStory` + `CodeScenario` nodes; raises CodeStoryMapError if no recognisable Epic folders found

+ sync(external: Dict<FilePath, String>, canonical: StoryMap): UpdateReport
	Interaction:
		parsed = self.parse(external)
		return canonical.translateFrom(parsed)

- _emitFiles(): Dict<FilePath, String>
	Invariant: walks the built node tree, calling each node's `_writeCode` and aggregating file output

- _preserveHandWritten(previous: String, generated: String): String
	Invariant: every HAND-WRITTEN START/END region in previous survives regeneration byte-for-byte

- _folderSlug(node: Epic | SubEpic, siblings: List): String
	Invariant: to_kebab; appends --{sequentialOrder} suffix on name collision

### **TypeScriptStoryMap : CodeStoryMap, TypeScriptStoryNode** << Entity >>

`LEAF_EXTENSION = -stories.ts`. The tests root also carries shared modules
`story-types.ts` (`Interaction`, `Scenario`, `Story`, `StepFn`, `TierImpl<S>`) and
`story-runner.ts`.

+ createChildEpic(source: Epic): TypeScriptEpic
	Interaction: return new TypeScriptEpic(source.name, source.sequentialOrder)

### **PythonStoryMap : CodeStoryMap, PythonStoryNode** << Entity >>

`LEAF_EXTENSION = _stories.py`. Each Epic also emits an `__init__.py` helper.

+ createChildEpic(source: Epic): PythonEpic
	Interaction: return new PythonEpic(source.name, source.sequentialOrder)

### **JavaStoryMap : CodeStoryMap, JavaStoryNode** << Entity >>

`LEAF_EXTENSION = Stories.java`. Each Epic emits a helper class.

+ createChildEpic(source: Epic): JavaEpic
	Interaction: return new JavaEpic(source.name, source.sequentialOrder)

### **JavaScriptStoryMap : CodeStoryMap, JavaScriptStoryNode** << Entity >>

`LEAF_EXTENSION = -stories.js`. Shared modules are `story-types.js` and `story-runner.js`.

+ createChildEpic(source: Epic): JavaScriptEpic
	Interaction: return new JavaScriptEpic(source.name, source.sequentialOrder)

### decisions made

- Code format follows the **same node pattern as Diagram** — one `CodeStoryNode` mixin extending `StoryNode`, then `CodeEpic / SubEpic / Story / Scenario` abstract nodes, then per-language concrete subclasses; scenarios are first-class nodes with their own `updateSelf`, not a leaf handled inside a flat adapter
- The language-specific difference lives on `<Language>Scenario._writeCode` — TypeScript emits a keyed property with `satisfies`, Python emits a `TypedDict` literal, Java emits a static record, JavaScript emits a plain object; the tree shape and reconciliation algorithm are identical across languages
- `CodeStoryMap` inherits `StoryMap, CodeStoryNode` — it IS a StoryMap subclass, part of the node hierarchy just like `JsonStoryMap` and `DiagramStoryMap`; the `render / parse / sync` surface is inherited from `StoryNode.translateFrom` plus a thin file-tree emit/read layer, not a separate adapter pattern
- Test suites, test cases, and tests are **not** in this hierarchy — they are language-native implementation code populated by scanners; there is no `CodeTest` node, no `CodeTierTree`, no test-side transformer; `TestSuite.language` is a tag for downstream consumers
- `Increment` has no Code implementation — it is a product / delivery concept, not code; the Code format's `createChildIncrement` delegates to `MarkdownIncrement` bound to the workspace's `thin-slicing.md`; if `thin-slicing.md` is absent, the Code StoryMap parses zero increments (not an error, just nothing to reconcile)
- `_preserveHandWritten` protects any hand-written module additions in story-map source files — generated story constants and scenario definitions are always regenerated from the model; anything else authors add to a leaf file (helper functions, additional imports) survives regeneration byte-for-byte

## **Translation Result**

### **TranslationError** << Exception >>

Raised when `translateFrom` or `reverseOn` is called with an incompatible argument.

### **ChangeKind** << Enum >>

EXACT_MATCH | RENAME | ADD | REMOVE | REORDER

### **Change** << ValueObject >> (frozen)

------
+ kind: ChangeKind
+ fromName: Optional<String>
+ toName: Optional<String>
+ nodeName: Optional<String>
+ parentName: Optional<String>
+ confidence: Optional<Float>

### **UpdateReport** << Entity >>

+ UpdateReport()
------
+ << composition >> changes: List<Change>
+ snapshot: Optional<NodeSnapshot>
+ owningNodeId: Optional<ObjectId>
	Invariant: set to id(node) when captureSnapshot is called; guards reverseOn against foreign reports
----
+ captureSnapshot(node: StoryNode): void
	Invariant: must be called before any updateSelf or _reconcileCollection runs
	Interaction:
		self.snapshot = NodeSnapshot.of(node)
		self.owningNodeId = id(node)

+ addExactMatch(selfName: NodeName, sourceName: NodeName): void
+ addRename(fromName: NodeName, toName: NodeName, confidence: Float): void
+ addNew(node: StoryNode, parentName: NodeName): void
+ addRemoved(node: StoryNode, parentName: NodeName): void
+ addReorder(fromName: NodeName, toName: NodeName): void

+ reverseOn(node: StoryNode): void
	Invariant: raises TranslationError if owningNodeId != id(node) or snapshot is None

+ hasChanges(): Boolean
+ adds(): List<Change>
+ removes(): List<Change>
+ renames(): List<Change>
+ reorders(): List<Change>

### **NodeSnapshot** << ValueObject >>

+ NodeSnapshot(nodeId: ObjectId, name: NodeName, sequentialOrder: Integer, extraFields: dict, childSnapshots: List<NodeSnapshot>)
------
+ nodeId: ObjectId
+ name: NodeName
+ sequentialOrder: Integer
+ extraFields: dict
	Invariant: type-specific fields captured via node.snapshotFields()
+ << composition >> childSnapshots: List<NodeSnapshot>
----
+ restoreInto(node: StoryNode): void
	Interaction:
		node.name = self.name
		node.sequentialOrder = self.sequentialOrder
		node.restoreSnapshotFields(self.extraFields)
		children = node.children()
		for i, childSnapshot in enumerate(self.childSnapshots):
			if i < len(children): childSnapshot.restoreInto(children[i])

+ of(node: StoryNode): NodeSnapshot
	Invariant: static factory; captures current state recursively
	Interaction:
		return new NodeSnapshot(
			nodeId: id(node), name: node.name,
			sequentialOrder: node.sequentialOrder,
			extraFields: node.snapshotFields(),
			childSnapshots: [NodeSnapshot.of(c) for c in node.children()]
		)

### references

**Ref — story_graph_ops/update_report.py**
Source: `skills/supporting/story-graph-ops/scripts/story_graph_ops/update_report.py`
Locator: UpdateReport, NodeSnapshot, ChildCollectionPair, Change, ChangeKind, TranslationError
Extract: whole

### decisions made

- `UpdateReport` is an Entity — identity is the specific translation run that produced it
- `NodeSnapshot` is a ValueObject — immutable once created; `nodeId` is part of captured state, not a snapshot identity key
- `captureSnapshot` must be the first call inside `translateFrom` — any write before snapshot risks losing reversal fidelity
- `owningNodeId` guards `reverseOn` — calling reverse on the wrong node raises `TranslationError`
- `extraFields` allows leaf classes to snapshot type-specific fields without modifying base snapshot logic

---

# Scanner Artifact Model

Parsed workspace metadata consumed by practice scanners. The model (StoryMap,
Story.scenarios, SubEpic.testSuites, StoryMap.increments) is already populated by the
time a scanner receives the Workspace. The Scanner Artifact Model adds only what cannot
live on the model: document-level context files and the file:line citation carrier.

## **SourceLocation** << ValueObject >> (frozen)

Immutable file:line citation. Used throughout the model for violation citing.

+ SourceLocation(file: String, line: Integer)
------
+ file: String
	Invariant: relative path from workspace root
+ line: Integer
	Invariant: 1-indexed; 0 = unknown
----
+ render(): String
	Invariant: returns "file:line" when line > 0; returns file otherwise

---

## **Workspace** << aggregate >>

Thin facade over the loaded model. Scanners receive a `Workspace` and use `has_xxx()`
guards before accessing a field.

+ Workspace(root: Path, storyMap: StoryMap, storyContexts: List<StoryContext>)
------
+ root: Path
+ storyMap: StoryMap
	Invariant: fully loaded — Story.scenarios, SubEpic.testSuites, StoryMap.increments are already attached
+ << composition >> storyContexts: List<StoryContext>
----
+ hasStoryMap(): Boolean
	Invariant: storyMap has at least one epic
+ hasStoryContexts(): Boolean
+ hasIncrements(): Boolean
	Invariant: storyMap.increments is non-empty
+ hasScenarios(): Boolean
	Invariant: at least one Story anywhere under storyMap has a non-empty scenarios list
+ hasTestSuites(): Boolean
	Invariant: at least one SubEpic anywhere under storyMap has a non-empty testSuites list

---

## **StoryContext** << ValueObject >>

One `story-context.md` file at the root of an epic or sub-epic folder.

+ StoryContext(folder: String, title: String, hasStatus: Boolean, hasStoriesInScope: Boolean, hasContextNotes: Boolean, storiesInScope: List<String>, isLeafFolder: Boolean, source: SourceLocation)
------
+ folder: String
	Invariant: relative path from workspace root to the containing folder
+ title: String
+ hasStatus: Boolean
+ hasStoriesInScope: Boolean
+ hasContextNotes: Boolean
+ storiesInScope: List<String>
+ isLeafFolder: Boolean
	Invariant: true when the folder has no child sub-folders; story-context.md at a leaf is a placement violation

---

## Application Services: workspace/ loaders

+ load_workspace(root: Path): Workspace
	Interaction:
		storyMap    = load_story_map(root)                          ← picks primary source; scenarios embedded arrive with it
		increments  = load_increments(root, storyMap)               ← reconciles thin-slicing.md and/or thin-slicing.drawio into storyMap.increments
		looseScens  = load_loose_scenarios(root)                    ← fallback for scenarios authored outside the primary story-map source
		testSuites  = load_tests(root)
		contexts    = load_story_contexts(root)
		_attachLooseScenariosToStoryMap(storyMap, looseScens)
		_attachTestSuitesToSubEpics(storyMap, testSuites)
		_attachTestCasesToStories(storyMap)
		return new Workspace(root, storyMap, contexts)

+ load_story_map(root: Path): StoryMap
	Invariant: detection order for the primary source — `story-graph.json` → `story-map.drawio` → `story-map.md` → language code tree (`*-stories.<ext>` under tests root); returns empty StoryMap if none found; the chosen adapter's `parse` populates Epics, SubEpics, Stories and any embedded Scenarios in one pass

+ load_increments(root: Path, storyMap: StoryMap): List<Increment>
	Invariant: detection order — `thin-slicing.md` → `thin-slicing.drawio` → `## Thin slices` section inside `story-map.md`; the chosen adapter's `parse` produces `Increment` nodes that are then reconciled into `storyMap.increments` via `StoryMap.translateFrom` on the increment child pair; returns [] if none found

+ load_loose_scenarios(root: Path): List<Scenario>
	Invariant: fallback path for scenarios authored outside the primary story-map source — scans `**/scenarios/*.md` and any standalone `scenarios.drawio` when the primary source did not carry them; deduplicates by (storyName, scenarioName); returns [] when the primary source already carries scenarios

+ load_tests(root: Path): List<TestSuite>
	Invariant: discovers the workspace's tier set from file-name segments (e.g. `*-<tier>.test.ts`, `test_*_<tier>.py`, `<Tier>Test.java`) and its language set from file extensions; for each test file constructs a TestSuite with the extracted `Tier` and `Language`, validates that the corresponding `*-stories.<ext>` sibling exists in the same language (loader error otherwise), parses TestCase / Test objects; returns [] if nothing found

+ load_story_contexts(root: Path): List<StoryContext>

- _attachLooseScenariosToStoryMap(storyMap: StoryMap, scenarios: List<Scenario>): void
	Invariant: only invoked when the primary story-map source did not embed scenarios — attaches loose scenarios to their parent `Story` by `storyName` match; JSON and every code language embed scenarios in the primary source and skip this path entirely; Markdown may embed inline (skip) or place them in `**/scenarios/*.md` (attach); DrawIO always uses this path — the primary source `story-map.drawio` carries only structure, and scenarios flow in from the sibling `scenarios.drawio`

- _attachTestSuitesToSubEpics(storyMap: StoryMap, testSuites: List<TestSuite>): void
	Invariant: matches each TestSuite to a SubEpic by path convention; resolves `storySource` on each contained TestCase against the matching-language `*-stories.<ext>`; appends to `SubEpic.testSuites`

- _attachTestCasesToStories(storyMap: StoryMap): void
	Invariant: for each SubEpic, iterates all testSuites, matches each TestCase to a Story by name; appends to Story.testCases

### decisions made

- `load_workspace` attaches all subsidiary data to the model before returning — scanners see a fully populated model; they never call sub-loaders
- `Workspace` does not carry `scenarios`, `tests`, or `increments` as separate fields — those live on the model where they belong (`Story.scenarios`, `SubEpic.testSuites`, `StoryMap.increments`); scanners traverse `storyMap` to find them
- Scenarios arrive through one of two paths: **embedded** in the primary story-map source (JSON, all four code languages, and inline Markdown carry them), or **loose** via `load_loose_scenarios` (DrawIO's `scenarios.drawio`, standalone `**/scenarios/*.md`); `_attachLooseScenariosToStoryMap` handles the loose case by name-matching to parent Stories
- Increments are loaded through a separate detection chain (`thin-slicing.md` → `thin-slicing.drawio` → embedded section) and reconciled into `storyMap.increments` via `translateFrom` — same reconciliation mechanism epics use, not a bulk replace
- `load_tests` discovers `Tier` and `Language` at load time from file names and extensions — neither is a fixed enum baked into the loader; the presence of a sibling `*-stories.<ext>` in the matching language is validated per suite
- Unmatched scenarios, unmatched test cases, and orphaned test files stay in their lists after attachment; scanners detect them by walking the model and comparing

---

# Boundary Domain

### **LanguageAst** << abstract >>

Holds a parsed or generated AST for one language.

------
----
+ parse(source: CodeString): void
+ generate(): CodeString
+ nodeFor(name: NodeName): AstNode

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
