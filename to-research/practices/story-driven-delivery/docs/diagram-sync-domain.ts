// Story Map Diagram Sync — Domain Model (TypeScript)
// Generated 1-1 from story-ops-domain-specification.md
//
// Multiple inheritance note: TypeScript does not support multiple inheritance.
// The three-layer stack (StoryNode → DiagramStoryNode → BackendStoryNode) is
// implemented using the mixin pattern so DrawIOEpic correctly inherits from
// both DiagramEpic and DrawIOStoryNode.

// ─── Primitive value types ──────────────────────────────────────────────────

type NodeName = string;
type CriteriaText = string;
type FilePath = string;
type StoryType = 'user' | 'system' | 'technical';
type StyleKey = string;
type XmlString = string;
type JsonPayload = Record<string, unknown>;
type CellId = string;

type Constructor<T = object> = new (...args: unknown[]) => T;

// ─── Supporting value objects ────────────────────────────────────────────────

interface Position { x: number; y: number; }
interface Boundary { position: Position; width: number; height: number; }
interface ContainmentRule { allowedParents: string[]; allowedChildren: string[]; }
interface PlacementRule { x: number; yStrategy: string; height: number; widthStrategy: string; }
interface FormattingRule { styleKey: StyleKey; }

interface DomainConcept { name: string; }
interface StoryUser { name: string; }

// ─── ChildCollectionPair ─────────────────────────────────────────────────────

interface ChildCollectionPair {
  selfChildren:   StoryNode[];
  sourceChildren: StoryNode[];
  createChild:    (source: StoryNode) => StoryNode;
}

// ─── UpdateReport / NodeSnapshot ─────────────────────────────────────────────

class NodeSnapshot {
  readonly name:           NodeName;
  readonly sequentialOrder: number;
  readonly childSnapshots: NodeSnapshot[];

  private constructor(name: NodeName, sequentialOrder: number, childSnapshots: NodeSnapshot[]) {
    this.name            = name;
    this.sequentialOrder = sequentialOrder;
    this.childSnapshots  = childSnapshots;
  }

  static of(node: StoryNode): NodeSnapshot {
    const childSnapshots = node.children().map(NodeSnapshot.of);
    return new NodeSnapshot(node.name, node.sequentialOrder, childSnapshots);
  }

  restoreInto(node: StoryNode): void {
    node.name            = this.name;
    node.sequentialOrder = this.sequentialOrder;
    const nodeChildren   = node.children();
    this.childSnapshots.forEach((snap, i) => snap.restoreInto(nodeChildren[i]));
  }
}

class UpdateReport {
  readonly changes:  string[]      = [];
  snapshot!:         NodeSnapshot;

  captureSnapshot(node: StoryNode): void {
    this.snapshot = NodeSnapshot.of(node);
  }

  addExactMatch(selfName: NodeName, sourceName: NodeName): void {
    this.changes.push(`exact-match: ${selfName} ← ${sourceName}`);
  }
  addRename(from: NodeName, to: NodeName, confidence: number): void {
    this.changes.push(`rename: ${from} → ${to} (${confidence})`);
  }
  addNew(node: StoryNode): void {
    this.changes.push(`new: ${node.name}`);
  }
  addRemoved(node: StoryNode): void {
    this.changes.push(`removed: ${node.name}`);
  }
  addSubEpicSiblingReorder(a: NodeName, b: NodeName): void {
    this.changes.push(`reorder-sub-epic: ${a} ↔ ${b}`);
  }
  addStoryGroupReorder(a: NodeName, b: NodeName): void {
    this.changes.push(`reorder-story: ${a} ↔ ${b}`);
  }

  reverseOn(node: StoryNode): void {
    this.snapshot.restoreInto(node);
  }
}

// ─── Story Hierarchy (Layer 1 — domain) ──────────────────────────────────────

abstract class StoryNode {
  name:            NodeName;
  sequentialOrder: number;
  behavior:        string = '';

  constructor(name: NodeName, sequentialOrder: number) {
    this.name            = name;
    this.sequentialOrder = sequentialOrder;
  }

  // Fixed algorithm — never overridden.
  translateFrom(source: StoryNode): UpdateReport {
    const report = new UpdateReport();
    report.captureSnapshot(this);
    this.updateSelf(source);
    for (const pair of this.childCollections(source)) {
      this.reconcileCollection(pair, report);
    }
    return report;
  }

  reverse(report: UpdateReport): void {
    report.reverseOn(this);
  }

  children(): StoryNode[] {
    return this.childCollections(this).flatMap(p => p.selfChildren);
  }

  // Extension points — overridden per subclass.
  abstract updateSelf(source: StoryNode): void;
  abstract childCollections(source: StoryNode): ChildCollectionPair[];

  // Private helpers — owned by the fixed algorithm.
  private reconcileCollection(pair: ChildCollectionPair, report: UpdateReport): void {
    const matched = new Set<StoryNode>();
    for (const sourceChild of pair.sourceChildren) {
      const match = this.findMatch(sourceChild.name, sourceChild.sequentialOrder, pair.selfChildren);
      if (match) {
        matched.add(match);
        match.translateFrom(sourceChild);
        report.addExactMatch(match.name, sourceChild.name);
      } else {
        const newChild = pair.createChild(sourceChild);
        pair.selfChildren.push(newChild);
        newChild.translateFrom(sourceChild);
        report.addNew(newChild);
      }
    }
    for (const selfChild of pair.selfChildren) {
      if (!matched.has(selfChild)) {
        report.addRemoved(selfChild);
      }
    }
  }

  private findMatch(name: NodeName, order: number, candidates: StoryNode[]): StoryNode | null {
    return candidates.find(c => c.name === name || c.sequentialOrder === order) ?? null;
  }
}

class Epic extends StoryNode {
  domainConcepts: DomainConcept[] = [];
  subEpics:       SubEpic[]       = [];

  constructor(name: NodeName, sequentialOrder: number) { super(name, sequentialOrder); }

  updateSelf(source: Epic): void {
    this.name            = source.name;
    this.sequentialOrder = source.sequentialOrder;
    this.domainConcepts  = source.domainConcepts;
  }

  childCollections(source: Epic): ChildCollectionPair[] {
    return [{
      selfChildren:   this.subEpics,
      sourceChildren: source.subEpics,
      createChild:    (s) => this.createChildSubEpic(s as SubEpic),
    }];
  }

  createChildSubEpic(source: SubEpic): SubEpic {
    return new SubEpic(source.name, source.sequentialOrder);
  }
}

class SubEpic extends StoryNode {
  hasSubEpics:    boolean         = false;
  testFile:       FilePath        = '';
  domainConcepts: DomainConcept[] = [];
  subEpics:       SubEpic[]       = [];
  stories:        Story[]         = [];

  constructor(name: NodeName, sequentialOrder: number) { super(name, sequentialOrder); }

  updateSelf(source: SubEpic): void {
    this.name            = source.name;
    this.sequentialOrder = source.sequentialOrder;
    this.hasSubEpics     = source.hasSubEpics;
    this.testFile        = source.testFile;
    this.domainConcepts  = source.domainConcepts;
  }

  // sub-epics reconciled before stories so depth is known before row positions are computed
  childCollections(source: SubEpic): ChildCollectionPair[] {
    return [
      {
        selfChildren:   this.subEpics,
        sourceChildren: source.subEpics,
        createChild:    (s) => this.createChildSubEpic(s as SubEpic),
      },
      {
        selfChildren:   this.stories,
        sourceChildren: source.stories,
        createChild:    (s) => this.createChildStory(s as Story),
      },
    ];
  }

  createChildSubEpic(source: SubEpic): SubEpic {
    return new SubEpic(source.name, source.sequentialOrder);
  }
  createChildStory(source: Story): Story {
    return new Story(source.name, source.sequentialOrder, source.storyType);
  }

  allStoriesRecursive(): Story[] {
    return [
      ...this.subEpics.flatMap(se => se.allStoriesRecursive()),
      ...this.stories,
    ];
  }
}

class Story extends StoryNode {
  storyType:          StoryType           = 'user';
  users:              StoryUser[]         = [];
  acceptanceCriteria: AcceptanceCriteria[] = [];

  constructor(name: NodeName, sequentialOrder: number, storyType: StoryType = 'user') {
    super(name, sequentialOrder);
    this.storyType = storyType;
  }

  updateSelf(source: Story): void {
    this.name            = source.name;
    this.sequentialOrder = source.sequentialOrder;
    this.storyType       = source.storyType;
    this.users           = source.users;
  }

  childCollections(source: Story): ChildCollectionPair[] {
    return [{
      selfChildren:   this.acceptanceCriteria,
      sourceChildren: source.acceptanceCriteria,
      createChild:    (s) => this.createChildAcceptanceCriteria(s as AcceptanceCriteria),
    }];
  }

  createChildAcceptanceCriteria(source: AcceptanceCriteria): AcceptanceCriteria {
    return new AcceptanceCriteria(source.criteriaText, source.sequentialOrder);
  }
}

class AcceptanceCriteria extends StoryNode {
  criteriaText: CriteriaText;

  constructor(criteriaText: CriteriaText, sequentialOrder: number) {
    super(criteriaText, sequentialOrder);
    this.criteriaText = criteriaText;
  }

  updateSelf(source: AcceptanceCriteria): void {
    this.criteriaText    = source.criteriaText;
    this.sequentialOrder = source.sequentialOrder;
  }

  childCollections(_source: AcceptanceCriteria): ChildCollectionPair[] {
    return []; // leaf node
  }
}

// ─── Boundary Domain ─────────────────────────────────────────────────────────

abstract class BackendElement {
  cellId: CellId = '';
  value:  string = '';

  abstract position(): Position;
  abstract boundary(): Boundary;
  abstract setPosition(x: number, y: number): void;
  abstract setSize(width: number, height: number): void;
  setValue(text: string): void { this.value = text; }
  abstract applyStyleForType(styleKey: StyleKey): void;
}

class DrawIOElement extends BackendElement {
  private _position: Position = { x: 0, y: 0 };
  private _boundary: Boundary = { position: this._position, width: 0, height: 0 };

  position(): Position { return this._position; }
  boundary(): Boundary { return this._boundary; }
  setPosition(x: number, y: number): void { this._position = { x, y }; }
  setSize(width: number, height: number): void {
    this._boundary = { position: this._position, width, height };
  }
  applyStyleForType(_styleKey: StyleKey): void { /* writes mxCell style attribute */ }
  toXml(): XmlString { return `<mxCell value="${this.value}" id="${this.cellId}" />`; }
}

class MiroElement extends BackendElement {
  private _position: Position = { x: 0, y: 0 };
  private _boundary: Boundary = { position: this._position, width: 0, height: 0 };

  position(): Position { return this._position; }
  boundary(): Boundary { return this._boundary; }
  setPosition(x: number, y: number): void { this._position = { x, y }; }
  setSize(width: number, height: number): void {
    this._boundary = { position: this._position, width, height };
  }
  applyStyleForType(_styleKey: StyleKey): void { /* writes Miro shape/style field */ }
  toApiPayload(): JsonPayload { return { type: 'sticky_note', data: { content: this.value } }; }
}

// ─── Layout constants ─────────────────────────────────────────────────────────

const EPIC_Y         = 20;
const EPIC_HEIGHT    = 30;
const SUB_EPIC_HEIGHT = 30;
const ROW_GAP        = 10;
const ACTOR_GAP      = 20;
const CELL_SIZE      = 80;

// ─── RowPositions (ValueObject) ───────────────────────────────────────────────

class RowPositions {
  readonly maxDepth: number;

  constructor(maxDepth: number) { this.maxDepth = maxDepth; }

  subEpicY(depth: number): number {
    return EPIC_Y + EPIC_HEIGHT + ROW_GAP + depth * (SUB_EPIC_HEIGHT + ROW_GAP);
  }
  actorY(): number {
    return this.subEpicY(this.maxDepth) + SUB_EPIC_HEIGHT + ACTOR_GAP;
  }
  storyY(): number {
    return this.actorY() + CELL_SIZE + ROW_GAP;
  }
  yFor(node: DiagramStoryNode): number {
    if (node instanceof DiagramEpic)    return EPIC_Y;
    if (node instanceof DiagramSubEpic) return this.subEpicY(node.depth);
    if (node instanceof DiagramStory)   return this.storyY();
    return 0;
  }
}

// ─── Diagram mixin (Layer 2) ──────────────────────────────────────────────────
//
// Because TypeScript does not support multiple inheritance, the diagram layer
// is applied as a mixin over any StoryNode subclass.
// DiagramEpic    = DiagramMixin(Epic)
// DiagramSubEpic = DiagramMixin(SubEpic)
// DiagramStory   = DiagramMixin(Story)

type DiagramStoryNode = InstanceType<ReturnType<typeof DiagramMixin>>;

function DiagramMixin<TBase extends Constructor<StoryNode>>(Base: TBase) {
  return class extends Base {
    // updateSelf extends the domain layer to also set position + size
    updateSelf(source: StoryNode): void {
      super.updateSelf(source);
      const rows      = new RowPositions(maxSubEpicDepth(source));
      const placement = this.placementRules();
      this.setPosition(placement.x, rows.yFor(this as unknown as DiagramStoryNode));
      this.setSize(placement.width, placement.height);
      this.applyFormatting(this.formattingRules());
    }

    // Overridden by each concrete class.
    containmentRules(): ContainmentRule {
      return { allowedParents: [], allowedChildren: [] };
    }
    placementRules(): PlacementRule {
      return { x: 0, yStrategy: 'fixed', height: 0, widthStrategy: 'span-children' };
    }
    formattingRules(): FormattingRule {
      return { styleKey: '' };
    }

    // Delegated to BackendElement — overridden by BackendStoryNode.
    setPosition(_x: number, _y: number): void { /* abstract */ }
    setSize(_width: number, _height: number): void { /* abstract */ }
    applyFormatting(_rules: FormattingRule): void { /* abstract */ }
  };
}

// Compute max sub-epic depth of a node tree (used by RowPositions).
function maxSubEpicDepth(node: StoryNode, depth = 0): number {
  if (node instanceof SubEpic) {
    return Math.max(depth, ...node.subEpics.map(se => maxSubEpicDepth(se, depth + 1)));
  }
  if (node instanceof Epic) {
    return Math.max(0, ...node.subEpics.map(se => maxSubEpicDepth(se, 0)));
  }
  return depth;
}

class DiagramEpic extends DiagramMixin(Epic) {
  override placementRules(): PlacementRule {
    return { x: 0, yStrategy: 'fixed', height: EPIC_HEIGHT, widthStrategy: 'span-children' };
  }
  override createChildSubEpic(source: SubEpic): SubEpic {
    return new DiagramSubEpic(source.name, source.sequentialOrder);
  }
}

class DiagramSubEpic extends DiagramMixin(SubEpic) {
  depth: number = 0;

  override placementRules(): PlacementRule {
    return { x: 0, yStrategy: 'sub-epic-y', height: SUB_EPIC_HEIGHT, widthStrategy: 'span-children' };
  }
  override createChildSubEpic(source: SubEpic): DiagramSubEpic {
    const child = new DiagramSubEpic(source.name, source.sequentialOrder);
    child.depth = this.depth + 1;
    return child;
  }
  override createChildStory(source: Story): DiagramStory {
    return new DiagramStory(source.name, source.sequentialOrder, source.storyType);
  }
}

class DiagramStory extends DiagramMixin(Story) {
  override placementRules(): PlacementRule {
    return { x: 0, yStrategy: 'story-y', height: CELL_SIZE, widthStrategy: 'fixed-cell' };
  }
}

// ─── Backend mixin (Layer 3) ──────────────────────────────────────────────────
//
// BackendMixin wraps any DiagramMixin-extended class and adds the held
// BackendElement plus serialization in updateSelf.

function BackendMixin<TBase extends Constructor<StoryNode>>(Base: TBase) {
  return class extends Base {
    element!: BackendElement;
    cellId:   CellId = '';

    position(): Position { return this.element.position(); }
    boundary(): Boundary { return this.element.boundary(); }

    override setPosition(x: number, y: number): void { this.element.setPosition(x, y); }
    override setSize(width: number, height: number): void { this.element.setSize(width, height); }
    override applyFormatting(rules: FormattingRule): void {
      this.element.applyStyleForType(rules.styleKey);
    }

    // updateSelf extends the diagram layer to also serialize to element
    override updateSelf(source: StoryNode): void {
      super.updateSelf(source);
      this.element.setValue(this.name);
      this.element.applyStyleForType(this.formattingRules().styleKey);
    }

    collectAllNodes(): this[] {
      const result: this[] = [this];
      for (const pair of this.childCollections(this)) {
        for (const child of pair.selfChildren) {
          result.push(...(child as this).collectAllNodes());
        }
      }
      return result;
    }
  };
}

// ─── DrawIO backend (concrete layer) ─────────────────────────────────────────

class DrawIOEpic extends BackendMixin(DiagramEpic) {
  constructor(name: NodeName, sequentialOrder: number) {
    super(name, sequentialOrder);
    this.element = new DrawIOElement();
  }

  override createChildSubEpic(source: SubEpic): DrawIOSubEpic {
    return new DrawIOSubEpic(source.name, source.sequentialOrder);
  }
}

class DrawIOSubEpic extends BackendMixin(DiagramSubEpic) {
  constructor(name: NodeName, sequentialOrder: number) {
    super(name, sequentialOrder);
    this.element = new DrawIOElement();
  }

  override createChildSubEpic(source: SubEpic): DrawIOSubEpic {
    const child = new DrawIOSubEpic(source.name, source.sequentialOrder);
    child.depth = this.depth + 1;
    return child;
  }
  override createChildStory(source: Story): DrawIOStory {
    return new DrawIOStory(source.name, source.sequentialOrder, source.storyType);
  }
}

class DrawIOStory extends BackendMixin(DiagramStory) {
  constructor(name: NodeName, sequentialOrder: number, storyType: StoryType = 'user') {
    super(name, sequentialOrder, storyType);
    this.element = new DrawIOElement();
  }
}

// ─── Miro backend (concrete layer) ───────────────────────────────────────────

class MiroEpic extends BackendMixin(DiagramEpic) {
  constructor(name: NodeName, sequentialOrder: number) {
    super(name, sequentialOrder);
    this.element = new MiroElement();
  }

  override createChildSubEpic(source: SubEpic): MiroSubEpic {
    return new MiroSubEpic(source.name, source.sequentialOrder);
  }
}

class MiroSubEpic extends BackendMixin(DiagramSubEpic) {
  constructor(name: NodeName, sequentialOrder: number) {
    super(name, sequentialOrder);
    this.element = new MiroElement();
  }

  override createChildSubEpic(source: SubEpic): MiroSubEpic {
    const child = new MiroSubEpic(source.name, source.sequentialOrder);
    child.depth = this.depth + 1;
    return child;
  }
  override createChildStory(source: Story): MiroStory {
    return new MiroStory(source.name, source.sequentialOrder, source.storyType);
  }
}

class MiroStory extends BackendMixin(DiagramStory) {
  constructor(name: NodeName, sequentialOrder: number, storyType: StoryType = 'user') {
    super(name, sequentialOrder, storyType);
    this.element = new MiroElement();
  }
}

// ─── Exports ─────────────────────────────────────────────────────────────────

export {
  // Value types
  StoryType,
  // Core hierarchy
  StoryNode, Epic, SubEpic, Story, AcceptanceCriteria,
  // Diagram layer
  DiagramEpic, DiagramSubEpic, DiagramStory, RowPositions,
  // DrawIO backend
  DrawIOEpic, DrawIOSubEpic, DrawIOStory, DrawIOElement,
  // Miro backend
  MiroEpic, MiroSubEpic, MiroStory, MiroElement,
  // Translation result
  UpdateReport, NodeSnapshot,
  // Types
  ChildCollectionPair, Position, Boundary,
};
