import {
  KnowledgeGraph,
  KnowledgeGraphNode,
  WebKnowledgeGraphNode,
  KnowledgeGraphPanel,
  KnowledgeGraphFilter,
} from "./knowledge-graph";
import { stageFor } from "./catalog";

const GRAPH_DEADLINE_MS = 180_000;
const DATABASE_DEADLINE_MS = 2 * 60 * 60 * 1000;

export type RuleCatalogEntry = {
  slug: string;
  practice: string;
  fidelity: string;
  applies_to: string[];
};

export type KnowledgeGraphFilterOptions = {
  practices: string[];
  stages: string[];
  node_types: string[];
  relationship_types: string[];
  rules: string[];
  ruleCatalog: RuleCatalogEntry[];
};

const EMPTY_OPTIONS: KnowledgeGraphFilterOptions = {
  practices: [],
  stages: [],
  node_types: [],
  relationship_types: [],
  rules: [],
  ruleCatalog: [],
};

export type PracticeMember = {
  practice: string;
  stage: string;
  type: string;
  rules: string[];
  connectors: string[];
};

/** Browser subtype of KnowledgeGraph. Hosts fetch and UI state; does not replace the graph. */
export class KnowledgeGraphClient extends KnowledgeGraph {
  graphId: string;
  options: KnowledgeGraphFilterOptions;
  members: PracticeMember[];

  constructor(storyModel?: any, ceModel?: any, domainDrivenDesignModel?: any, description?: any) {
    super(storyModel, ceModel, domainDrivenDesignModel, description);
    this.graphId = "";
    this.options = { ...EMPTY_OPTIONS };
    this.members = [];
  }

  async createDatabase(): Promise<void> {
    const raw = await this.postJson(
      "/api/knowledge-graphs/create-database",
      { folder: this.folder },
      DATABASE_DEADLINE_MS,
      "Create database",
    );
    this.takeSave(raw);
  }

  async refreshMaster(): Promise<void> {
    const raw = await this.postJson(
      "/api/knowledge-graphs/refresh-master",
      { folder: this.folder },
      DATABASE_DEADLINE_MS,
      "Merge working to master",
    );
    this.takeSave(raw);
  }

  async reloadWorkingCopy(): Promise<void> {
    const raw = await this.postJson(
      "/api/knowledge-graphs/reload-working-copy",
      { folder: this.folder },
      DATABASE_DEADLINE_MS,
      "Reload working copy",
    );
    this.takeSave(raw);
  }

  async loadKnowledgeGraph(path: any, paths?: string[]): Promise<void> {
    this.folder = path;
    if (paths) {
      this.graphId = "";
    }
    const suffix = this.graphId ? `/${this.graphId}` : "/scan";
    const raw = this.graphId
      ? await this.getJson(`/api/knowledge-graphs${suffix}`)
      : await this.postJson(
          "/api/knowledge-graphs/scan",
          { folder: path, paths: paths ?? [] },
          GRAPH_DEADLINE_MS,
          "Load Knowledge Graph",
        );
    this.takeSave(raw);
  }

  choose(node: KnowledgeGraphNode): void {
    super.choose(node);
    if (node.source && !node.panel) {
      node.panel = new KnowledgeGraphPanel(node.source, node.source.language);
      node.panel.open = true;
    }
  }

  takeSave(raw: any): void {
    const presented = raw ?? {};
    const dto = presented.knowledge_graph ?? presented;
    this.graphId = dto.id ?? presented.id ?? this.graphId;
    this.folder = presented.folder ?? dto.folder ?? this.folder;
    if (typeof window !== "undefined" && this.folder) {
      window.localStorage.setItem("kg-scan-root-v2", this.folder);
      if (this.graphId) {
        window.localStorage.setItem("kg-scan-graph-id-v2", this.graphId);
      }
    }
    const rows = presented.listed_tree ?? presented.nodes ?? [];
    const tree = rows.map((row: any) => WebKnowledgeGraphNode.fromDto(row));
    this.options.ruleCatalog = Array.isArray(presented.rule_catalog) ? presented.rule_catalog : [];
    this.matching = tree;
    this.nodes = this.flattenNodes(tree);
    this.options = this.filterOptions(presented.filter_options, this.nodes);
    this.options.ruleCatalog = Array.isArray(presented.rule_catalog)
      ? presented.rule_catalog
      : this.options.ruleCatalog;
    this.members = this.practiceMembers(dto);
    if (presented.selected_node) {
      const found =
        this.nodes.find(
          (node) => node.nodeId === (presented.selected_node.node_id ?? presented.selected_node.nodeId),
        ) ?? WebKnowledgeGraphNode.fromDto(presented.selected_node);
      this.choose(found);
    }
    if (Array.isArray(presented.filter)) {
      this.filter = presented.filter.map((row: any) => new KnowledgeGraphFilter(row.selected ?? []));
    }
  }

  practiceMembers(dto: any): PracticeMember[] {
    const buckets = new Map<string, PracticeMember>();
    const members: PracticeMember[] = [];
    const take = (practice: string, stage: string, type: string): PracticeMember | null => {
      if (!practice || !type) {
        return null;
      }
      const key = `${practice}\0${stage}\0${type}`;
      const existing = buckets.get(key);
      if (existing) {
        return existing;
      }
      const created: PracticeMember = { practice, stage, type, rules: [], connectors: [] };
      buckets.set(key, created);
      members.push(created);
      return created;
    };
    for (const graph of dto.practice_graphs ?? []) {
      for (const row of graph.nodes ?? []) {
        const bucket = take(
          String(row.practice ?? graph.name ?? ""),
          stageFor(String(row.fidelity ?? row.stage ?? "")),
          String(row.semantic_type ?? ""),
        );
        if (!bucket) {
          continue;
        }
        for (const slug of this.ruleSlugs(row)) {
          if (!bucket.rules.includes(slug)) {
            bucket.rules.push(slug);
          }
        }
      }
      for (const edge of graph.relationships ?? []) {
        const kind = String(edge.kind ?? "");
        if (!kind) {
          continue;
        }
        for (const id of [edge.from_id, edge.to_id]) {
          const parsed = this.nodeIdParts(id);
          if (!parsed) {
            continue;
          }
          for (const bucket of members) {
            if (bucket.practice === parsed.practice && bucket.type === parsed.type && !bucket.connectors.includes(kind)) {
              bucket.connectors.push(kind);
            }
          }
        }
      }
    }
    return members;
  }

  filterOptions(given: any, nodes: KnowledgeGraphNode[]): KnowledgeGraphFilterOptions {
    const source = given ?? {};
    return {
      practices: this.listed(source.practices, nodes.map((node) => node.practice)),
      stages: this.listed(source.stages, nodes.map((node) => node.stage)),
      node_types: this.listed(source.node_types, nodes.map((node) => node.nodeType?.name ?? "")),
      relationship_types: this.listed(source.relationship_types, []),
      rules: this.listed(
        source.rules,
        nodes.flatMap((node) => (node.ruleHits ?? []).map((hit) => hit.slug)),
      ),
    };
  }

  listed(given: unknown, fallback: string[]): string[] {
    const rows = Array.isArray(given) ? given.map((item) => String(item)).filter(Boolean) : [];
    const names = rows.length ? rows : fallback.filter(Boolean);
    return [...new Set(names)];
  }

  flattenNodes(nodes: KnowledgeGraphNode[]): KnowledgeGraphNode[] {
    return nodes.flatMap((node) => [node, ...this.flattenNodes(node.children ?? [])]);
  }

  async getJson(url: string): Promise<any> {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`KnowledgeGraph ${url} not found`);
    }
    return response.json();
  }

  async postJson(url: string, body: unknown, deadlineMs: number, label: string): Promise<any> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), deadlineMs);
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      if (!response.ok) {
        const detail = (await response.json().catch(() => ({}))) as { error?: string };
        throw new Error(detail.error ?? `${label} failed`);
      }
      return response.json();
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error(`${label} stopped after ${deadlineMs / 1000}s with no result`);
      }
      throw error;
    } finally {
      clearTimeout(timer);
    }
  }

  ruleSlugs(row: any): string[] {
    const listed = [
      ...(row.applicable_rules ?? []),
      ...(row.rules ?? []).map((rule: any) => rule.slug ?? rule.rule_slug ?? ""),
    ];
    return [...new Set(listed.map((slug) => String(slug)).filter(Boolean))];
  }

  nodeIdParts(id: unknown): { practice: string; type: string } | null {
    const parts = String(id ?? "").split(":");
    if (parts.length < 2 || !parts[0] || !parts[1]) {
      return null;
    }
    return { practice: parts[0], type: parts[1] };
  }
}
