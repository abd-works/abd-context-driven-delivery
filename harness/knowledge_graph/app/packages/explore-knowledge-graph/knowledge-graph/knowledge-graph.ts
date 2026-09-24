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
  PRACTICES,
  RELATIONSHIP_KINDS,
  RULE_GUIDANCE,
  STAGES,
  stageFor,
} from './catalog';

export const KEEP_OPERATIONS_SMALL_FOCUSED = 'keep-operations-small-focused';

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
});

export const NodeSchema = z.object({
  node_id: z.string().min(1),
  name: z.string().min(1),
  practice: z.string(),
  fidelity: z.string().nullable().default(null),
  semantic_type: z.string(),
  properties: z.record(z.string()).default({}),
  applicable_rules: z.array(z.string()).default([]),
  violations: z.array(RuleHitSchema).default([]),
  source: SourceRangeSchema.nullable().default(null),
});

export const RelationshipSchema = z.object({
  kind: z.string(),
  from_id: z.string(),
  to_id: z.string(),
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
};

export type GraphFilterOptions = {
  practices: string[];
  stages: string[];
  node_types: string[];
  relationship_types: string[];
  rules: string[];
};

export type ListedRule = {
  slug: string;
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
};

export type ListedRelationshipKind = {
  kind: string;
  targets: ListedRelatedNode[];
};

export type ListedTreeNode = {
  node_id: string;
  name: string;
  path: string;
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
}

export class NodeRules {
  constructor(
    private readonly applicableRules: readonly string[],
    private readonly hits: readonly RuleHit[],
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
    if (!this.applicableRules.includes(ruleSlug)) {
      return 'absent';
    }
    if (this.hits.some((hit) => hit.ruleSlug === ruleSlug)) {
      return 'violating';
    }
    return 'passing';
  }

  hasRule(ruleSlug: string): boolean {
    return this.applicableRules.includes(ruleSlug);
  }

  details(): ListedRule[] {
    const slugs = this.applicableRules.length
      ? this.applicableRules
      : [...new Set(this.hits.map((hit) => hit.ruleSlug))];
    return slugs.map((slug) => {
      const hit = this.hits.find((entry) => entry.ruleSlug === slug);
      return listedRuleFromHit(slug, hit);
    });
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
    return stageFor(this.dto.fidelity);
  }

  get semanticType(): string {
    return this.dto.semantic_type;
  }

  get properties(): Record<string, string> {
    return { ...this.dto.properties };
  }

  get rules(): NodeRules {
    if (!this._rules) {
      const hits = this.dto.violations.map((hit) => new RuleHit(hit));
      this._rules = new NodeRules(this.dto.applicable_rules, hits);
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
    return this.selectedNode?.source ?? null;
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
      selected_tree: findListedNode(listedTree, this.view.selectedNodeId),
      selected_rule: this._selectedRule(),
      source_file: this.sourceFile,
    };
  }

  static fromDto(dto: KnowledgeGraphDto): KnowledgeGraph {
    return new KnowledgeGraph(ensureFolderPackages(dropClonedOperationHits(dto)));
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
      properties: node.properties,
      rule_statuses: node.rules.statuses(),
      rules,
      relationships: this._listedRelationships(node),
      source: node.source,
      failed,
      total: failed,
    };
  }

  private _nodeViolationCount(node: GraphNode): number {
    const slugs = listed(this.view.filter.rules, this.view.filter.rule);
    const seen = new Set<string>();
    for (const hit of node.rules.violations) {
      if (slugs !== null && !slugs.includes(hit.ruleSlug)) {
        continue;
      }
      seen.add(hit.ruleSlug);
    }
    return seen.size;
  }

  private _listedRules(node: GraphNode): ListedRule[] {
    const slugs = listed(this.view.filter.rules, this.view.filter.rule);
    if (this.view.filter.violations) {
      const seen = new Set<string>();
      const violating: ListedRule[] = [];
      for (const hit of node.rules.violations) {
        if (seen.has(hit.ruleSlug)) {
          continue;
        }
        if (slugs !== null && !slugs.includes(hit.ruleSlug)) {
          continue;
        }
        seen.add(hit.ruleSlug);
        violating.push(listedRuleFromHit(hit.ruleSlug, hit));
      }
      return violating;
    }
    const details = node.rules.details();
    if (slugs === null) {
      return details;
    }
    return details.filter((rule) => slugs.includes(rule.slug));
  }

  private _listedRelationships(node: GraphNode): ListedRelationshipKind[] {
    this._relatedByNode();
    const groups = this._related?.get(node.nodeId) ?? [];
    const kinds = listed(
      this.view.filter.relationshipTypes,
      this.view.filter.relationshipType || this.view.filter.connectorKind,
    );
    if (kinds === null) {
      return groups;
    }
    return groups.filter((group) => kinds.includes(group.kind));
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
      for (const [nodeId, byKind] of grouped) {
        const extra = [...byKind.keys()].filter(
          (kind) => !(RELATIONSHIP_KINDS as readonly string[]).includes(kind),
        );
        related.set(nodeId, [
          ...RELATIONSHIP_KINDS.map((kind) => ({
            kind,
            targets: [...(byKind.get(kind)?.values() ?? [])].sort((left, right) =>
              left.name.localeCompare(right.name),
            ),
          })),
          ...extra.sort().map((kind) => ({
            kind,
            targets: [...(byKind.get(kind)?.values() ?? [])].sort((left, right) =>
              left.name.localeCompare(right.name),
            ),
          })),
        ]);
      }
      this._related = related;
    }
    return this._related;
  }

  private _listedTree(): ListedTreeNode[] {
    const { childrenByParent, childIds } = this._treeChildren();
    const sortChildren = (nodes: GraphNode[]) =>
      [...nodes].sort((left, right) => {
        const rank = treeTypeRank(left.semanticType) - treeTypeRank(right.semanticType);
        if (rank !== 0) {
          return rank;
        }
        return this._treeLabel(left).localeCompare(this._treeLabel(right));
      });
    const nest = (
      node: GraphNode,
      prefix: string,
      parentOrigin: SourceRangeDto | null,
    ): ListedTreeNode => {
      const leaf = this._listedLeaf(node);
      const origin = leaf.source?.file ? leaf.source : parentOrigin;
      const path = prefix ? `${prefix}.${leaf.name}` : leaf.name;
      const children = sortChildren(childrenByParent.get(node.nodeId) ?? []).map(
        (child) => nest(child, path, origin),
      );
      return {
        ...leaf,
        path,
        origin,
        children,
        failed: leaf.failed + children.reduce((sum, child) => sum + child.failed, 0),
        total: leaf.total + children.reduce((sum, child) => sum + child.total, 0),
      };
    };
    const folders = this._topLevelFolders();
    const listedRoots = this._narrowsToHits()
      ? folders.filter(
          (folder) => (childrenByParent.get(folder.nodeId) ?? []).length > 0,
        )
      : folders;
    const practices = listed(
      this.view.filter.practices,
      this.view.filter.practice,
    );
    if (practices?.length === 1) {
      const head = this._practiceHead(practices[0]);
      if (head) {
        for (const folder of listedRoots) {
          this._adoptChild(childrenByParent, childIds, head.nodeId, folder);
        }
        return [nest(head, '', null)];
      }
    }
    return sortChildren(listedRoots).map((node) => nest(node, '', null));
  }

  private _narrowsToHits(): boolean {
    return (
      Boolean(this.view.filter.violations) ||
      listed(this.view.filter.rules, this.view.filter.rule) !== null
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
        if (!owner || owner.semanticType !== 'OoadClass') {
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

  private _practiceHead(practice: string): GraphNode | null {
    const skipRoot = new Set(['CleanEngineeringModel', 'StoryMap']);
    return (
      this._allNodes().find(
        (node) => node.practice === practice && skipRoot.has(node.semanticType),
      ) ??
      this._allNodes().find(
        (node) =>
          node.practice === practice &&
          this._isTopLevelFolder(node) &&
          this._treeLabel(node) === practice,
      ) ??
      null
    );
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
    return (
      this._allNodes().find((node) => this._modulePath(node) === path) ?? null
    );
  }

  private _foldersByPath() {
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
    return byPath;
  }

  private _visibleNodes(): GraphNode[] {
    const seeds = this.listedNodes();
    const seedIds = new Set(seeds.map((node) => node.nodeId));
    const visible = new Map(seeds.map((node) => [node.nodeId, node]));
    let grew = true;
    while (grew) {
      grew = false;
      for (const edge of this._treeOwnsEdges()) {
        if (!visible.has(edge.toId) || visible.has(edge.fromId)) {
          continue;
        }
        const parent = this._nodeById(edge.fromId);
        if (!parent) {
          continue;
        }
        visible.set(parent.nodeId, parent);
        grew = true;
      }
    }
    if (!this._narrowsToHits()) {
      grew = true;
      const down = new Set(seedIds);
      while (grew) {
        grew = false;
        for (const edge of this._treeOwnsEdges()) {
          if (!down.has(edge.fromId) || down.has(edge.toId)) {
            continue;
          }
          const child = this._nodeById(edge.toId);
          if (!child || this._isFileNode(child)) {
            continue;
          }
          down.add(edge.toId);
          visible.set(child.nodeId, child);
          grew = true;
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
      for (const child of modules) {
        let nearest: { node: GraphNode; path: string } | null = null;
        for (const candidate of modules) {
          if (candidate.path === child.path) {
            continue;
          }
          if (!child.path.startsWith(`${candidate.path}/`)) {
            continue;
          }
          if (!nearest || candidate.path.length > nearest.path.length) {
            nearest = candidate;
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
          (to.semanticType === 'Property' && from.semanticType !== 'OoadClass') ||
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
          (child.semanticType === 'Property' && parent.semanticType !== 'OoadClass') ||
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
    const classes = this._allNodes().filter(
      (node) =>
        node.semanticType === 'OoadClass' &&
        node.source?.file &&
        (node.source.start_line ?? 0) >= 1,
    );
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
      for (const cls of classes) {
        const clsFile = cls.source?.file.replaceAll('\\', '/') ?? '';
        const start = cls.source?.start_line ?? 0;
        const end = cls.source?.end_line ?? start;
        if (clsFile !== file || line < start || line > end) {
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

  private _treeLabel(node: GraphNode): string {
    const path = this._modulePath(node);
    if (path) {
      return path.split('/').pop() ?? node.name;
    }
    return node.name;
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
    const nodes = this._allNodes();
    return {
      practices: unique([
        ...PRACTICES,
        ...nodes.map((node) => node.practice),
      ]),
      stages: [...STAGES],
      node_types: unique(nodes.map((node) => node.semanticType)),
      relationship_types: unique([
        ...RELATIONSHIP_KINDS,
        ...this._allEdges().map((edge) => edge.kind),
      ]),
      rules: this._ruleOptions(),
    };
  }

  private _ruleOptions(): string[] {
    const practices = listed(this.view.filter.practices, this.view.filter.practice);
    const stages = listed(this.view.filter.stages, this.view.filter.fidelity);
    const slugs: string[] = [];
    for (const node of this._allNodes()) {
      if (!allows(practices, node.practice)) {
        continue;
      }
      if (!allows(stages, node.stage)) {
        continue;
      }
      slugs.push(...node.rules.applicable);
      slugs.push(...node.rules.violations.map((hit) => hit.ruleSlug));
    }
    if (this.view.filter.violations) {
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

  private _matchesRules(node: GraphNode): boolean {
    const { violations } = this.view.filter;
    const rules = listed(this.view.filter.rules, this.view.filter.rule);
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

function listedRuleFromHit(slug: string, hit?: RuleHit): ListedRule {
  return {
    slug,
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
  if (path.includes('.')) {
    return path.replaceAll('.', '/');
  }
  return path;
}

function treeTypeRank(kind: string): number {
  if (kind === 'Package') return 0;
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
    kind === 'DomainService'
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

function ensureFolderPackages(dto: KnowledgeGraphDto): KnowledgeGraphDto {
  const byPath = new Map<string, string>();
  const seenIds = new Set<string>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      seenIds.add(node.node_id);
      if (node.semantic_type !== 'Module' && node.semantic_type !== 'Package') {
        continue;
      }
      const path = folderPathOf(node);
      if (!path) {
        continue;
      }
      node.properties = { ...node.properties, folder: path };
      byPath.set(path, node.node_id);
    }
  }
  const needed = new Set<string>();
  for (const path of byPath.keys()) {
    addAncestorFolders(needed, path);
  }
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      const file = node.source?.file?.replaceAll('\\', '/') ?? '';
      if (!file.includes('/')) {
        continue;
      }
      addAncestorFolders(needed, file.slice(0, file.lastIndexOf('/')));
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
