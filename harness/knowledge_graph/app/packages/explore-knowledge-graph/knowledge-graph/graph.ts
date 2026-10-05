/**
 * knowledge-graph.ts — domain core.
 *
 * Framework-free: no Express, no React, no lowdb.
 * KnowledgeGraph is the aggregate root. KnowledgeGraphRepository
 * load / create / search / update that root.
 *
 * Sources: harness/knowledge_graph/.context/module-context.md,
 * knowledge-graph-explorer-sketch.md, graph_node.py Kind.
 */
import { z } from 'zod';
import {
  INVERSE_KIND,
  NODE_TYPES_BY_PRACTICE,
  PRACTICES,
  RELATIONSHIP_KINDS,
  STAGES,
  RULE_GUIDANCE,
  closestFidelity,
  stageFor,
} from './catalog';

export const KEEP_OPERATIONS_SMALL_FOCUSED = 'keep-operations-small-focused';

export const CLASS_KINDS = new Set([
  'OoadClass',
  'Entity',
  'EntityRoot',
  'ValueObject',
  'Repository',
  'DomainService',
  'DomainEvent',
  'Specification',
  'Factory',
]);

export function isClassKind(kind: string): boolean {
  return CLASS_KINDS.has(kind);
}

const STEP_KEYWORD = /^(Given|When|Then|And|But)\s/i;
const STEP_CALL = /(?:^|\n)\s*\.?(given|when|then|and|but)\s*\(/i;

export function stepTitle(
  name: string,
  semanticType: string,
  keyword = '',
  sourceText = '',
): string {
  if (semanticType !== 'Step' || STEP_KEYWORD.test(name)) {
    return name;
  }
  const fromKeyword = keyword.trim();
  const fromSource = sourceText.match(STEP_CALL)?.[1] ?? '';
  const raw = fromKeyword || fromSource;
  if (!raw) {
    return name;
  }
  const label = raw.charAt(0).toUpperCase() + raw.slice(1).toLowerCase();
  return `${label} ${name}`;
}

export const SourceRangeSchema = z.object({
  file: z.string(),
  start_line: z.number().int(),
  end_line: z.number().int(),
  text: z.string().optional().default(''),
});

export const RuleHitSchema = z.object({
  rule_slug: z.string(),
  message: z.string().default(''),
  body: z.string().default(''),
  practice: z.string().default(''),
  fidelity: z.string().nullable().default(null),
  tag: z.string().default('base'),
});

export const NodeSchema = z.object({
  node_id: z.string().min(1),
  name: z.string().min(1),
  practice: z.string(),
  fidelity: z.string().nullable().default(null),
  semantic_type: z.string(),
  sequential_order: z.number().optional(),
  keyword: z.string().optional(),
  properties: z.record(z.string()).default({}),
  applicable_rules: z.array(z.string()).default([]),
  rule_catalog: z
    .array(z.object({ slug: z.string(), tag: z.string().default('base') }))
    .default([]),
  rule_tags: z.record(z.string()).default({}),
  violations: z.array(RuleHitSchema).default([]),
  source: SourceRangeSchema.nullable().default(null),
});

export const RelationshipSchema = z.object({
  kind: z.string(),
  from_id: z.string(),
  to_id: z.string(),
  sequential_order: z.number().int().default(0),
  immediate: z.boolean().default(true),
});

export const PracticeGraphSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  nodes: z.array(NodeSchema).default([]),
  relationships: z.array(RelationshipSchema).default([]),
});

export const KnowledgeGraphSchema = z.object({
  id: z.string().uuid(),
  folder: z.string().default(''),
  practice_graphs: z.array(PracticeGraphSchema),
});

export type SourceRangeDto = z.infer<typeof SourceRangeSchema>;
export type RuleHitDto = z.infer<typeof RuleHitSchema>;
export type NodeDto = z.infer<typeof NodeSchema>;
export type RelationshipDto = z.infer<typeof RelationshipSchema>;
export type PracticeGraphDto = z.infer<typeof PracticeGraphSchema>;
export type KnowledgeGraphDto = z.infer<typeof KnowledgeGraphSchema>;

export type GraphFilter = {
  practices?: string[];
  stages?: string[];
  nodeTypes?: string[];
  relationshipTypes?: string[];
  practice?: string;
  fidelity?: string;
  nodeType?: string;
  relationshipType?: string;
  connectorKind?: string;
  node?: string;
  violations?: boolean;
  rules?: string[];
  rule?: string;
  ruleSources?: string[];
};

export type GraphFilterOptions = {
  practices: string[];
  stages: string[];
  node_types: string[];
  relationship_types: string[];
  rules: string[];
  rule_sources: string[];
};

export type ListedRule = {
  slug: string;
  tag: string;
  status: 'passing' | 'violating';
  body: string;
  message: string;
  practice: string;
  fidelity: string;
};

export type CreateKnowledgeGraphInput = {
  folder?: string;
  practiceGraphs: PracticeGraphDto[];
};

export type ListedRelatedNode = {
  node_id: string;
  name: string;
  semantic_type: string;
  practice: string;
};

export type ListedRelationshipKind = {
  kind: string;
  targets: ListedRelatedNode[];
};

export type ListedTreeNode = {
  node_id: string;
  name: string;
  path: string;
  practice: string;
  semantic_type: string;
  is_file: boolean;
  properties: Record<string, string>;
  rule_statuses: Record<string, 'passing' | 'violating'>;
  rules: ListedRule[];
  relationships: ListedRelationshipKind[];
  source: SourceRangeDto | null;
  origin: SourceRangeDto | null;
  failed: number;
  total: number;
  children: ListedTreeNode[];
};

export class RuleHit {
  constructor(private readonly dto: RuleHitDto) {}

  get ruleSlug(): string {
    return this.dto.rule_slug;
  }

  get message(): string {
    return this.dto.message;
  }

  get body(): string {
    return this.dto.body;
  }

  get practice(): string {
    return this.dto.practice;
  }

  get fidelity(): string {
    return this.dto.fidelity ?? '';
  }

  get tag(): string {
    return this.dto.tag || 'base';
  }
}

export class NodeRules {
  constructor(
    private readonly applicableRules: readonly string[],
    private readonly hits: readonly RuleHit[],
    private readonly catalog: readonly { slug: string; tag: string }[] = [],
    private readonly ruleTags: Record<string, string> = {},
  ) {}

  get violations(): RuleHit[] {
    return [...this.hits];
  }

  get applicable(): readonly string[] {
    return this.applicableRules;
  }

  statuses(): Record<string, 'passing' | 'violating'> {
    const result: Record<string, 'passing' | 'violating'> = {};
    for (const slug of this.applicableRules) {
      result[slug] = this.status(slug) === 'violating' ? 'violating' : 'passing';
    }
    return result;
  }

  status(ruleSlug: string): 'passing' | 'violating' | 'absent' {
    if (!this.hasRule(ruleSlug)) {
      return 'absent';
    }
    if (this.hits.some((hit) => hit.ruleSlug === ruleSlug)) {
      return 'violating';
    }
    return 'passing';
  }

  hasRule(ruleSlug: string): boolean {
    if (this.catalog.some((entry) => entry.slug === ruleSlug)) {
      return true;
    }
    return this.applicableRules.includes(ruleSlug);
  }

  details(): ListedRule[] {
    return this._entries().map((entry) => {
      const hit = this.hits.find(
        (item) => item.ruleSlug === entry.slug && item.tag === entry.tag,
      );
      return listedRuleFromHit(entry.slug, hit, entry.tag);
    });
  }

  private _entries(): { slug: string; tag: string }[] {
    if (this.catalog.length > 0) {
      return this.catalog.map((entry) => ({
        slug: entry.slug,
        tag: entry.tag || 'base',
      }));
    }
    const slugs = this.applicableRules.length
      ? [...this.applicableRules]
      : [...new Set(this.hits.map((hit) => hit.ruleSlug))];
    return slugs.map((slug) => ({ slug, tag: this._tagForSlug(slug) }));
  }

  private _tagForSlug(slug: string): string {
    const hit = this.hits.find((item) => item.ruleSlug === slug);
    if (hit) {
      return hit.tag || 'base';
    }
    const catalog = this.catalog.find((entry) => entry.slug === slug);
    if (catalog) {
      return catalog.tag || 'base';
    }
    return this.ruleTags[slug] || 'base';
  }

  tally(): { failed: number; total: number } {
    const failed = new Set(this.hits.map((hit) => hit.ruleSlug)).size;
    return { failed, total: Math.max(this.applicableRules.length, failed) };
  }
}

export class GraphNode {
  private _rules: NodeRules | null = null;

  constructor(private readonly dto: NodeDto) {}

  get nodeId(): string {
    return this.dto.node_id;
  }

  get name(): string {
    return this.dto.name;
  }

  get practice(): string {
    return this.dto.practice;
  }

  get fidelity(): string | null {
    return this.dto.fidelity;
  }

  get stage(): string {
    return stageFor(this.dto.fidelity) || stageFor(closestFidelity(this.practice, this.semanticType));
  }

  get semanticType(): string {
    return this.dto.semantic_type;
  }

  get sequentialOrder(): number {
    return this.dto.sequential_order ?? 0;
  }

  get keyword(): string {
    return this.dto.keyword ?? '';
  }

  get properties(): Record<string, string> {
    return { ...this.dto.properties };
  }

  get rules(): NodeRules {
    if (!this._rules) {
      const hits = this.dto.violations.map((hit) => new RuleHit(hit));
      this._rules = new NodeRules(
        this.dto.applicable_rules,
        hits,
        this.dto.rule_catalog ?? [],
        this.dto.rule_tags ?? {},
      );
    }
    return this._rules;
  }

  get source(): SourceRangeDto | null {
    return this.dto.source;
  }

  get isFile(): boolean {
    return this.dto.source !== null;
  }

  get isFolder(): boolean {
    return this.dto.source === null;
  }

  static fromDto(dto: NodeDto): GraphNode {
    return new GraphNode(dto);
  }
}

export class Relationship {
  constructor(private readonly dto: RelationshipDto) {}

  get kind(): string {
    return this.dto.kind;
  }

  get fromId(): string {
    return this.dto.from_id;
  }

  get toId(): string {
    return this.dto.to_id;
  }

  get sequentialOrder(): number {
    return this.dto.sequential_order;
  }

  get immediate(): boolean {
    return this.dto.immediate;
  }

  static fromDto(dto: RelationshipDto): Relationship {
    return new Relationship(dto);
  }
}

export class PracticeGraph {
  constructor(private readonly dto: PracticeGraphDto) {}

  get id(): string {
    return this.dto.id;
  }

  get name(): string {
    return this.dto.name;
  }

  get nodes(): GraphNode[] {
    return this.dto.nodes.map((node) => GraphNode.fromDto(node));
  }

  get relationships(): Relationship[] {
    return this.dto.relationships.map((edge) => Relationship.fromDto(edge));
  }

  static fromDto(dto: PracticeGraphDto): PracticeGraph {
    return new PracticeGraph(dto);
  }
}

export class KnowledgeGraph {
  private _nodes: GraphNode[] | null = null;
  private _byId: Map<string, GraphNode> | null = null;
  private _owns: Array<{ fromId: string; toId: string }> | null = null;
  private _treeOwns: Array<{ fromId: string; toId: string }> | null = null;
  private _edges: RelationshipDto[] | null = null;
  private _fromEdges: Map<string, RelationshipDto[]> | null = null;
  private _ownerOf: Map<string, string> | null = null;
  private _ownedNames: Map<string, Map<string, string>> | null = null;
  private _kinds: Map<string, Set<string>> | null = null;
  private _related: Map<string, ListedRelationshipKind[]> | null = null;

  constructor(
    private readonly dto: KnowledgeGraphDto,
    private readonly view: {
      selectedNodeId: string | null;
      selectedRuleSlug: string | null;
      filter: GraphFilter;
    } = { selectedNodeId: null, selectedRuleSlug: null, filter: {} },
  ) {}

  get id(): string {
    return this.dto.id;
  }

  get folder(): string {
    return this.dto.folder;
  }

  get practiceGraphs(): PracticeGraph[] {
    return this.dto.practice_graphs.map((graph) => PracticeGraph.fromDto(graph));
  }

  browse(): GraphNode[] {
    return this.listedNodes();
  }

  listedNodes(): GraphNode[] {
    return this._allNodes().filter((node) => this._matchesFilter(node));
  }

  selectNode(nodeId: string, ruleSlug?: string | null): KnowledgeGraph {
    return this._withView({
      ...this.view,
      selectedNodeId: nodeId,
      selectedRuleSlug: ruleSlug ?? null,
    });
  }

  followRelationship(toId: string): KnowledgeGraph {
    return this.selectNode(toId);
  }

  filterGraph(filter: GraphFilter): KnowledgeGraph {
    return this._withView({
      ...this.view,
      filter,
    });
  }

  get selectedNode(): GraphNode | null {
    if (!this.view.selectedNodeId) {
      return null;
    }
    return this._nodeById(this.view.selectedNodeId);
  }

  get sourceFile(): SourceRangeDto | null {
    const selected = this.selectedNode;
    if (!selected) {
      return null;
    }
    if (selected.source?.file) {
      return selected.source;
    }
    return this._classSource(selected.name);
  }

  toDto(): KnowledgeGraphDto {
    return this.dto;
  }

  present() {
    const listedTree = this._listedTree();
    return {
      knowledge_graph: this.dto,
      folder: this.folder,
      filter: this.view.filter,
      filter_options: this._filterOptions(),
      listed_nodes: this.listedNodes().map((node) => this._listedLeaf(node)),
      listed_tree: listedTree,
      selected_node: this.selectedNode
        ? {
            node_id: this.selectedNode.nodeId,
            name: this.selectedNode.name,
            practice: this.selectedNode.practice,
            stage: this.selectedNode.stage,
            semantic_type: this.selectedNode.semanticType,
            is_file: this.selectedNode.isFile,
            is_folder: this.selectedNode.isFolder,
            rules: this._listedRules(this.selectedNode),
          }
        : null,
      selected_tree: this._sourcePane(findListedNode(listedTree, this.view.selectedNodeId)),
      selected_rule: this._selectedRule(),
      source_file: this.sourceFile,
    };
  }

  presentSelection(_listedTree?: ListedTreeNode[]) {
    const selected = this.selectedNode;
    return {
      selected_node: selected
        ? {
            node_id: selected.nodeId,
            name: selected.name,
            practice: selected.practice,
            stage: selected.stage,
            semantic_type: selected.semanticType,
            is_file: selected.isFile,
            is_folder: selected.isFolder,
            rules: this._listedRules(selected),
          }
        : null,
      selected_tree: selected ? this._sourcePane(this._paneClass(selected)) : null,
      selected_rule: this._selectedRule(),
      source_file: this.sourceFile,
    };
  }

  selectionSourceRanges(): SourceRangeDto[] {
    const selected = this.selectedNode;
    if (!selected) {
      return [];
    }
    this._ensureRelationIndex();
    const keep = new Set<string>([selected.nodeId]);
    let frontier = [selected.nodeId];
    for (let depth = 0; depth < 5; depth += 1) {
      const next: string[] = [];
      const add = (id: string) => {
        if (!id || keep.has(id)) {
          return;
        }
        keep.add(id);
        next.push(id);
      };
      for (const id of frontier) {
        const owner = this._owningClassNode(id);
        if (owner) {
          add(owner.nodeId);
        }
        for (const edge of this._fromEdges?.get(id) ?? []) {
          if (edge.kind === 'invokes' || edge.kind === 'hasType' || edge.kind === 'demonstrates') {
            add(edge.to_id);
          }
        }
        const text = this._nodeById(id)?.source?.text ?? '';
        if (!text) {
          continue;
        }
        for (const member of memberCallLabels(text).keys()) {
          const found = this._memberNamed(member, owner);
          if (found) {
            add(found.nodeId);
          }
        }
      }
      frontier = next;
    }
    const ranges: SourceRangeDto[] = [];
    const seen = new Set<string>();
    for (const id of keep) {
      const source = this._nodeById(id)?.source;
      if (!source?.file || source.text) {
        continue;
      }
      const key = `${source.file}:${source.start_line}:${source.end_line}`;
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      ranges.push(source);
    }
    return ranges;
  }

  hydrateSource(ranges: SourceRangeDto[]): void {
    const texts = new Map(
      ranges
        .filter((range) => range.file && range.text)
        .map((range) => [`${range.file}:${range.start_line}:${range.end_line}`, range.text ?? '']),
    );
    if (texts.size === 0) {
      return;
    }
    for (const practice of this.dto.practice_graphs) {
      for (const node of practice.nodes) {
        const source = node.source;
        if (!source?.file) {
          continue;
        }
        const text = texts.get(`${source.file}:${source.start_line}:${source.end_line}`);
        if (text) {
          node.source = { ...source, text };
        }
      }
    }
  }

  static fromDto(dto: KnowledgeGraphDto): KnowledgeGraph {
    return new KnowledgeGraph(
      ensureFolderPackages(dropClonedOperationHits(dropCatalogModules(dto))),
    );
  }

  private _sourcePane(node: ListedTreeNode | null): ListedTreeNode | null {
    if (!node) {
      return node;
    }
    if (isClassKind(node.semantic_type)) {
      return node;
    }
    if (node.semantic_type === 'Operation' || node.semantic_type === 'Property') {
      return this._memberPane(node, 1, new Set());
    }
    if (node.semantic_type === 'Example') {
      return { ...node, children: this._classesForExample(node.node_id).map((cls) => this._paneClass(cls)) };
    }
    if (node.semantic_type === 'Step') {
      return {
        ...node,
        children: [
          ...node.children.filter(
            (child) => child.semantic_type === 'Example' || child.semantic_type === 'Step',
          ),
          ...this._operationsForStep(node),
          ...this._observedForStep(node),
          ...this._classesForStep(node).map((cls) => this._paneClass(cls)),
        ],
      };
    }
    return node;
  }

  private _withoutMembers(children: ListedTreeNode[]): ListedTreeNode[] {
    return children
      .filter(
        (child) =>
          child.semantic_type !== 'Property' &&
          child.semantic_type !== 'Operation' &&
          child.semantic_type !== 'Parameter' &&
          child.semantic_type !== 'FieldGroup',
      )
      .map((child) => ({ ...child, children: this._withoutMembers(child.children) }));
  }

  private _memberPane(node: ListedTreeNode, depth: number, stack: Set<string>): ListedTreeNode {
    const owner = this._owningClassNode(node.node_id);
    const types =
      node.semantic_type === 'Property'
        ? this._propertyClasses(node)
        : this._referencedTypeNodes(node, owner);
    const typeNodes = types.map((typeNode) => this._paneClass(typeNode));
    if (owner && !typeNodes.some((typeNode) => typeNode.node_id === owner.nodeId)) {
      typeNodes.push(this._paneClass(owner));
    }
    const calls = depth >= 5 ? [] : this._directCalls(node, stack);
    const next = new Set(stack);
    next.add(node.node_id);
    return {
      ...node,
      children: [
        ...typeNodes,
        ...calls.map((call) => this._memberPane(call, depth + 1, next)),
      ],
    };
  }

  private _directCalls(caller: ListedTreeNode, stack: Set<string>): ListedTreeNode[] {
    const labels = memberCallLabels(caller.source?.text ?? '');
    const byName = new Map<string, GraphNode>();
    const owner = this._owningClassNode(caller.node_id);
    for (const member of labels.keys()) {
      const named = this._memberNamed(member, owner);
      if (
        named &&
        named.nodeId !== caller.node_id &&
        !stack.has(named.nodeId) &&
        (named.semanticType === 'Operation' || named.semanticType === 'Property')
      ) {
        if (
          caller.semantic_type === 'Operation' &&
          named.semanticType === 'Property' &&
          isSimpleProperty(named.source?.text ?? '')
        ) {
          continue;
        }
        byName.set(named.name, named);
      }
    }
    for (const edge of this._fromEdges?.get(caller.node_id) ?? []) {
      if (edge.kind !== 'invokes') {
        continue;
      }
      const target = this._nodeById(edge.to_id);
      if (!target || target.nodeId === caller.node_id || stack.has(target.nodeId)) {
        continue;
      }
      if (target.semanticType !== 'Operation' && target.semanticType !== 'Property') {
        continue;
      }
      if (
        caller.semantic_type === 'Operation' &&
        target.semanticType === 'Property' &&
        isSimpleProperty(target.source?.text ?? '')
      ) {
        continue;
      }
      byName.set(target.name, target);
    }
    const ordered: ListedTreeNode[] = [];
    const used = new Set<string>();
    for (const [member, label] of labels) {
      const target = byName.get(member);
      if (!target || used.has(target.nodeId)) {
        continue;
      }
      used.add(target.nodeId);
      ordered.push({ ...this._paneClass(target), name: label });
    }
    for (const target of byName.values()) {
      if (used.has(target.nodeId)) {
        continue;
      }
      const owner = this._owningClassNode(target.nodeId);
      ordered.push({
        ...this._paneClass(target),
        name: owner ? `${owner.name}.${target.name}` : target.name,
      });
    }
    return ordered;
  }

  private _propertyClasses(property: ListedTreeNode): GraphNode[] {
    const names = new Set(fieldTypeNames(property.source?.text ?? ''));
    for (const group of property.relationships) {
      if (group.kind !== 'hasType') {
        continue;
      }
      for (const target of group.targets) {
        names.add(target.name);
      }
    }
    for (const edge of this._fromEdges?.get(property.node_id) ?? []) {
      if (edge.kind !== 'hasType') {
        continue;
      }
      const target = this._nodeById(edge.to_id);
      if (target) {
        names.add(target.name);
      }
    }
    const owner = this._owningClassNode(property.node_id);
    return this._classesNamed(names, new Set(owner ? [owner.nodeId] : []));
  }

  private _classesNamed(names: Iterable<string>, exclude: Set<string>): GraphNode[] {
    const found: GraphNode[] = [];
    const seen = new Set(exclude);
    for (const name of names) {
      if (SKIP_TYPES.has(name)) {
        continue;
      }
      const matches = this._allNodes().filter(
        (node) => isClassKind(node.semanticType) && node.name === name,
      );
      const match = matches.find((node) => node.source?.text) ?? matches[0];
      if (!match || seen.has(match.nodeId)) {
        continue;
      }
      seen.add(match.nodeId);
      found.push(match);
    }
    return found;
  }

  private _operationsForStep(step: ListedTreeNode): ListedTreeNode[] {
    const found: ListedTreeNode[] = [];
    const seen = new Set<string>();
    for (const edge of this._allEdges()) {
      if (edge.kind !== 'invokes' || edge.from_id !== step.node_id) {
        continue;
      }
      const operation = this._nodeById(edge.to_id);
      if (!operation || operation.semanticType !== 'Operation' || seen.has(operation.nodeId)) {
        continue;
      }
      seen.add(operation.nodeId);
      const listed = this._listedLeaf(operation);
      found.push(
        this._memberPane(
          {
            ...listed,
            path: listed.name,
            origin: listed.source,
            children: [],
          },
          1,
          new Set(),
        ),
      );
    }
    return found;
  }

  private _observedForStep(step: ListedTreeNode): ListedTreeNode[] {
    const found: ListedTreeNode[] = [];
    const seen = new Set<string>();
    const exampleIds = new Set(
      step.children.filter((child) => child.semantic_type === 'Example').map((child) => child.node_id),
    );
    for (const edge of this._allEdges()) {
      if (edge.kind === 'owns' && edge.from_id === step.node_id) {
        const owned = this._nodeById(edge.to_id);
        if (owned?.semanticType === 'Example') {
          exampleIds.add(owned.nodeId);
        }
      }
    }
    for (const edge of this._allEdges()) {
      if (
        (edge.kind !== 'retrievedUsing' || !exampleIds.has(edge.from_id)) &&
        (edge.kind !== 'observes' || edge.from_id !== step.node_id)
      ) {
        continue;
      }
      const member = this._nodeById(edge.to_id);
      if (
        !member ||
        (member.semanticType !== 'Operation' && member.semanticType !== 'Property') ||
        seen.has(member.nodeId)
      ) {
        continue;
      }
      seen.add(member.nodeId);
      const listed = this._listedLeaf(member);
      found.push(
        this._memberPane(
          { ...listed, path: listed.name, origin: listed.source, children: [] },
          1,
          new Set(),
        ),
      );
    }
    return found;
  }

  private _classesForExample(exampleId: string): GraphNode[] {
    const found: GraphNode[] = [];
    const seen = new Set<string>();
    for (const edge of this._allEdges()) {
      if (edge.kind !== 'demonstrates' || edge.from_id !== exampleId) {
        continue;
      }
      const cls = this._nodeById(edge.to_id);
      if (!cls || !isClassKind(cls.semanticType) || seen.has(cls.nodeId)) {
        continue;
      }
      seen.add(cls.nodeId);
      found.push(cls);
    }
    return found;
  }

  private _classesForStep(step: ListedTreeNode): GraphNode[] {
    const found: GraphNode[] = [];
    const seen = new Set<string>();
    const add = (cls: GraphNode | null) => {
      if (!cls || !isClassKind(cls.semanticType) || seen.has(cls.nodeId)) {
        return;
      }
      seen.add(cls.nodeId);
      found.push(cls);
    };
    for (const edge of this._allEdges()) {
      if (edge.from_id !== step.node_id) {
        continue;
      }
      if (edge.kind === 'owns') {
        const example = this._nodeById(edge.to_id);
        if (example?.semanticType === 'Example') {
          for (const cls of this._classesForExample(example.nodeId)) {
            add(cls);
          }
        }
      }
      if (edge.kind === 'invokes') {
        const operation = this._nodeById(edge.to_id);
        if (!operation || operation.semanticType !== 'Operation') {
          continue;
        }
        const owner = this._owningClassNode(operation.nodeId);
        add(owner);
        const listed = findListedNode([step], operation.nodeId) ?? {
          ...this._paneClass(operation),
        };
        for (const cls of this._referencedTypeNodes(listed, owner)) {
          add(cls);
        }
      }
    }
    for (const child of step.children) {
      if (child.semantic_type !== 'Example') {
        continue;
      }
      for (const cls of this._classesForExample(child.node_id)) {
        add(cls);
      }
    }
    return found;
  }

  private _paneClass(node: GraphNode): ListedTreeNode {
    const leaf = this._listedLeaf(node);
    return {
      ...leaf,
      path: leaf.name,
      origin: leaf.source,
      children: [],
    };
  }

  private _owningClassNode(operationId: string): GraphNode | null {
    this._ensureRelationIndex();
    const ownerId = this._ownerOf?.get(operationId);
    if (!ownerId) {
      return null;
    }
    const owner = this._nodeById(ownerId);
    return owner && isClassKind(owner.semanticType) ? owner : null;
  }

  private _memberNamed(name: string, owner: GraphNode | null): GraphNode | null {
    if (!owner) {
      return null;
    }
    this._ensureRelationIndex();
    let byName = this._ownedNames?.get(owner.nodeId);
    if (!byName) {
      byName = new Map();
      for (const edge of this._fromEdges?.get(owner.nodeId) ?? []) {
        if (edge.kind !== 'owns') {
          continue;
        }
        const member = this._nodeById(edge.to_id);
        if (
          !member ||
          (member.semanticType !== 'Operation' && member.semanticType !== 'Property')
        ) {
          continue;
        }
        if (!byName.has(member.name)) {
          byName.set(member.name, member.nodeId);
        }
      }
      this._ownedNames?.set(owner.nodeId, byName);
    }
    const id = byName.get(name);
    return id ? this._nodeById(id) : null;
  }

  private _ensureRelationIndex(): void {
    if (this._fromEdges) {
      return;
    }
    this._fromEdges = new Map();
    this._ownerOf = new Map();
    this._ownedNames = new Map();
    for (const edge of this._allEdges()) {
      const listed = this._fromEdges.get(edge.from_id);
      if (listed) {
        listed.push(edge);
      } else {
        this._fromEdges.set(edge.from_id, [edge]);
      }
      if (edge.kind === 'owns') {
        this._ownerOf.set(edge.to_id, edge.from_id);
      }
    }
  }

  private _signatureText(operation: ListedTreeNode, owner: GraphNode | null): string {
    return methodSignature(operation.name, operation.source?.text ?? '', owner?.source?.text ?? '');
  }

  private _referencedTypeNodes(operation: ListedTreeNode, owner: GraphNode | null): GraphNode[] {
    const names = new Set<string>(signatureTypeNames(this._signatureText(operation, owner)));
    for (const child of operation.children) {
      if (child.semantic_type !== 'Parameter') {
        continue;
      }
      for (const group of child.relationships) {
        if (group.kind !== 'hasType') {
          continue;
        }
        for (const target of group.targets) {
          names.add(target.name);
        }
      }
    }
    for (const group of operation.relationships) {
      if (group.kind !== 'returns' && group.kind !== 'hasType') {
        continue;
      }
      for (const target of group.targets) {
        names.add(target.name);
      }
    }
    const found: GraphNode[] = [];
    const seen = new Set<string>(owner ? [owner.nodeId] : []);
    for (const name of names) {
      if (SKIP_TYPES.has(name)) {
        continue;
      }
      const match = this._allNodes().find(
        (node) => isClassKind(node.semanticType) && node.name === name,
      );
      if (!match || seen.has(match.nodeId)) {
        continue;
      }
      seen.add(match.nodeId);
      found.push(match);
    }
    return found;
  }

  private _withView(view: {
    selectedNodeId: string | null;
    selectedRuleSlug: string | null;
    filter: GraphFilter;
  }): KnowledgeGraph {
    const next = new KnowledgeGraph(this.dto, view);
    next._nodes = this._nodes;
    next._byId = this._byId;
    next._owns = this._owns;
    next._treeOwns = this._treeOwns;
    next._edges = this._edges;
    next._folderIndex = this._folderIndex;
    next._fromEdges = this._fromEdges;
    next._ownerOf = this._ownerOf;
    next._ownedNames = this._ownedNames;
    next._kinds = this._kinds;
    next._related = this._related;
    return next;
  }

  private _listedLeaf(node: GraphNode) {
    const rules = this._listedRules(node);
    // Tree (failed/total) is a violation rollup. Counting every applicable
    // rule here inflated Module/Operation parents into hundreds of thousands
    // while leaves looked like zeros after most hits were cleared.
    const failed = this._nodeViolationCount(node);
    return {
      node_id: node.nodeId,
      name: this._treeLabel(node),
      practice: node.practice,
      semantic_type: node.semanticType,
      is_file: node.isFile,
      properties: withoutFolder(node.properties),
      rule_statuses: node.rules.statuses(),
      rules,
      applicable_rules: [...node.rules.applicable],
      violations: node.rules.violations.map((hit) => ({
        rule_slug: hit.ruleSlug,
        message: hit.message,
        practice: hit.practice,
        fidelity: hit.fidelity,
      })),
      relationships: this._listedRelationships(node),
      source:
        node.source?.file ||
        ((node.semanticType === 'Step' || node.semanticType === 'Example') && node.source?.text)
          ? node.source
          : node.semanticType === 'Property' || node.semanticType === 'Operation'
            ? node.source
            : this._classSource(node.name),
      failed,
      total: failed,
    };
  }

  private _classSource(name: string): SourceRangeDto | null {
    const key = name.replace(/[^A-Za-z0-9]/g, '').toLowerCase();
    if (!key) {
      return null;
    }
    let match: SourceRangeDto | null = null;
    for (const other of this._allNodes()) {
      if (!isClassKind(other.semanticType) || !other.source?.file) {
        continue;
      }
      const otherKey = other.name.replace(/[^A-Za-z0-9]/g, '').toLowerCase();
      if (otherKey !== key) {
        continue;
      }
      if (other.name === name) {
        return other.source;
      }
      match = other.source;
    }
    return match;
  }

  private _nodeViolationCount(node: GraphNode): number {
    const slugs = listed(this.view.filter.rules, this.view.filter.rule);
    const sources = listed(this.view.filter.ruleSources);
    const seen = new Set<string>();
    for (const hit of node.rules.violations) {
      if (slugs !== null && !slugs.includes(hit.ruleSlug)) {
        continue;
      }
      if (sources !== null && !sources.includes(hit.tag)) {
        continue;
      }
      seen.add(`${hit.ruleSlug}\0${hit.tag}`);
    }
    return seen.size;
  }

  private _listedRules(node: GraphNode): ListedRule[] {
    const slugs = listed(this.view.filter.rules, this.view.filter.rule);
    const sources = listed(this.view.filter.ruleSources);
    const chosen = (rule: { slug: string; tag: string }) =>
      (slugs === null || slugs.includes(rule.slug)) &&
      (sources === null || sources.includes(rule.tag));
    if (this.view.filter.violations) {
      const seen = new Set<string>();
      const violating: ListedRule[] = [];
      for (const hit of node.rules.violations) {
        const tag = hit.tag || 'base';
        const key = `${hit.ruleSlug}\0${tag}`;
        if (seen.has(key) || !chosen({ slug: hit.ruleSlug, tag })) {
          continue;
        }
        seen.add(key);
        violating.push(listedRuleFromHit(hit.ruleSlug, hit, tag));
      }
      return violating;
    }
    return node.rules.details().filter(chosen);
  }

  private _listedRelationships(node: GraphNode): ListedRelationshipKind[] {
    this._relatedByNode();
    const groups = this._related?.get(node.nodeId) ?? [];
    const kinds = listed(
      this.view.filter.relationshipTypes,
      this.view.filter.relationshipType || this.view.filter.connectorKind,
    );
    const chosen = kinds === null ? groups : groups.filter((group) => kinds.includes(group.kind));
    return this._targetsInSelectedPractices(node, chosen);
  }

  private _targetsInSelectedPractices(
    node: GraphNode,
    groups: ListedRelationshipKind[],
  ): ListedRelationshipKind[] {
    const practices = listed(this.view.filter.practices, this.view.filter.practice);
    if (!practices) {
      return groups;
    }
    const classModelOnly = practices.length === 1 && practices[0] === 'clean_engineering';
    return groups
      .map((group) => ({
        ...group,
        targets: group.targets.filter((target) => {
          if (
            classModelOnly &&
            isClassKind(node.semanticType) &&
            group.kind === 'invokes'
          ) {
            return false;
          }
          return practices.includes(target.practice);
        }),
      }))
      .filter((group) => group.targets.length > 0);
  }

  private _relatedByNode(): Map<string, ListedRelationshipKind[]> {
    if (!this._related) {
      const grouped = new Map<
        string,
        Map<string, Map<string, ListedRelatedNode>>
      >();
      const add = (nodeId: string, kind: string, other: GraphNode) => {
        if (!kind || nodeId === other.nodeId) {
          return;
        }
        let byKind = grouped.get(nodeId);
        if (!byKind) {
          byKind = new Map();
          grouped.set(nodeId, byKind);
        }
        let byTarget = byKind.get(kind);
        if (!byTarget) {
          byTarget = new Map();
          byKind.set(kind, byTarget);
        }
        byTarget.set(other.nodeId, {
          node_id: other.nodeId,
          name: this._treeLabel(other),
          semantic_type: other.semanticType,
          practice: other.practice,
        });
      };
      for (const edge of this._allEdges()) {
        const from = this._nodeById(edge.from_id);
        const to = this._nodeById(edge.to_id);
        if (!from || !to) {
          continue;
        }
        add(from.nodeId, edge.kind, to);
        add(to.nodeId, INVERSE_KIND[edge.kind] ?? edge.kind, from);
      }
      const related = new Map<string, ListedRelationshipKind[]>();
      const targetsFor = (byKind: Map<string, Map<string, ListedRelatedNode>>, kind: string) =>
        [...(byKind.get(kind)?.values() ?? [])].sort((left, right) =>
          left.name.localeCompare(right.name),
        );
      for (const [nodeId, byKind] of grouped) {
        const extra = [...byKind.keys()].filter(
          (kind) => !(RELATIONSHIP_KINDS as readonly string[]).includes(kind),
        );
        related.set(
          nodeId,
          [
            ...RELATIONSHIP_KINDS.map((kind) => ({
              kind,
              targets: targetsFor(byKind, kind),
            })),
            ...extra.sort().map((kind) => ({
              kind,
              targets: targetsFor(byKind, kind),
            })),
          ].filter((group) => group.targets.length > 0),
        );
      }
      this._related = related;
    }
    return this._related;
  }

  private _listedTree(): ListedTreeNode[] {
    return this._practiceListedTree();
  }

  private _practiceRootNames(): string[] {
    const selected = listed(this.view.filter.practices, this.view.filter.practice);
    if (selected && selected.length > 0) {
      return selected;
    }
    const present = new Set(
      this.dto.practice_graphs
        .filter((graph) => graph.name && graph.name !== 'workspace' && graph.nodes.length > 0)
        .map((graph) => graph.name),
    );
    return unique([...PRACTICES.filter((name) => present.has(name)), ...present]);
  }

  private _practiceListedTree(): ListedTreeNode[] {
    const practices = this._practiceRootNames();
    const closure = this._practiceClosure();
    const structural = new Set(['StoryMap', 'StoryModel', 'CleanEngineeringModel']);
    const parentOf = this._ownsParents(closure);
    const parentsOf = (nodeId: string) =>
      (parentOf.get(nodeId) ?? [])
        .map((parentId) => closure.get(parentId))
        .filter((parent): parent is GraphNode => Boolean(parent))
        .filter(
          (parent) =>
            !structural.has(parent.semanticType) && parent.semanticType !== 'Package',
        );
    const roots = [...closure.values()].filter((node) => {
      if (structural.has(node.semanticType) || this._isFileNode(node)) {
        return false;
      }
      return parentsOf(node.nodeId).length === 0;
    });
    const sortNodes = (nodes: GraphNode[]) =>
      [...nodes].sort((left, right) => this._compareTreeNodes(left, right));
    const nest = (node: GraphNode, prefix: string, stack: Set<string>): ListedTreeNode => {
      const leaf = this._listedLeaf(node);
      const path = prefix ? `${prefix}.${leaf.name}` : leaf.name;
      const next = new Set(stack);
      next.add(node.nodeId);
      const nested = sortNodes(
        [...closure.values()].filter(
          (child) =>
            !next.has(child.nodeId) &&
            (parentOf.get(child.nodeId) ?? []).includes(node.nodeId),
        ),
      ).map((child) => nest(child, path, next));
      const folded = this._foldBackground(node, leaf, nested);
      return {
        ...leaf,
        name: folded.name,
        source: folded.source,
        path,
        origin: leaf.source?.file ? leaf.source : null,
        children: this._arrangeListedChildren(node, path, folded.children),
        failed: leaf.failed + folded.failed,
        total: leaf.total + folded.total,
      };
    };
    const heads = roots.filter((node) => this._practiceHead(node, practices));
    return practices.map((practice) => {
      const children =
        practice === 'clean_engineering'
          ? this._folderPracticeChildren(practice)
          : sortNodes(heads.filter((node) => node.practice === practice)).map((node) =>
              nest(node, `${practice}.${node.name}`, new Set()),
            );
      return {
        node_id: `practice:${practice}`,
        name: practice,
        path: practice,
        practice,
        semantic_type: 'Practice',
        is_file: false,
        properties: {},
        rule_statuses: {},
        rules: [],
        relationships: [],
        source: null,
        origin: null,
        children,
        failed: children.reduce((sum, child) => sum + child.failed, 0),
        total: children.reduce((sum, child) => sum + child.total, 0),
      };
    });
  }

  private _folderPracticeChildren(practice: string): ListedTreeNode[] {
    const parentOf = new Map<string, string>();
    for (const edge of this._treeOwnsEdges()) {
      const from = this._nodeById(edge.fromId);
      if (from?.practice === 'ddd') {
        continue;
      }
      parentOf.set(edge.toId, edge.fromId);
    }
    const keep = new Set<string>();
    for (const node of this.listedNodes()) {
      if (node.semanticType === 'CleanEngineeringModel' || this._isFileNode(node)) {
        continue;
      }
      if (node.practice !== practice) {
        continue;
      }
      keep.add(node.nodeId);
      const seen = new Set<string>();
      let current = parentOf.get(node.nodeId);
      while (current && !seen.has(current)) {
        seen.add(current);
        keep.add(current);
        current = parentOf.get(current);
      }
    }
    const sortNodes = (nodes: GraphNode[]) =>
      [...nodes].sort((left, right) => this._compareTreeNodes(left, right));
    const nest = (node: GraphNode, prefix: string, stack: Set<string>): ListedTreeNode => {
      const leaf = this._listedLeaf(node);
      const path = prefix ? `${prefix}.${leaf.name}` : leaf.name;
      const next = new Set(stack);
      next.add(node.nodeId);
      const nested = sortNodes(
        [...keep]
          .filter((id) => parentOf.get(id) === node.nodeId && !next.has(id))
          .map((id) => this._nodeById(id))
          .filter((child): child is GraphNode => Boolean(child)),
      ).map((child) => nest(child, path, next));
      const folded = this._foldBackground(node, leaf, nested);
      return {
        ...leaf,
        name: folded.name,
        source: folded.source,
        path,
        origin: leaf.source?.file ? leaf.source : null,
        children: this._arrangeListedChildren(node, path, folded.children),
        failed: leaf.failed + folded.failed,
        total: leaf.total + folded.total,
      };
    };
    const roots = sortNodes(
      [...keep]
        .map((id) => this._nodeById(id))
        .filter((node): node is GraphNode => Boolean(node))
        .filter((node) => {
          const parent = parentOf.get(node.nodeId);
          return !parent || !keep.has(parent);
        }),
    );
    return roots.map((node) => nest(node, `${practice}.${node.name}`, new Set()));
  }

  private _foldBackground(
    node: GraphNode,
    leaf: { name: string; source: SourceRangeDto | null },
    children: ListedTreeNode[],
  ): { name: string; source: SourceRangeDto | null; children: ListedTreeNode[]; failed: number; total: number } {
    const failed = children.reduce((sum, child) => sum + child.failed, 0);
    const total = children.reduce((sum, child) => sum + child.total, 0);
    const name =
      node.semanticType === 'Background' && (leaf.name === 'each' || leaf.name === 'all')
        ? 'background'
        : leaf.name;
    return { name, source: leaf.source, children, failed, total };
  }

  private _arrangeListedChildren(
    node: GraphNode,
    path: string,
    children: ListedTreeNode[],
  ): ListedTreeNode[] {
    return arrangeListedClassChildren(
      { node_id: node.nodeId, path, practice: node.practice },
      children,
      this._allEdges().filter(
        (edge) => edge.from_id === node.nodeId && edge.kind !== 'belongsTo',
      ),
    );
  }

  private _practiceHead(node: GraphNode, practices: string[]): boolean {
    if (!practices.includes(node.practice) || this._isFileNode(node)) {
      return false;
    }
    if (node.semanticType === 'Package' || node.semanticType === 'Example') {
      return false;
    }
    if (node.practice === 'stories') {
      return node.semanticType === 'Epic';
    }
    if (node.practice === 'ddd') {
      return node.semanticType === 'BoundedContext';
    }
    if (node.practice === 'bdd') {
      return node.semanticType === 'Description';
    }
    return true;
  }

  private _practiceClosure(): Map<string, GraphNode> {
    const closure = new Map(this.listedNodes().map((node) => [node.nodeId, node]));
    const edges = this._allEdges().filter(
      (edge) => edge.kind === 'owns' || edge.kind === 'scopes',
    );
    let grew = true;
    while (grew) {
      grew = false;
      for (const edge of edges) {
        if (closure.has(edge.to_id) && !closure.has(edge.from_id)) {
          const parent = this._nodeById(edge.from_id);
          if (parent) {
            closure.set(parent.nodeId, parent);
            grew = true;
          }
        }
        if (closure.has(edge.from_id) && !closure.has(edge.to_id)) {
          const child = this._nodeById(edge.to_id);
          if (child && !this._isFileNode(child)) {
            closure.set(child.nodeId, child);
            grew = true;
          }
        }
      }
    }
    return closure;
  }

  private _ownsParents(closure: Map<string, GraphNode>): Map<string, string[]> {
    const parentOf = new Map<string, string[]>();
    const owned = new Set<string>();
    for (const edge of this._allEdges()) {
      if (edge.kind !== 'owns' && edge.kind !== 'scopes') {
        continue;
      }
      if (!closure.has(edge.from_id) || !closure.has(edge.to_id)) {
        continue;
      }
      if (edge.kind === 'owns') {
        const nextParent = closure.get(edge.from_id);
        const child = closure.get(edge.to_id);
        if (child?.semanticType === 'Example') {
          if (nextParent?.semanticType === 'Step' || nextParent?.semanticType === 'Background') {
            const parents = parentOf.get(edge.to_id) ?? [];
            if (!parents.includes(edge.from_id)) {
              parents.push(edge.from_id);
              parentOf.set(edge.to_id, parents);
            }
            owned.add(edge.to_id);
          }
          continue;
        }
        const currentId = parentOf.get(edge.to_id)?.[0];
        const currentParent = currentId ? closure.get(currentId) : undefined;
        const packageWouldReplace =
          currentParent !== undefined &&
          currentParent.semanticType !== 'Package' &&
          nextParent?.semanticType === 'Package';
        if (!packageWouldReplace) {
          parentOf.set(edge.to_id, [edge.from_id]);
          owned.add(edge.to_id);
        }
        continue;
      }
      if (owned.has(edge.to_id)) {
        continue;
      }
      const parents = parentOf.get(edge.to_id) ?? [];
      if (!parents.includes(edge.from_id)) {
        parents.push(edge.from_id);
        parentOf.set(edge.to_id, parents);
      }
    }
    for (const edge of this._allEdges()) {
      if (edge.kind !== 'loads' && edge.kind !== 'demonstratedThrough') {
        continue;
      }
      const child = closure.get(edge.to_id);
      const parent = closure.get(edge.from_id);
      if (!child || child.semanticType !== 'Example' || owned.has(edge.to_id) || !parent) {
        continue;
      }
      if (parent.semanticType !== 'Step' && parent.semanticType !== 'Background') {
        continue;
      }
      const parents = parentOf.get(edge.to_id) ?? [];
      if (!parents.includes(edge.from_id)) {
        parents.push(edge.from_id);
        parentOf.set(edge.to_id, parents);
      }
    }
    for (const [childId, parents] of parentOf) {
      if (closure.get(childId)?.semanticType === 'Example') {
        continue;
      }
      const stories = parents.filter(
        (parentId) => closure.get(parentId)?.semanticType === 'Story',
      );
      if (stories.length > 0) {
        parentOf.set(childId, stories);
      }
    }
    return parentOf;
  }

  private _narrowsToHits(): boolean {
    return (
      Boolean(this.view.filter.violations) ||
      listed(this.view.filter.rules, this.view.filter.rule) !== null ||
      listed(this.view.filter.ruleSources) !== null
    );
  }

  private _treeChildren() {
    const visible = this._visibleNodes();
    const visibleIds = new Set(visible.map((node) => node.nodeId));
    const childrenByParent = new Map<string, GraphNode[]>();
    const childIds = new Set<string>();
    const parentOf = new Map<string, string>();
    for (const edge of this._treeOwnsEdges()) {
      parentOf.set(edge.toId, edge.fromId);
    }
    if (!this._narrowsToHits()) {
      for (const folder of this._topLevelFolders()) {
        visibleIds.add(folder.nodeId);
      }
    }
    this._adoptFolderTree(childrenByParent, childIds, visibleIds, parentOf);
    for (const node of visible) {
      if (this._isFileNode(node)) {
        continue;
      }
      if (node.semanticType === 'Property') {
        const ownerId = parentOf.get(node.nodeId);
        const owner = ownerId ? this._nodeById(ownerId) : null;
        if (!owner || !isClassKind(owner.semanticType)) {
          continue;
        }
      }
      const parentId = this._visibleAncestor(parentOf, visibleIds, node.nodeId);
      if (parentId && !this._isTopLevelFolder(node)) {
        this._adoptChild(childrenByParent, childIds, parentId, node);
      }
    }
    const skipRoot = new Set(['CleanEngineeringModel', 'StoryMap']);
    for (const extra of visible) {
      if (
        childIds.has(extra.nodeId) ||
        skipRoot.has(extra.semanticType) ||
        this._isFileNode(extra) ||
        extra.semanticType === 'Property' ||
        this._isTopLevelFolder(extra)
      ) {
        continue;
      }
      const home = this._folderHome(extra);
      if (home) {
        this._adoptChild(childrenByParent, childIds, home.nodeId, extra);
      }
    }
    return { childrenByParent, childIds };
  }

  private _adoptFolderTree(
    childrenByParent: Map<string, GraphNode[]>,
    childIds: Set<string>,
    visibleIds: Set<string>,
    parentOf: Map<string, string>,
  ) {
    const folders = this._allNodes()
      .map((node) => ({ node, path: this._modulePath(node) }))
      .filter((entry): entry is { node: GraphNode; path: string } => Boolean(entry.path))
      .sort((left, right) => left.path.length - right.path.length);
    for (const { node } of folders) {
      if (this._isTopLevelFolder(node) || childIds.has(node.nodeId)) {
        continue;
      }
      const parentId = parentOf.get(node.nodeId);
      const parent = parentId ? this._nodeById(parentId) : null;
      if (!parentId || !parent) {
        continue;
      }
      if (this._narrowsToHits() && !visibleIds.has(node.nodeId)) {
        continue;
      }
      if (
        !visibleIds.has(parentId) &&
        !childIds.has(parentId) &&
        !this._isTopLevelFolder(parent)
      ) {
        continue;
      }
      this._adoptChild(childrenByParent, childIds, parentId, node);
      if (!this._narrowsToHits()) {
        visibleIds.add(node.nodeId);
      }
    }
  }

  private _adoptChild(
    childrenByParent: Map<string, GraphNode[]>,
    childIds: Set<string>,
    fromId: string,
    child: GraphNode,
  ) {
    if (childIds.has(child.nodeId) || fromId === child.nodeId) {
      return;
    }
    const siblings = childrenByParent.get(fromId) ?? [];
    if (siblings.some((entry) => entry.nodeId === child.nodeId)) {
      return;
    }
    siblings.push(child);
    childrenByParent.set(fromId, siblings);
    childIds.add(child.nodeId);
  }

  private _visibleAncestor(
    parentOf: Map<string, string>,
    visibleIds: Set<string>,
    nodeId: string,
  ): string | null {
    const seen = new Set<string>();
    let current = parentOf.get(nodeId);
    while (current) {
      if (seen.has(current) || current === nodeId) {
        return null;
      }
      seen.add(current);
      if (visibleIds.has(current)) {
        const ancestor = this._nodeById(current);
        if (ancestor && !this._isFileNode(ancestor)) {
          return current;
        }
      }
      current = parentOf.get(current);
    }
    return null;
  }

  private _isTopLevelFolder(node: GraphNode): boolean {
    if (node.isFile) {
      return false;
    }
    if (node.semanticType !== 'Package' && node.semanticType !== 'Module') {
      return false;
    }
    const path = this._modulePath(node);
    return Boolean(path && !path.includes('/'));
  }

  private _topLevelFolders(): GraphNode[] {
    const byPath = new Map<string, GraphNode>();
    for (const node of this._allNodes()) {
      if (!this._isTopLevelFolder(node)) {
        continue;
      }
      const path = this._modulePath(node);
      if (!path) {
        continue;
      }
      const current = byPath.get(path);
      if (!current || (current.semanticType === 'Package' && node.semanticType === 'Module')) {
        byPath.set(path, node);
      }
    }
    return [...byPath.values()];
  }

  private _folderHome(node: GraphNode): GraphNode | null {
    const path = this._homePath(node);
    if (!path) {
      return null;
    }
    const parts = path.split('/').filter(Boolean);
    for (let index = parts.length; index >= 1; index -= 1) {
      const prefix = parts.slice(0, index).join('/');
      const folder = this._folderByPath(prefix);
      if (folder && folder.nodeId !== node.nodeId) {
        return folder;
      }
    }
    return null;
  }

  private _homePath(node: GraphNode): string {
    const file = node.source?.file?.replaceAll('\\', '/') ?? '';
    return (
      this._modulePath(node) ||
      asFolderPath(node.properties.folder || '') ||
      (file.includes('/') ? file.slice(0, file.lastIndexOf('/')) : '')
    );
  }

  private _folderByPath(path: string): GraphNode | null {
    return this._foldersByPath().get(path) ?? null;
  }

  private _folderIndex: Map<string, GraphNode> | null = null;

  private _foldersByPath() {
    if (this._folderIndex) {
      return this._folderIndex;
    }
    const byPath = new Map<string, GraphNode>();
    for (const node of this._allNodes()) {
      const path = this._modulePath(node);
      if (!path) {
        continue;
      }
      const current = byPath.get(path);
      if (
        !current ||
        (current.semanticType === 'Package' && node.semanticType === 'Module')
      ) {
        byPath.set(path, node);
      }
    }
    this._folderIndex = byPath;
    return byPath;
  }

  private _visibleNodes(): GraphNode[] {
    const seeds = this.listedNodes();
    const seedIds = new Set(seeds.map((node) => node.nodeId));
    const visible = new Map(seeds.map((node) => [node.nodeId, node]));
    const parentsOf = new Map<string, string[]>();
    const childrenOf = new Map<string, string[]>();
    for (const edge of this._treeOwnsEdges()) {
      const parents = parentsOf.get(edge.toId);
      if (parents) {
        parents.push(edge.fromId);
      } else {
        parentsOf.set(edge.toId, [edge.fromId]);
      }
      const children = childrenOf.get(edge.fromId);
      if (children) {
        children.push(edge.toId);
      } else {
        childrenOf.set(edge.fromId, [edge.toId]);
      }
    }
    const up = [...visible.keys()];
    for (let index = 0; index < up.length; index += 1) {
      for (const parentId of parentsOf.get(up[index]) ?? []) {
        if (visible.has(parentId)) {
          continue;
        }
        const parent = this._nodeById(parentId);
        if (!parent) {
          continue;
        }
        visible.set(parent.nodeId, parent);
        up.push(parent.nodeId);
      }
    }
    if (!this._narrowsToHits()) {
      const seenDown = new Set(seedIds);
      const down = [...seedIds];
      for (let index = 0; index < down.length; index += 1) {
        for (const childId of childrenOf.get(down[index]) ?? []) {
          if (seenDown.has(childId)) {
            continue;
          }
          const child = this._nodeById(childId);
          if (!child || this._isFileNode(child)) {
            continue;
          }
          seenDown.add(childId);
          down.push(childId);
          visible.set(child.nodeId, child);
        }
      }
      for (const edge of this._allEdges()) {
        if (!seedIds.has(edge.from_id) && !seedIds.has(edge.to_id)) {
          continue;
        }
        const otherId = seedIds.has(edge.from_id) ? edge.to_id : edge.from_id;
        const other = this._nodeById(otherId);
        if (other) {
          visible.set(other.nodeId, other);
        }
      }
    }
    return [...visible.values()];
  }

  private _allNodes(): GraphNode[] {
    if (!this._nodes) {
      this._nodes = this.dto.practice_graphs.flatMap((graph) =>
        graph.nodes.map((node) => GraphNode.fromDto(node)),
      );
      this._byId = new Map(this._nodes.map((node) => [node.nodeId, node]));
      this._nodes = [...this._byId.values()];
    }
    return this._nodes;
  }

  private _nodeById(nodeId: string): GraphNode | null {
    this._allNodes();
    return this._byId?.get(nodeId) ?? null;
  }

  private _ownsEdges() {
    if (!this._owns) {
      const edges = this._allEdges()
        .filter((edge) => edge.kind === 'owns')
        .map((edge) => ({ fromId: edge.from_id, toId: edge.to_id }));
      const seen = new Set(edges.map((edge) => `${edge.fromId}>${edge.toId}`));
      const modules = this._allNodes()
        .map((node) => ({ node, path: this._modulePath(node) }))
        .filter(
          (entry): entry is { node: GraphNode; path: string } =>
            Boolean(entry.path),
        );
      const byPath = new Map(modules.map((entry) => [entry.path, entry]));
      for (const child of modules) {
        const parts = child.path.split('/');
        let nearest: { node: GraphNode; path: string } | null = null;
        for (let index = parts.length - 1; index >= 1; index -= 1) {
          const candidate = byPath.get(parts.slice(0, index).join('/'));
          if (candidate) {
            nearest = candidate;
            break;
          }
        }
        if (!nearest) {
          continue;
        }
        const key = `${nearest.node.nodeId}>${child.node.nodeId}`;
        if (seen.has(key)) {
          continue;
        }
        seen.add(key);
        edges.push({ fromId: nearest.node.nodeId, toId: child.node.nodeId });
      }
      this._owns = edges;
    }
    return this._owns;
  }

  private _treeOwnsEdges() {
    if (!this._treeOwns) {
      const parentByChild = new Map<string, { fromId: string; rank: number }>();
      const take = (fromId: string, toId: string, rank: number) => {
        if (!fromId || !toId || fromId === toId) {
          return;
        }
        const current = parentByChild.get(toId);
        if (current && current.rank <= rank) {
          return;
        }
        parentByChild.set(toId, { fromId, rank });
      };
      this._attachFolderParents(take);
      this._attachSourceParents(take);
      this._attachOwnedMembers(take);
      this._attachMembersBySourceRange(take);
      this._treeOwns = [...parentByChild.entries()].map(([toId, parent]) => ({
        fromId: parent.fromId,
        toId,
      }));
    }
    return this._treeOwns;
  }

  private _attachFolderParents(
    take: (fromId: string, toId: string, rank: number) => void,
  ) {
    const byPath = this._foldersByPath();
    for (const [path, child] of byPath) {
      const cut = path.lastIndexOf('/');
      if (cut < 0) {
        continue;
      }
      const parent = byPath.get(path.slice(0, cut));
      if (!parent) {
        continue;
      }
      take(parent.nodeId, child.nodeId, treeOwnerRank(parent.semanticType));
    }
  }

  private _attachSourceParents(
    take: (fromId: string, toId: string, rank: number) => void,
  ) {
    const byPath = this._foldersByPath();
    for (const node of this._allNodes()) {
      if (
        this._isFileNode(node) ||
        node.semanticType === 'Parameter' ||
        node.semanticType === 'Property'
      ) {
        continue;
      }
      const file = node.source?.file?.replaceAll('\\', '/');
      if (!file) {
        continue;
      }
      const cut = file.lastIndexOf('/');
      if (cut < 0) {
        continue;
      }
      const parent = byPath.get(file.slice(0, cut));
      if (!parent || parent.nodeId === node.nodeId) {
        continue;
      }
      take(parent.nodeId, node.nodeId, 15);
    }
  }

  private _isFileNode(node: GraphNode): boolean {
    return (
      node.semanticType === 'File' ||
      node.nodeId.startsWith('ce:File:')
    );
  }

  private _treeOwner(node: GraphNode | null): GraphNode | null {
    if (!node) {
      return null;
    }
    if (!this._isFileNode(node)) {
      return node;
    }
    return this._folderHome(node);
  }

  private _attachOwnedMembers(
    take: (fromId: string, toId: string, rank: number) => void,
  ) {
    const skip = new Set(['CleanEngineeringModel', 'StoryMap']);
    for (const edge of this._allEdges()) {
      if (edge.kind === 'owns' || edge.kind === 'hasParameter') {
        const to = this._nodeById(edge.to_id);
        if (!to || this._isFileNode(to)) {
          continue;
        }
        const from = this._treeOwner(this._nodeById(edge.from_id));
        if (
          !from ||
          skip.has(from.semanticType) ||
          (to.semanticType === 'Property' && !isClassKind(from.semanticType)) ||
          this._isDistantFolderOwner(from, to) ||
          containmentRank(from.semanticType) > containmentRank(to.semanticType)
        ) {
          continue;
        }
        take(from.nodeId, edge.to_id, treeOwnerRank(from.semanticType));
      }
      if (edge.kind === 'belongsTo') {
        const child = this._nodeById(edge.from_id);
        if (!child || this._isFileNode(child)) {
          continue;
        }
        const parent = this._treeOwner(this._nodeById(edge.to_id));
        if (
          !parent ||
          skip.has(parent.semanticType) ||
          (child.semanticType === 'Property' && !isClassKind(parent.semanticType)) ||
          this._isDistantFolderOwner(parent, child) ||
          containmentRank(parent.semanticType) > containmentRank(child.semanticType)
        ) {
          continue;
        }
        take(parent.nodeId, edge.from_id, treeOwnerRank(parent.semanticType));
      }
    }
  }

  private _attachMembersBySourceRange(
    take: (fromId: string, toId: string, rank: number) => void,
  ) {
    const classesByFile = new Map<string, GraphNode[]>();
    for (const node of this._allNodes()) {
      if (
        !isClassKind(node.semanticType) ||
        !node.source?.file ||
        (node.source.start_line ?? 0) < 1
      ) {
        continue;
      }
      const file = node.source.file.replaceAll('\\', '/');
      const listed = classesByFile.get(file);
      if (listed) {
        listed.push(node);
      } else {
        classesByFile.set(file, [node]);
      }
    }
    for (const node of this._allNodes()) {
      if (node.semanticType !== 'Operation' && node.semanticType !== 'Property') {
        continue;
      }
      const file = node.source?.file?.replaceAll('\\', '/') ?? '';
      const line = node.source?.start_line ?? 0;
      if (!file || line < 1) {
        continue;
      }
      let owner: GraphNode | null = null;
      let span = Number.POSITIVE_INFINITY;
      for (const cls of classesByFile.get(file) ?? []) {
        const start = cls.source?.start_line ?? 0;
        const end = cls.source?.end_line ?? start;
        if (line < start || line > end) {
          continue;
        }
        const size = end - start;
        if (size < span) {
          span = size;
          owner = cls;
        }
      }
      if (owner) {
        take(owner.nodeId, node.nodeId, treeOwnerRank(owner.semanticType));
      }
    }
  }

  private _isDistantFolderOwner(from: GraphNode | null, to: GraphNode | null): boolean {
    if (!from || !to) {
      return false;
    }
    if (from.semanticType !== 'Module' && from.semanticType !== 'Package') {
      return false;
    }
    const fromPath = this._modulePath(from);
    const file = to.source?.file?.replaceAll('\\', '/') ?? '';
    if (!fromPath || !file) {
      return false;
    }
    const dir = file.includes('/') ? file.slice(0, file.lastIndexOf('/')) : '';
    return dir !== fromPath && dir.startsWith(`${fromPath}/`);
  }

  private _compareTreeNodes(left: GraphNode, right: GraphNode): number {
    const rank = treeTypeRank(left.semanticType) - treeTypeRank(right.semanticType);
    if (rank !== 0) {
      return rank;
    }
    if (left.semanticType === 'Step' && right.semanticType === 'Step') {
      const leftLine = left.source?.start_line ?? 0;
      const rightLine = right.source?.start_line ?? 0;
      if (leftLine > 0 && rightLine > 0 && leftLine !== rightLine) {
        return leftLine - rightLine;
      }
      if (left.sequentialOrder !== right.sequentialOrder) {
        return left.sequentialOrder - right.sequentialOrder;
      }
    }
    return this._treeLabel(left).localeCompare(this._treeLabel(right));
  }

  private _treeLabel(node: GraphNode): string {
    const path = this._modulePath(node);
    const name = path ? (path.split('/').pop() ?? node.name) : node.name;
    return stepTitle(name, node.semanticType, node.keyword, node.source?.text ?? '');
  }

  private _modulePath(node: GraphNode): string | null {
    if (node.isFile) {
      return null;
    }
    if (node.semanticType !== 'Module' && node.semanticType !== 'Package') {
      return null;
    }
    return asFolderPath(node.properties.folder || node.name) || null;
  }

  private _allEdges(): RelationshipDto[] {
    if (!this._edges) {
      this._edges = this.dto.practice_graphs.flatMap(
        (graph) => graph.relationships,
      );
    }
    return this._edges;
  }

  private _selectedRule(): ListedRule | null {
    const slug = this.view.selectedRuleSlug;
    if (!slug || !this.selectedNode) {
      return null;
    }
    return (
      this.selectedNode.rules.details().find((rule) => rule.slug === slug) ?? null
    );
  }

  private _filterOptions(): GraphFilterOptions {
    const except = (cleared: GraphFilter) =>
      this._allNodes().filter((node) => this._matchesFacet(node, cleared));
    const forPractices = except({ practices: undefined, practice: undefined });
    const forStages = except({ stages: undefined, fidelity: undefined });
    const forTypes = except({ nodeTypes: undefined, nodeType: undefined });
    const unfiltered = this._allNodes();
    return {
      practices: unique([
        ...PRACTICES,
        ...forPractices.map((node) => node.practice).filter(Boolean),
      ]),
      stages: unique([
        ...STAGES,
        ...forStages.map((node) => node.stage).filter(Boolean),
      ]),
      node_types: unique([
        ...forTypes.map((node) => node.semanticType).filter(Boolean),
        ...practiceNodeTypes(this.view.filter.practices),
      ]),
      relationship_types: unique([
        ...RELATIONSHIP_KINDS,
        ...this._kindsOn(unfiltered),
      ]),
      rules: this._slugsOn(unfiltered, true),
      rule_sources: unique(['base', 'project', ...this._sourcesOn(unfiltered)]),
    };
  }

  private _matchesFacet(node: GraphNode, cleared: GraphFilter): boolean {
    const filter = { ...this.view.filter, ...cleared };
    return this._matchesIdentity(node, filter) && this._matchesRules(node, filter);
  }

  private _kindsOn(nodes: GraphNode[]): string[] {
    const ids = new Set(nodes.map((node) => node.nodeId));
    return unique(
      this._allEdges()
        .filter((edge) => ids.has(edge.from_id) || ids.has(edge.to_id))
        .map((edge) => edge.kind),
    );
  }

  private _slugsOn(nodes: GraphNode[], unfiltered = false): string[] {
    const sources = unfiltered ? null : listed(this.view.filter.ruleSources);
    const slugs: string[] = [];
    for (const node of nodes) {
      for (const rule of node.rules.details()) {
        if (sources !== null && !sources.includes(rule.tag)) {
          continue;
        }
        slugs.push(rule.slug);
      }
      for (const hit of node.rules.violations) {
        if (sources !== null && !sources.includes(hit.tag)) {
          continue;
        }
        slugs.push(hit.ruleSlug);
      }
    }
    if (!unfiltered && this.view.filter.violations) {
      const failing = new Set<string>();
      for (const node of this._allNodes()) {
        for (const hit of node.rules.violations) {
          failing.add(hit.ruleSlug);
        }
      }
      return unique(slugs).filter((slug) => failing.has(slug));
    }
    return unique(slugs);
  }

  private _matchesFilter(node: GraphNode): boolean {
    if (!this._matchesIdentity(node, this.view.filter)) {
      return false;
    }
    return this._matchesRules(node);
  }

  private _matchesIdentity(node: GraphNode, filter: GraphFilter): boolean {
    const practices = listed(filter.practices, filter.practice);
    const stages = listed(filter.stages, filter.fidelity);
    const nodeTypes = listed(filter.nodeTypes, filter.nodeType);
    const relationshipTypes = listed(
      filter.relationshipTypes,
      filter.relationshipType || filter.connectorKind,
    );
    if (node.semanticType === 'Package') {
      if (nodeTypes !== null) {
        return allows(nodeTypes, node.semanticType);
      }
      return false;
    }
    if (!allows(practices, node.practice)) {
      return false;
    }
    if (!allows(stages, node.stage)) {
      return false;
    }
    if (!allows(nodeTypes, node.semanticType)) {
      return false;
    }
    if (filter.node && node.name !== filter.node) {
      return false;
    }
    if (
      relationshipTypes !== null &&
      !relationshipTypes.some((kind) => this._hasConnectorKind(node, kind))
    ) {
      return false;
    }
    return true;
  }

  private _sourcesOn(nodes: GraphNode[]): string[] {
    const tags: string[] = [];
    for (const node of nodes) {
      for (const rule of node.rules.details()) {
        if (rule.tag) {
          tags.push(rule.tag);
        }
      }
      for (const hit of node.rules.violations) {
        if (hit.tag) {
          tags.push(hit.tag);
        }
      }
    }
    return unique(tags);
  }

  private _matchesRules(node: GraphNode, filter: GraphFilter = this.view.filter): boolean {
    const { violations } = filter;
    const rules = listed(filter.rules, filter.rule);
    const sources = listed(filter.ruleSources);
    if (sources !== null) {
      const matching = node.rules.details().filter((rule) => {
        if (!sources.includes(rule.tag)) {
          return false;
        }
        return rules === null || rules.includes(rule.slug);
      });
      if (matching.length === 0) {
        return false;
      }
      if (violations) {
        return matching.some((rule) => rule.status === 'violating');
      }
      return true;
    }
    if (rules !== null && !rules.some((slug) => node.rules.hasRule(slug))) {
      return false;
    }
    if (violations && rules !== null) {
      return rules.some((slug) => node.rules.status(slug) === 'violating');
    }
    if (violations) {
      return node.rules.violations.length > 0;
    }
    return true;
  }

  private _kindsByNode(): Map<string, Set<string>> {
    if (!this._kinds) {
      const kinds = new Map<string, Set<string>>();
      for (const edge of this._allEdges()) {
        let fromKinds = kinds.get(edge.from_id);
        if (!fromKinds) {
          fromKinds = new Set();
          kinds.set(edge.from_id, fromKinds);
        }
        fromKinds.add(edge.kind);
        let toKinds = kinds.get(edge.to_id);
        if (!toKinds) {
          toKinds = new Set();
          kinds.set(edge.to_id, toKinds);
        }
        toKinds.add(edge.kind);
      }
      this._kinds = kinds;
    }
    return this._kinds;
  }

  private _hasConnectorKind(node: GraphNode, kind: string): boolean {
    return this._kindsByNode().get(node.nodeId)?.has(kind) ?? false;
  }
}

function dropCatalogModules(dto: KnowledgeGraphDto): KnowledgeGraphDto {
  const catalogIds = catalogModuleIds(dto);
  if (catalogIds.size === 0) {
    return dto;
  }
  rehomeCatalogOwns(dto, catalogIds);
  for (const graph of dto.practice_graphs) {
    graph.nodes = graph.nodes.filter((node) => !catalogIds.has(node.node_id));
    graph.relationships = graph.relationships.filter(
      (edge) => !catalogIds.has(edge.from_id) && !catalogIds.has(edge.to_id),
    );
  }
  return dto;
}

function catalogModuleIds(dto: KnowledgeGraphDto): Set<string> {
  const modules = dto.practice_graphs.flatMap((graph) =>
    graph.nodes.filter((node) => node.semantic_type === 'Module'),
  );
  const moduleIds = new Set(modules.map((node) => node.node_id));
  const ownsModule = new Set<string>();
  for (const graph of dto.practice_graphs) {
    for (const edge of graph.relationships) {
      if (edge.kind === 'owns' && moduleIds.has(edge.from_id) && moduleIds.has(edge.to_id)) {
        ownsModule.add(edge.from_id);
      }
    }
  }
  const folders = modules.map(moduleFolderOf).filter(Boolean);
  return new Set(
    modules
      .filter((node) => {
        if (ownsModule.has(node.node_id)) {
          return false;
        }
        const folder = moduleFolderOf(node);
        return folders.some((other) => other.startsWith(`${folder}/`));
      })
      .map((node) => node.node_id),
  );
}

function moduleFolderOf(node: NodeDto): string {
  const folder = asFolderPath(node.properties?.folder || '');
  if (folder) {
    return folder;
  }
  if (node.semantic_type !== 'Module') {
    return '';
  }
  return asFolderPath(node.name.replaceAll('.', '/'));
}

function rehomeCatalogOwns(dto: KnowledgeGraphDto, catalogIds: Set<string>) {
  for (const graph of dto.practice_graphs) {
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns' || !catalogIds.has(edge.from_id)) {
        continue;
      }
      const child = graph.nodes.find((node) => node.node_id === edge.to_id);
      const owner = owningModuleForFile(
        graph,
        child?.source?.file || '',
        catalogIds,
      );
      if (owner) {
        edge.from_id = owner.node_id;
      }
    }
  }
}

function owningModuleForFile(
  graph: PracticeGraphDto,
  file: string,
  catalogIds: Set<string>,
): NodeDto | null {
  const path = file.replaceAll('\\', '/');
  const modules = graph.nodes.filter(
    (node) => node.semantic_type === 'Module' && !catalogIds.has(node.node_id),
  );
  const matches = modules.filter((node) => {
    const folder = moduleFolderOf(node);
    return folder && (path === folder || path.startsWith(`${folder}/`));
  });
  if (matches.length > 0) {
    return matches.sort(
      (left, right) => moduleFolderOf(right).length - moduleFolderOf(left).length,
    )[0];
  }
  const childFolder = path.split('/').slice(0, 2).join('/');
  if (!childFolder || !path.startsWith(`${childFolder}/`)) {
    return null;
  }
  const created: NodeDto = {
    node_id: `ce:Module:${childFolder.replaceAll('/', '.')}`,
    name: childFolder.split('/').pop() || childFolder,
    practice: 'clean_engineering',
    semantic_type: 'Module',
    properties: { folder: childFolder },
    applicable_rules: [],
    violations: [],
    source: null,
  };
  graph.nodes.push(created);
  return created;
}

function dropClonedOperationHits(dto: KnowledgeGraphDto): KnowledgeGraphDto {
  const nodeById = new Map<string, NodeDto>();
  const classOf = new Map<string, string>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      nodeById.set(node.node_id, node);
    }
  }
  for (const graph of dto.practice_graphs) {
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns' && edge.kind !== 'belongsTo') {
        continue;
      }
      const parentId = edge.kind === 'owns' ? edge.from_id : edge.to_id;
      const childId = edge.kind === 'owns' ? edge.to_id : edge.from_id;
      if (nodeById.get(parentId)?.semantic_type === 'OoadClass') {
        classOf.set(childId, parentId);
      }
    }
  }
  const memberTypes = new Set(['Operation', 'Property', 'Parameter']);
  const counts = new Map<string, number>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      if (!memberTypes.has(node.semantic_type)) {
        continue;
      }
      for (const hit of node.violations) {
        const key = `${hit.rule_slug}\0${hit.message}`;
        counts.set(key, (counts.get(key) ?? 0) + 1);
      }
    }
  }
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      if (!memberTypes.has(node.semantic_type)) {
        continue;
      }
      const owner = nodeById.get(classOf.get(node.node_id) ?? '');
      node.violations = node.violations.filter((hit) => {
        const copies = counts.get(`${hit.rule_slug}\0${hit.message}`) ?? 0;
        return copies <= 1 || operationHitBelongs(node, owner, hit);
      });
    }
  }
  return dto;
}

function operationHitBelongs(
  node: NodeDto,
  owner: NodeDto | undefined,
  hit: { message: string },
): boolean {
  const labeled = /Operation '([^']+)'/.exec(hit.message);
  if (labeled && labeled[1].includes('.')) {
    const split = labeled[1].lastIndexOf('.');
    const cls = labeled[1].slice(0, split);
    const op = labeled[1].slice(split + 1);
    return node.name === op && owner?.name === cls;
  }
  const lines = / is (\d+) lines/.exec(hit.message);
  if (lines && node.source && node.source.start_line >= 1) {
    const end = node.source.end_line || node.source.start_line;
    return end - node.source.start_line + 1 === Number(lines[1]);
  }
  const attr =
    /private attribute '([^']+)'/.exec(hit.message) ??
    /via '([^']+)'/.exec(hit.message);
  if (attr && node.source?.text) {
    return node.source.text.includes(attr[1]);
  }
  return false;
}

export const SKIP_TYPES = new Set([
  'string',
  'number',
  'boolean',
  'unknown',
  'void',
  'any',
  'null',
  'undefined',
  'object',
  'never',
  'bigint',
  'symbol',
  'str',
  'int',
  'float',
  'bool',
  'None',
  'list',
  'dict',
  'self',
  'Promise',
  'Array',
  'Readonly',
  'Partial',
  'Record',
  'Map',
  'Set',
  'Date',
]);

export function methodSignature(name: string, operationText: string, classText: string): string {
  const line = classText.match(new RegExp(`(?:^|\\n)[^\\n]*\\b${name}\\s*\\([^\\n]*`))?.[0] ?? '';
  if (line.includes(':') || line.includes('->')) {
    return line;
  }
  if (operationText.includes('(')) {
    return operationText;
  }
  return line || operationText;
}

export function isSimpleProperty(text: string): boolean {
  const lines = text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith('//'));
  if (lines.length === 0) {
    return true;
  }
  const body = lines.join('\n');
  if (/\b(if|for|while|switch|try|catch|throw)\b/.test(body)) {
    return false;
  }
  if (/\b(get|set|async|function)\b/.test(body) && body.includes('(')) {
    return false;
  }
  if (/\([^)]*\)\s*\{/.test(body)) {
    return false;
  }
  return lines.length <= 2;
}

export function memberCallLabels(text: string): Map<string, string> {
  const labels = new Map<string, string>();
  const call = /\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b/g;
  for (const match of text.matchAll(call)) {
    if (SKIP_TYPES.has(match[1]) || labels.has(match[2])) {
      continue;
    }
    labels.set(match[2], `${match[1]}.${match[2]}`);
  }
  return labels;
}

export function fieldTypeNames(text: string): string[] {
  const declared = text.split(':').slice(1).join(':');
  return typeIdentifiers(declared);
}

export function arrangeListedClassChildren(
  owner: { node_id: string; path?: string; practice: string },
  children: ListedTreeNode[],
  edges: RelationshipDto[] = [],
): ListedTreeNode[] {
  const members = children.flatMap((child) =>
    child.semantic_type === 'FieldGroup' ? child.children ?? [] : [child],
  );
  for (const child of members) {
    if (!child.practice) {
      child.practice = owner.practice;
    }
  }
  const byId = new Map(members.map((child) => [child.node_id, child]));
  const outgoing = edges
    .filter((edge) => edge.from_id === owner.node_id)
    .sort((left, right) => {
      const immediate = Number(right.immediate !== false) - Number(left.immediate !== false);
      if (immediate !== 0) {
        return immediate;
      }
      return (left.sequential_order ?? 0) - (right.sequential_order ?? 0);
    });
  const seen = new Set<string>();
  const immediate: ListedTreeNode[] = [];
  const collapsed = new Map<string, ListedTreeNode[]>();
  const collapseOrder = new Map<string, number>();
  for (const edge of outgoing) {
    const child = byId.get(edge.to_id);
    if (!child || seen.has(child.node_id)) {
      continue;
    }
    seen.add(child.node_id);
    if (edge.immediate !== false) {
      immediate.push(child);
      continue;
    }
    const group = collapsed.get(edge.kind) ?? [];
    group.push(child);
    collapsed.set(edge.kind, group);
    if (!collapseOrder.has(edge.kind)) {
      collapseOrder.set(edge.kind, edge.sequential_order ?? 0);
    }
  }
  for (const child of members) {
    if (!seen.has(child.node_id)) {
      immediate.push(child);
    }
  }
  const arranged = [...immediate];
  for (const [kind, group] of [...collapsed.entries()].sort(
    (left, right) => (collapseOrder.get(left[0]) ?? 0) - (collapseOrder.get(right[0]) ?? 0),
  )) {
    arranged.push({
      node_id: `${owner.node_id}::${kind}`,
      name: kind,
      path: `${owner.path ?? owner.node_id}.${kind}`,
      practice: owner.practice,
      semantic_type: 'FieldGroup',
      is_file: false,
      properties: {},
      rule_statuses: {},
      rules: [],
      relationships: [],
      source: null,
      origin: null,
      children: group,
      failed: group.reduce((sum, child) => sum + child.failed, 0),
      total: group.reduce((sum, child) => sum + child.total, 0),
    });
  }
  return arranged;
}

export function signatureTypeNames(text: string): string[] {
  const head = text.split('{')[0] ?? '';
  const params = head.match(/\(([^)]*)\)/)?.[1] ?? '';
  const names: string[] = [];
  for (const part of params.split(',')) {
    if (!part.includes(':')) {
      continue;
    }
    names.push(...typeIdentifiers(part.slice(part.indexOf(':') + 1)));
  }
  names.push(...returnTypeNames(head));
  return names;
}

export function returnTypeNames(text: string): string[] {
  const head = text.split('{')[0] ?? '';
  const returned = head.match(/\)\s*(?::|->)\s*([\s\S]*)$/)?.[1] ?? '';
  return typeIdentifiers(returned);
}

function typeIdentifiers(text: string): string[] {
  return text.match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? [];
}

function findListedNode(
  nodes: ListedTreeNode[],
  nodeId: string | null,
): ListedTreeNode | null {
  if (!nodeId) {
    return null;
  }
  for (const node of nodes) {
    if (node.node_id === nodeId) {
      return node;
    }
    const nested = findListedNode(node.children, nodeId);
    if (nested) {
      return nested;
    }
  }
  return null;
}

function listedRuleFromHit(slug: string, hit?: RuleHit, tag?: string): ListedRule {
  return {
    slug,
    tag: hit?.tag || tag || 'base',
    status: hit ? 'violating' : 'passing',
    body: hit?.body || RULE_GUIDANCE[slug] || '',
    message: hit?.message ?? '',
    practice: hit?.practice ?? '',
    fidelity: hit?.fidelity ?? '',
  };
}

function listed(
  values: string[] | undefined,
  fallback?: string,
): string[] | null {
  if (values === undefined) {
    return fallback ? [fallback] : null;
  }
  return values;
}

function withoutFolder(properties: Record<string, string>): Record<string, string> {
  const shown: Record<string, string> = {};
  for (const [name, value] of Object.entries(properties)) {
    if (name !== 'folder' && value) {
      shown[name] = value;
    }
  }
  return shown;
}

function allows(selected: string[] | null, value: string): boolean {
  return selected === null || selected.includes(value);
}

function unique(values: Array<string | null | undefined>): string[] {
  return [...new Set(values.filter((value): value is string => Boolean(value)))];
}

function asFolderPath(raw: string): string {
  const path = raw.replaceAll('\\', '/').replace(/^\/+|\/+$/g, '');
  if (!path) {
    return '';
  }
  if (path.includes('/')) {
    return path;
  }
  const withoutExt = path.replace(/\.(tsx|ts|jsx|js|mjs|cjs|py)$/i, '');
  if (withoutExt.includes('.')) {
    return withoutExt.replaceAll('.', '/');
  }
  return withoutExt || path;
}

function practiceNodeTypes(practices: string[] | undefined): string[] {
  const selected =
    practices && practices.length > 0 && practices.length < PRACTICES.length
      ? practices
      : [...PRACTICES];
  return selected.flatMap((practice) => NODE_TYPES_BY_PRACTICE[practice] ?? []);
}

function treeTypeRank(kind: string): number {
  if (kind === 'Practice' || kind === 'Package') return 0;
  if (kind === 'Epic' || kind === 'BoundedContext' || kind === 'Description') return 1;
  if (kind === 'SubEpic' || kind === 'Aggregate' || kind === 'Context') return 2;
  if (kind === 'Story') return 3;
  if (kind === 'Background') return 4;
  if (kind === 'Scenario') return 5;
  if (kind === 'Step' || kind === 'Observation') return 6;
  if (kind === 'Example') return 20;
  if (kind === 'EntityRoot') return 3;
  if (kind === 'Entity') return 4;
  if (kind === 'ValueObject') return 5;
  if (kind === 'DomainEvent') return 6;
  if (kind === 'Specification') return 7;
  if (kind === 'Repository') return 8;
  if (kind === 'DomainService') return 9;
  if (kind === 'Module') return 1;
  if (kind === 'CleanEngineeringModel' || kind === 'StoryMap') return 2;
  if (kind === 'Operation') return 4;
  if (kind === 'Property') return 5;
  if (kind === 'Parameter') return 6;
  return 3;
}

function treeOwnerRank(kind: string): number {
  if (kind === 'OoadClass') return 8;
  if (kind === 'Operation') return 10;
  if (kind === 'Story' || kind === 'Scenario' || kind === 'Background' || kind === 'Step' || kind === 'Epic' || kind === 'SubEpic') return 12;
  if (kind === 'Package') return 40;
  if (kind === 'Module' || kind === 'File') return 30;
  if (kind === 'CleanEngineeringModel' || kind === 'StoryMap') return 80;
  return 20;
}

function containmentRank(kind: string): number {
  if (kind === 'Package' || kind === 'Module' || kind === 'File') return 1;
  if (
    kind === 'OoadClass' ||
    kind === 'Entity' ||
    kind === 'EntityRoot' ||
    kind === 'ValueObject' ||
    kind === 'Repository' ||
    kind === 'DomainEvent' ||
    kind === 'DomainService' ||
    kind === 'Specification'
  ) {
    return 2;
  }
  if (kind === 'Operation' || kind === 'Property') return 3;
  if (kind === 'Parameter') return 4;
  return 2;
}

function folderPathOf(node: NodeDto): string {
  if (node.source) {
    return '';
  }
  const folder = asFolderPath(node.properties?.folder || '');
  if (folder) {
    return folder;
  }
  if (node.semantic_type === 'Module' || node.semantic_type === 'Package') {
    return asFolderPath(node.name);
  }
  return '';
}

function addAncestorFolders(needed: Set<string>, path: string) {
  const parts = path.split('/').filter(Boolean);
  for (let index = 1; index <= parts.length; index += 1) {
    needed.add(parts.slice(0, index).join('/'));
  }
}

function packageNode(path: string): NodeDto {
  return {
    node_id: `pkg:${path}`,
    name: path.split('/').pop() ?? path,
    practice: '',
    fidelity: null,
    semantic_type: 'Package',
    properties: { folder: path },
    applicable_rules: [],
    violations: [],
    source: null,
  };
}

function sourceDirectories(dto: KnowledgeGraphDto): Set<string> {
  const dirs = new Set<string>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      const file = node.source?.file?.replaceAll('\\', '/') ?? '';
      const cut = file.lastIndexOf('/');
      if (cut <= 0) {
        continue;
      }
      addAncestorFolders(dirs, file.slice(0, cut));
    }
  }
  return dirs;
}

function ensureFolderPackages(dto: KnowledgeGraphDto): KnowledgeGraphDto {
  const dirs = sourceDirectories(dto);
  const drop = new Set<string>();
  if (dirs.size > 0) {
    for (const graph of dto.practice_graphs) {
      graph.nodes = graph.nodes.filter((node) => {
        if (node.source || (node.semantic_type !== 'Module' && node.semantic_type !== 'Package')) {
          return true;
        }
        const path = folderPathOf(node);
        if (path && dirs.has(path)) {
          node.properties = { ...node.properties, folder: path };
          return true;
        }
        if ((node.applicable_rules?.length ?? 0) > 0 || (node.violations?.length ?? 0) > 0) {
          return true;
        }
        drop.add(node.node_id);
        return false;
      });
      graph.relationships = graph.relationships.filter(
        (edge) => !drop.has(edge.from_id) && !drop.has(edge.to_id),
      );
    }
  }
  const byPath = new Map<string, string>();
  const seenIds = new Set<string>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      seenIds.add(node.node_id);
      if (node.semantic_type !== 'Module' && node.semantic_type !== 'Package') {
        continue;
      }
      const path = folderPathOf(node);
      if (!path || (dirs.size > 0 && !dirs.has(path))) {
        continue;
      }
      node.properties = { ...node.properties, folder: path };
      if (!byPath.has(path) || node.semantic_type === 'Module') {
        byPath.set(path, node.node_id);
      }
    }
  }
  const needed = dirs.size > 0 ? dirs : new Set(byPath.keys());
  if (dirs.size === 0) {
    for (const path of byPath.keys()) {
      addAncestorFolders(needed, path);
    }
  }
  const packages: NodeDto[] = [];
  const edges: RelationshipDto[] = [];
  for (const path of [...needed].sort()) {
    if (!byPath.has(path)) {
      const node = packageNode(path);
      packages.push(node);
      byPath.set(path, node.node_id);
    }
  }
  const existing = dto.practice_graphs.find(
    (graph) => graph.id === 'practice:workspace',
  );
  const seen = new Set(
    (existing?.relationships ?? []).map(
      (edge) => `${edge.from_id}>${edge.to_id}`,
    ),
  );
  for (const [path, nodeId] of byPath) {
    const cut = path.lastIndexOf('/');
    if (cut < 0) {
      continue;
    }
    const parentId = byPath.get(path.slice(0, cut));
    if (!parentId) {
      continue;
    }
    const key = `${parentId}>${nodeId}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    edges.push({ kind: 'owns', from_id: parentId, to_id: nodeId });
  }
  const newPackages = packages.filter((node) => !seenIds.has(node.node_id));
  if (newPackages.length === 0 && edges.length === 0) {
    return dto;
  }
  if (existing) {
    existing.nodes.push(...newPackages);
    existing.relationships.push(...edges);
    return dto;
  }
  return {
    ...dto,
    practice_graphs: [
      {
        id: 'practice:workspace',
        name: 'workspace',
        nodes: packages,
        relationships: edges,
      },
      ...dto.practice_graphs,
    ],
  };
}

export interface KnowledgeGraphRepository {
  load(id: string): Promise<KnowledgeGraph | null>;
  create(input: CreateKnowledgeGraphInput): Promise<KnowledgeGraph>;
  search(query?: KnowledgeGraphSearch): Promise<KnowledgeGraph[]>;
  update(root: KnowledgeGraph): Promise<KnowledgeGraph>;
}
