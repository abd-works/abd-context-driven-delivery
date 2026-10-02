import {
  KnowledgeGraph,
  KnowledgeGraphNode,
  WebKnowledgeGraphNode,
  KnowledgeGraphPanel,
  KnowledgeGraphSource,
  KnowledgeGraphFilter,
  SourceRange,
} from "./knowledge-graph";

const GRAPH_DEADLINE_MS = 180_000;
const DATABASE_DEADLINE_MS = 15 * 60_000;

export type KnowledgeGraphFilterOptions = {
  practices: string[];
  stages: string[];
  node_types: string[];
  relationship_types: string[];
  rules: string[];
};

const EMPTY_OPTIONS: KnowledgeGraphFilterOptions = {
  practices: [],
  stages: [],
  node_types: [],
  relationship_types: [],
  rules: [],
};

export type PracticeMember = { practice: string; type: string };

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
    const raw = await postJson(
      "/api/knowledge-graphs/create-database",
      { folder: this.folder },
      DATABASE_DEADLINE_MS,
      "Create database",
    );
    this.takeSave(raw);
  }

  async refreshMaster(): Promise<void> {
    const raw = await postJson(
      "/api/knowledge-graphs/refresh-master",
      { folder: this.folder },
      DATABASE_DEADLINE_MS,
      "Refresh master",
    );
    this.takeSave(raw);
  }

  async reloadWorkingCopy(): Promise<void> {
    const raw = await postJson(
      "/api/knowledge-graphs/reload-working-copy",
      { folder: this.folder },
      DATABASE_DEADLINE_MS,
      "Reload working copy",
    );
    this.takeSave(raw);
  }

  async loadKnowledgeGraph(path: any): Promise<void> {
    this.folder = path;
    const suffix = this.graphId ? `/${this.graphId}` : "/scan";
    const raw = this.graphId
      ? await getJson(`/api/knowledge-graphs${suffix}`)
      : await postJson(
          "/api/knowledge-graphs/scan",
          { folder: path },
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
    const rows =
      presented.listed_tree ??
      presented.nodes ??
      (dto.practice_graphs ?? []).flatMap((graph: any) => graph.nodes ?? []);
    const tree = rows.map((row: any) => webNode(row));
    attachMembers(tree, dto);
    this.matching = tree;
    this.nodes = flattenNodes(tree);
    this.options = filterOptions(presented.filter_options, this.nodes);
    this.members = practiceMembers(dto);
    if (presented.selected_node) {
      const found =
        this.nodes.find(
          (node) => node.nodeId === (presented.selected_node.node_id ?? presented.selected_node.nodeId),
        ) ?? webNode(presented.selected_node);
      this.choose(found);
    }
    if (Array.isArray(presented.filter)) {
      this.filter = presented.filter.map((row: any) => new KnowledgeGraphFilter(row.selected ?? []));
    }
  }
}

function webNode(row: any): WebKnowledgeGraphNode {
  const origin = row.origin
    ? new SourceRange(row.origin.file, row.origin.start_line ?? row.origin.startLine, row.origin.end_line ?? row.origin.endLine, row.origin.text)
    : null;
  const node = new WebKnowledgeGraphNode(
    row.keyword ?? "",
    origin,
    row.properties ?? {},
    row.is_file ?? row.isFile ?? false,
    row.is_folder ?? row.isFolder ?? false,
  );
  node.name = row.name ?? "";
  node.practice = row.practice ?? "";
  node.stage = row.fidelity ?? row.stage ?? "";
  node.ruleHits = ruleHitsFrom(row);
  node.nodeId = row.node_id ?? row.nodeId ?? row.name ?? "";
  node.nodeType = row.semantic_type || row.nodeType
    ? { name: row.semantic_type ?? row.nodeType?.name ?? "" }
    : node.nodeType;
  node.isFolder =
    row.is_folder ??
    row.isFolder ??
    node.nodeType?.name === "Module" ??
    false;
  node.children = (row.children ?? []).map((child: any) => webNode(child));
  if (row.source?.file || row.file) {
    node.source = new KnowledgeGraphSource(
      row.source?.text ?? row.text ?? "",
      row.source?.file ?? row.file ?? "",
      row.source?.start_line ?? row.start_line ?? 0,
      row.source?.end_line ?? row.end_line ?? 0,
      row.source?.language ?? "",
    );
  }
  return node;
}

function attachMembers(tree: WebKnowledgeGraphNode[], dto: any): void {
  const members = (dto.practice_graphs ?? []).flatMap((graph: any) => graph.nodes ?? []);
  const skip = new Set(["Module", "Package", "StoryMap", "CleanEngineeringModel", "StoryModel"]);
  const classes = members.filter((row: any) => !skip.has(row.semantic_type));
  const walk = (nodes: WebKnowledgeGraphNode[]): void => {
    for (const node of nodes) {
      const folder =
        node.isFolder ||
        node.nodeType?.name === "Module" ||
        node.properties?.semantic_type === "Module";
      if (folder) {
        for (const row of classes) {
          if (!memberHomesIn(row, node.name)) {
            continue;
          }
          const id = row.node_id ?? row.name;
          if (!node.children.some((child) => child.nodeId === id || child.name === row.name)) {
            node.children.push(webNode(row));
          }
        }
      }
      walk(node.children);
    }
  };
  walk(tree);
}

function memberHomesIn(row: any, folderName: string): boolean {
  const needle = String(folderName).toLowerCase();
  if (!needle) {
    return false;
  }
  const file = String(row.source?.file ?? "").replaceAll("\\", "/").toLowerCase();
  const parts = file.split("/").filter(Boolean);
  const parent = parts.length > 1 ? parts[parts.length - 2] : "";
  const propFolder = String(row.properties?.folder ?? "").replaceAll("\\", "/").toLowerCase();
  const propParent = propFolder.split("/").filter(Boolean).pop() ?? "";
  if (parent && parent === needle) {
    return true;
  }
  if (propParent && propParent === needle) {
    return true;
  }
  return !file && !propParent && String(row.name ?? "").toLowerCase() === needle;
}

function ruleHitsFrom(row: any): { slug: string; status: string }[] {
  if (Array.isArray(row.rules) && row.rules.length) {
    return row.rules.map((rule: any) => ({
      slug: String(rule.slug ?? rule.rule_slug ?? ""),
      status: String(rule.status ?? "passing"),
    }));
  }
  const failing = new Set(
    (row.violations ?? []).map((hit: any) => String(hit.rule_slug ?? hit.ruleSlug ?? "")),
  );
  return (row.applicable_rules ?? []).map((slug: string) => ({
    slug,
    status: failing.has(slug) ? "violating" : "passing",
  }));
}

function practiceMembers(dto: any): PracticeMember[] {
  const seen = new Set<string>();
  const members: PracticeMember[] = [];
  for (const graph of dto.practice_graphs ?? []) {
    for (const row of graph.nodes ?? []) {
      const practice = String(row.practice ?? graph.name ?? "");
      const type = String(row.semantic_type ?? "");
      const key = `${practice}\0${type}`;
      if (!practice || !type || seen.has(key)) {
        continue;
      }
      seen.add(key);
      members.push({ practice, type });
    }
  }
  return members;
}

function filterOptions(given: any, nodes: KnowledgeGraphNode[]): KnowledgeGraphFilterOptions {
  const source = given ?? {};
  return {
    practices: listed(source.practices, nodes.map((node) => node.practice)),
    stages: listed(source.stages, nodes.map((node) => node.stage)),
    node_types: listed(source.node_types, nodes.map((node) => node.nodeType?.name ?? "")),
    relationship_types: listed(source.relationship_types, []),
    rules: listed(source.rules, []),
  };
}

function listed(given: unknown, fallback: string[]): string[] {
  const rows = Array.isArray(given) ? given.map((item) => String(item)).filter(Boolean) : [];
  const names = rows.length ? rows : fallback.filter(Boolean);
  return [...new Set(names)];
}

function flattenNodes(nodes: KnowledgeGraphNode[]): KnowledgeGraphNode[] {
  return nodes.flatMap((node) => [node, ...flattenNodes(node.children ?? [])]);
}

async function getJson(url: string): Promise<any> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`KnowledgeGraph ${url} not found`);
  }
  return response.json();
}

async function postJson(url: string, body: unknown, deadlineMs: number, label: string): Promise<any> {
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
