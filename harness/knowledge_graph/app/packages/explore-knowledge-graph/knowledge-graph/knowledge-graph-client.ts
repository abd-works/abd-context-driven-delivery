import {
  KnowledgeGraph,
  KnowledgeGraphNode,
  WebKnowledgeGraphNode,
  KnowledgeGraphPanel,
  KnowledgeGraphSource,
  KnowledgeGraphFilter,
  SourceRange,
} from "./knowledge-graph";
import { stageFor } from "../../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/catalog";

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

export type PracticeMember = {
  practice: string;
  stage: string;
  type: string;
  rules: string[];
  connectors: string[];
};

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

  async loadKnowledgeGraph(path: any, paths?: string[]): Promise<void> {
    this.folder = path;
    if (paths) {
      this.graphId = "";
    }
    const suffix = this.graphId ? `/${this.graphId}` : "/scan";
    const raw = this.graphId
      ? await getJson(`/api/knowledge-graphs${suffix}`)
      : await postJson(
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
    const rows =
      presented.listed_tree ??
      presented.nodes ??
      (dto.practice_graphs ?? []).flatMap((graph: any) => graph.nodes ?? []);
    const tree = rows.map((row: any) => webNode(row));
    attachMembers(tree, dto);
    inheritPractice(tree, "");
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
  node.stage = stageFor(String(row.fidelity ?? row.stage ?? ""));
  node.ruleHits = ruleHitsFrom(row);
  node.relationships = relationshipLinks(row);
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
  const folders = indexFolders(tree);
  for (const graph of dto.practice_graphs ?? []) {
    const rows = Array.isArray(graph.nodes) ? graph.nodes : [];
    const byId = new Map(rows.map((row: any) => [String(row.node_id ?? ""), row]));
    const owned = new Map<string, string[]>();
    for (const edge of graph.relationships ?? []) {
      if (edge.kind !== "owns") {
        continue;
      }
      const from = String(edge.from_id ?? "");
      const to = String(edge.to_id ?? "");
      if (!from || !to) {
        continue;
      }
      const list = owned.get(from) ?? [];
      list.push(to);
      owned.set(from, list);
    }
    const parentOf = new Map<string, string>();
    for (const [from, tos] of owned) {
      for (const to of tos) {
        parentOf.set(to, from);
      }
    }
    const built = new Map<string, WebKnowledgeGraphNode>();
    const build = (row: any, ancestors: Set<string>): WebKnowledgeGraphNode => {
      const id = String(row.node_id ?? row.name ?? "");
      const existing = built.get(id);
      if (existing) {
        return existing;
      }
      const node = webNode(row);
      built.set(id, node);
      const next = new Set(ancestors);
      next.add(id);
      for (const childId of owned.get(id) ?? []) {
        if (next.has(childId)) {
          continue;
        }
        const childRow = byId.get(childId);
        if (!childRow) {
          continue;
        }
        const child = build(childRow, next);
        if (child === node) {
          continue;
        }
        if (child.name === node.name && child.nodeType?.name === node.nodeType?.name) {
          for (const grand of child.children) {
            if (!node.children.some((item) => item.nodeId === grand.nodeId)) {
              node.children.push(grand);
            }
          }
          continue;
        }
        if (!node.children.some((item) => item.nodeId === child.nodeId)) {
          node.children.push(child);
        }
      }
      return node;
    };
    for (const row of rows) {
      const id = String(row.node_id ?? "");
      const node = build(row, new Set());
      const home = homeFolder(row, folders);
      const parentId = parentOf.get(id);
      const parentRow = parentId ? byId.get(parentId) : undefined;
      const parentHome = parentRow ? homeFolder(parentRow, folders) : null;
      if (home && sameFolderNode(home.node, row)) {
        if (node.practice && !home.node.practice) {
          home.node.practice = node.practice;
        }
        if (node.stage && !home.node.stage) {
          home.node.stage = node.stage;
        }
        const seen = new Set(home.node.ruleHits.map((hit) => hit.slug));
        for (const hit of node.ruleHits) {
          if (!seen.has(hit.slug)) {
            home.node.ruleHits.push(hit);
            seen.add(hit.slug);
          }
        }
        for (const child of node.children) {
          pushChild(home.node, child);
        }
        continue;
      }
      if (!home) {
        if (
          !parentId &&
          row.semantic_type !== "StoryModel" &&
          row.semantic_type !== "Module" &&
          row.semantic_type !== "Package"
        ) {
          if (!tree.some((item) => item.nodeId === node.nodeId || item.name === node.name)) {
            tree.push(node);
          }
        }
        continue;
      }
      if (parentHome && !sameFolderNode(parentHome.node, parentRow)) {
        continue;
      }
      pushChild(home.node, node);
    }
  }
}

function inheritPractice(nodes: WebKnowledgeGraphNode[], practice: string): void {
  for (const node of nodes) {
    const next = node.practice || practice;
    if (!node.practice && next && (node.nodeType?.name === "File" || node.isFile)) {
      node.practice = next;
    }
    inheritPractice(node.children ?? [], node.practice || practice);
  }
}

function indexFolders(
  nodes: WebKnowledgeGraphNode[],
  prefix = "",
): { node: WebKnowledgeGraphNode; path: string }[] {
  const found: { node: WebKnowledgeGraphNode; path: string }[] = [];
  for (const node of nodes) {
    const path = prefix ? `${prefix}/${node.name}` : node.name;
    if (isFolderNode(node)) {
      found.push({ node, path });
      found.push(...indexFolders(node.children ?? [], path));
    }
  }
  return found;
}

function isFolderNode(node: WebKnowledgeGraphNode): boolean {
  return Boolean(
    node.isFolder ||
      node.nodeType?.name === "Module" ||
      node.nodeType?.name === "Package",
  );
}

function homeFolder(
  row: any,
  folders: { node: WebKnowledgeGraphNode; path: string }[],
): { node: WebKnowledgeGraphNode; path: string } | null {
  const folderPath = String(row.properties?.folder ?? "").replaceAll("\\", "/");
  if (folderPath) {
    const exact = folders.find((folder) => folder.path.replaceAll("\\", "/") === folderPath);
    if (exact) {
      return exact;
    }
  }
  const key = compactName(row.name);
  if (!key) {
    return null;
  }
  const named = folders.filter((folder) => compactName(folder.node.name) === key);
  if (!named.length) {
    return null;
  }
  const prefer = row.practice === "stories" ? "tests" : "domain";
  return named.slice().sort((left, right) => {
    const leftRank = left.path === prefer || left.path.startsWith(`${prefer}/`) ? 0 : 1;
    const rightRank = right.path === prefer || right.path.startsWith(`${prefer}/`) ? 0 : 1;
    return leftRank - rightRank || left.path.length - right.path.length;
  })[0];
}

function sameFolderNode(folder: WebKnowledgeGraphNode, row: any): boolean {
  const type = String(row.semantic_type ?? "");
  return (type === "Module" || type === "Package") && compactName(folder.name) === compactName(row.name);
}

function pushChild(parent: { children: WebKnowledgeGraphNode[] }, child: WebKnowledgeGraphNode): void {
  if (!parent.children.some((item) => item.nodeId === child.nodeId || item.name === child.name)) {
    parent.children.push(child);
  }
}

function compactName(value: string): string {
  return String(value ?? "").toLowerCase().replace(/[^a-z0-9]/g, "");
}

function relationshipLinks(row: any): { kind: string; nodeId: string; name: string }[] {
  const groups = Array.isArray(row.relationships) ? row.relationships : [];
  const links: { kind: string; nodeId: string; name: string }[] = [];
  for (const group of groups) {
    const kind = String(group.kind ?? "");
    const targets = Array.isArray(group.targets) ? group.targets : [];
    for (const target of targets) {
      const nodeId = String(target.node_id ?? target.nodeId ?? "");
      const name = String(target.name ?? "");
      if (!kind || !nodeId || !name) {
        continue;
      }
      links.push({ kind, nodeId, name });
    }
  }
  return links;
}

function ruleHitsFrom(row: any): { slug: string; status: string; message: string }[] {
  if (Array.isArray(row.rules) && row.rules.length) {
    return row.rules.map((rule: any) => ({
      slug: String(rule.slug ?? rule.rule_slug ?? ""),
      status: String(rule.status ?? "passing"),
      message: String(rule.message ?? ""),
    }));
  }
  const failing = new Map(
    (row.violations ?? []).map((hit: any) => [
      String(hit.rule_slug ?? hit.ruleSlug ?? ""),
      String(hit.message ?? ""),
    ]),
  );
  return (row.applicable_rules ?? []).map((slug: string) => ({
    slug,
    status: failing.has(slug) ? "violating" : "passing",
    message: failing.get(slug) ?? "",
  }));
}

function practiceMembers(dto: any): PracticeMember[] {
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
      for (const slug of ruleSlugs(row)) {
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
        const parsed = nodeIdParts(id);
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

function ruleSlugs(row: any): string[] {
  const listed = [
    ...(row.applicable_rules ?? []),
    ...(row.rules ?? []).map((rule: any) => rule.slug ?? rule.rule_slug ?? ""),
  ];
  return [...new Set(listed.map((slug) => String(slug)).filter(Boolean))];
}

function nodeIdParts(id: unknown): { practice: string; type: string } | null {
  const parts = String(id ?? "").split(":");
  if (parts.length < 2 || !parts[0] || !parts[1]) {
    return null;
  }
  return { practice: parts[0], type: parts[1] };
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
