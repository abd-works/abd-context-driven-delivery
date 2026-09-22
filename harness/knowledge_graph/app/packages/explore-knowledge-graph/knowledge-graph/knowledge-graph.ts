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
  practice: z.string().default(''),
  fidelity: z.string().nullable().default(null),
});

export const NodeSchema = z.object({
  node_id: z.string().min(1),
  name: z.string().min(1),
  practice: z.string(),
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
  practice?: string;
  connectorKind?: string;
  node?: string;
  violations?: boolean;
  rule?: string;
};

export type CreateKnowledgeGraphInput = {
  folder?: string;
  practiceGraphs: PracticeGraphDto[];
};

export type KnowledgeGraphSearch = {
  id?: string;
};

export class RuleHit {
  constructor(private readonly dto: RuleHitDto) {}

  get ruleSlug(): string {
    return this.dto.rule_slug;
  }

  get message(): string {
    return this.dto.message;
  }

  get practice(): string {
    return this.dto.practice;
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
}

export class GraphNode {
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

  get semanticType(): string {
    return this.dto.semantic_type;
  }

  get properties(): Record<string, string> {
    return { ...this.dto.properties };
  }

  get rules(): NodeRules {
    const hits = this.dto.violations.map((hit) => new RuleHit(hit));
    return new NodeRules(this.dto.applicable_rules, hits);
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
    return new GraphNode(NodeSchema.parse(dto));
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
    return new Relationship(RelationshipSchema.parse(dto));
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
    return new PracticeGraph(PracticeGraphSchema.parse(dto));
  }
}

export class KnowledgeGraph {
  constructor(
    private readonly dto: KnowledgeGraphDto,
    private readonly view: {
      selectedNodeId: string | null;
      filter: GraphFilter;
    } = { selectedNodeId: null, filter: {} },
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

  selectNode(nodeId: string): KnowledgeGraph {
    return new KnowledgeGraph(this.dto, {
      ...this.view,
      selectedNodeId: nodeId,
    });
  }

  followRelationship(toId: string): KnowledgeGraph {
    return this.selectNode(toId);
  }

  filterGraph(filter: GraphFilter): KnowledgeGraph {
    return new KnowledgeGraph(this.dto, {
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
    const node = this.selectedNode;
    if (node === null || node.isFolder) {
      return null;
    }
    return node.source;
  }

  toDto(): KnowledgeGraphDto {
    return KnowledgeGraphSchema.parse(this.dto);
  }

  present() {
    return {
      knowledge_graph: this.toDto(),
      folder: this.folder,
      listed_nodes: this.listedNodes().map((node) => ({
        node_id: node.nodeId,
        name: node.name,
        practice: node.practice,
        semantic_type: node.semanticType,
        is_file: node.isFile,
        rule_statuses: node.rules.statuses(),
      })),
      selected_node: this.selectedNode
        ? {
            node_id: this.selectedNode.nodeId,
            name: this.selectedNode.name,
            is_file: this.selectedNode.isFile,
            is_folder: this.selectedNode.isFolder,
          }
        : null,
      source_file: this.sourceFile,
    };
  }

  static fromDto(dto: KnowledgeGraphDto): KnowledgeGraph {
    return new KnowledgeGraph(KnowledgeGraphSchema.parse(dto));
  }

  private _allNodes(): GraphNode[] {
    return this.practiceGraphs.flatMap((graph) => graph.nodes);
  }

  private _nodeById(nodeId: string): GraphNode | null {
    return this._allNodes().find((node) => node.nodeId === nodeId) ?? null;
  }

  private _matchesFilter(node: GraphNode): boolean {
    if (!this._matchesIdentity(node)) {
      return false;
    }
    return this._matchesRules(node);
  }

  private _matchesIdentity(node: GraphNode): boolean {
    const { practice, node: nodeName, connectorKind } = this.view.filter;
    if (practice && node.practice !== practice) {
      return false;
    }
    if (nodeName && node.name !== nodeName) {
      return false;
    }
    if (connectorKind && !this._hasConnectorKind(node, connectorKind)) {
      return false;
    }
    return true;
  }

  private _matchesRules(node: GraphNode): boolean {
    const { violations, rule } = this.view.filter;
    if (rule && !node.rules.hasRule(rule)) {
      return false;
    }
    if (violations && rule) {
      return node.rules.status(rule) === 'violating';
    }
    if (violations) {
      return node.rules.violations.length > 0;
    }
    return true;
  }

  private _hasConnectorKind(node: GraphNode, kind: string): boolean {
    return this.practiceGraphs.some((graph) =>
      graph.relationships.some(
        (edge) =>
          edge.kind === kind &&
          (edge.fromId === node.nodeId || edge.toId === node.nodeId),
      ),
    );
  }
}

export interface KnowledgeGraphRepository {
  load(id: string): Promise<KnowledgeGraph | null>;
  create(input: CreateKnowledgeGraphInput): Promise<KnowledgeGraph>;
  search(query?: KnowledgeGraphSearch): Promise<KnowledgeGraph[]>;
  update(root: KnowledgeGraph): Promise<KnowledgeGraph>;
}
