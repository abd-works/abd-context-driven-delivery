const FILTER_PRACTICE: Record<string, string> = {
  clean_engineering: "CleanEngineering",
  stories: "Stories",
  ddd: "Ddd",
  bdd: "Bdd",
  CleanEngineering: "CleanEngineering",
  Stories: "Stories",
  Ddd: "Ddd",
  Bdd: "Bdd",
};

const PRACTICE_ROOTS = [
  { ids: ["clean_engineering", "CleanEngineering"], label: "Clean Engineering" },
  { ids: ["stories", "Stories"], label: "Stories" },
  { ids: ["ddd", "Ddd"], label: "Domain Driven Design" },
  { ids: ["bdd", "Bdd"], label: "BDD" },
];

const PRACTICE_ID: Record<string, string> = {
  CleanEngineering: "clean_engineering",
  Stories: "stories",
  Ddd: "ddd",
  Bdd: "bdd",
  "Clean Engineering": "clean_engineering",
  "Domain Driven Design": "ddd",
  BDD: "bdd",
};

const STEP_CALL_SKIP = new Set([
  "expect",
  "toBe",
  "toEqual",
  "toHaveCount",
  "toBeVisible",
  "toContain",
  "getByRole",
  "getByLabel",
  "getByText",
  "getByTestId",
  "locator",
  "click",
  "fill",
  "press",
  "hover",
  "check",
  "uncheck",
  "selectOption",
  "filter",
  "map",
  "forEach",
  "then",
  "catch",
  "push",
  "includes",
  "toString",
  "json",
  "keys",
  "values",
  "entries",
  "all",
  "race",
  "resolve",
  "reject",
  "first",
  "nth",
  "last",
  "count",
  "waitFor",
  "toBeTruthy",
  "toBeFalsy",
  "not",
]);

export function includedFilterPractices(practices: string[]): string[] {
  const found: string[] = [];
  for (const practice of practices) {
    const name = FILTER_PRACTICE[practice] ?? practice;
    if (!found.includes(name)) {
      found.push(name);
    }
  }
  if (found.includes("Ddd") && !found.includes("CleanEngineering")) {
    found.push("CleanEngineering");
  }
  return found;
}

export function practiceId(value: string): string {
  return PRACTICE_ID[value] ?? value;
}

export function includedPracticeIds(selected: string[]): string[] {
  const found: string[] = [];
  for (const practice of selected) {
    const id = practiceId(practice);
    if (id && !found.includes(id)) {
      found.push(id);
    }
  }
  if (found.includes("ddd") && !found.includes("clean_engineering")) {
    found.push("clean_engineering");
  }
  return found;
}

export function practiceRootLabels(selected: string[]): string[] {
  if (!selected.length) {
    return PRACTICE_ROOTS.map((item) => item.label);
  }
  return PRACTICE_ROOTS.filter((item) => item.ids.some((id) => selected.includes(id))).map(
    (item) => item.label,
  );
}

export function editorHeight(
  lineCount: number,
  folds: { start: number; end: number }[],
  openStarts: number[],
  lineHeight = 20,
  maxHeight = 520,
): number {
  const open = new Set(openStarts);
  let hidden = 0;
  for (const fold of folds) {
    if (open.has(fold.start)) {
      continue;
    }
    const covered = folds.some(
      (other) =>
        other !== fold &&
        other.start <= fold.start &&
        other.end >= fold.end &&
        other.end > other.start &&
        !open.has(other.start),
    );
    if (covered) {
      continue;
    }
    hidden += Math.max(0, fold.end - fold.start + 1);
  }
  return Math.min(maxHeight, Math.max(1, lineCount - hidden) * lineHeight);
}

export function stepMembers(text: string): { operations: string[]; examples: string[] } {
  const operations: string[] = [];
  const examples: string[] = [];
  for (const match of text.matchAll(/\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g)) {
    const name = match[1];
    if (STEP_CALL_SKIP.has(name) || operations.includes(name)) {
      continue;
    }
    operations.push(name);
  }
  for (const match of text.matchAll(/\b([A-Za-z_][A-Za-z0-9_]*Examples?)\b/g)) {
    if (!examples.includes(match[1])) {
      examples.push(match[1]);
    }
  }
  return { operations, examples };
}

function _escape(value: any): string {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

class CodeQL {
  root: any;
  database: any;
  storyModel: StoryModel;
  cleanEngineeringModel: CleanEngineeringModel;
  domainDrivenDesignModel: DomainDrivenDesignModel;

  constructor(root: any, database: any) {
    this.root = root;
    this.database = database;
    this.storyModel = new StoryModel();
    this.cleanEngineeringModel = new CleanEngineeringModel();
    this.domainDrivenDesignModel = new DomainDrivenDesignModel();
  }

  populate(): void {
    this.storyModel.load();
    this.cleanEngineeringModel.load();
    this.domainDrivenDesignModel.load();
  }
}

class StoryModel {
  load(): void {}
}

class CleanEngineeringModel {
  load(): void {}
}

class DomainDrivenDesignModel {
  load(): void {}
}

class KnowledgeGraph {
  storyModel: KnowledgeGraphStoryModel;
  ceModel: KnowledgeGraphCleanEngineeringModel;
  domainDrivenDesignModel: KnowledgeGraphDomainDrivenDesignModel;
  description: KnowledgeGraphDescription;
  nodes: KnowledgeGraphNode[];
  kinds: KnowledgeGraphEdgeType[];
  folder: any;
  filter: KnowledgeGraphFilter[];
  matching: KnowledgeGraphNode[];
  selected: KnowledgeGraphNode | null;
  expanded: KnowledgeGraphNode[];

  constructor(
    storyModel: any,
    ceModel: any,
    domainDrivenDesignModel: any,
    description: any,
  ) {
    this.storyModel = new KnowledgeGraphStoryModel(storyModel);
    this.ceModel = new KnowledgeGraphCleanEngineeringModel(ceModel);
    this.domainDrivenDesignModel = new KnowledgeGraphDomainDrivenDesignModel(
      domainDrivenDesignModel,
    );
    this.description = new KnowledgeGraphDescription(description);
    this.nodes = [];
    this.kinds = [];
    this.folder = null;
    this.filter = [];
    this.matching = [];
    this.selected = null;
    this.expanded = [];
    this.saved = {};
    this.master = "";
    this.workingCopy = "";
  }

  _nodesFromModels(): KnowledgeGraphNode[] {
    const node = new KnowledgeGraphNode();
    node.name = this.storyModel?.name ?? "StoryModel";
    node.nodeId = node.name;
    return [node];
  }

  saved: Record<string, string>;
  master: string;
  workingCopy: string;

  saveKnowledgeGraph(): void {
    this.saved = this.saved ?? {};
    this.saved["story-map.kg"] = this.storyModel.save();
    this.saved["class-model.kg"] = this.ceModel.save();
    this.saved["bounded-context-map.kg"] = this.domainDrivenDesignModel.save();
    this.saved["description.kg"] = this.description.save();
    this.nodes = this._nodesFromModels();
    this.matching = this.nodes;
  }

  loadKnowledgeGraph(path: any): void {
    this.folder = path;
    this.storyModel.load(path);
    this.ceModel.load(path);
    this.domainDrivenDesignModel.load(path);
    this.description.load(path);
    this.nodes = this._nodesFromModels();
    this.matching = this.nodes;
  }

  createDatabase(): void {
    this.master = `${this.folder}/.codeql/javascript-master`;
    this.copyMasterToWorkingCopy();
  }

  copyMasterToWorkingCopy(): void {
    this.workingCopy = `${this.folder}/.codeql/javascript-working-copy`;
  }

  copyWorkingCopyToMaster(): void {
    this.master = this.workingCopy || `${this.folder}/.codeql/javascript-master`;
  }

  refreshMaster(): void {
    this.copyWorkingCopyToMaster();
    this.saveKnowledgeGraph();
    this.loadKnowledgeGraph(this.folder);
  }

  reloadWorkingCopy(): void {
    this.saveKnowledgeGraph();
    this.copyWorkingCopyToMaster();
    this.loadKnowledgeGraph(this.folder);
  }

  updateWorkingCopy(paths: any): void {
    this.saveKnowledgeGraph();
    this.loadKnowledgeGraph(this.folder);
  }

  choose(node: KnowledgeGraphNode): void {
    this.selected = node;
    if (node.panel) {
      node.panel.open = true;
    }
  }

  open(node: KnowledgeGraphNode): void {
    if (!this.expanded.includes(node)) {
      this.expanded.push(node);
    }
  }

  close(node: KnowledgeGraphNode): void {
    this.expanded = this.expanded.filter((item) => item !== node);
  }

  render(): string {
    const listed = this.matching.length ? this.matching : this.nodes;
    const filters = this.filter.map((item) => item.render()).join("");
    const tree = listed.map((node) => node.render(0, this.selected)).join("");
    const panel = this.selected?.panel?.render() ?? "";
    return `<section class="knowledge-graph">${filters}<ul class="practice-graph-tree">${tree}</ul>${panel}</section>`;
  }
}

class KnowledgeGraphNodeType {
  name: any;
  practice: any;
  stage: any;
  edgeTypes: KnowledgeGraphEdgeType[];

  constructor(name: any, practice: any, stage: any, edgeTypes: KnowledgeGraphEdgeType[]) {
    this.name = name;
    this.practice = practice;
    this.stage = stage;
    this.edgeTypes = edgeTypes;
  }
}

class KnowledgeGraphEdgeType {
  name: any;
  fromType: KnowledgeGraphNodeType;
  toType: KnowledgeGraphNodeType;
  inverse: KnowledgeGraphEdgeType | null;
  cardinality: any;

  constructor(
    name: any,
    fromType: KnowledgeGraphNodeType,
    toType: KnowledgeGraphNodeType,
    inverse: KnowledgeGraphEdgeType | null,
    cardinality: any,
  ) {
    this.name = name;
    this.fromType = fromType;
    this.toType = toType;
    this.inverse = inverse;
    this.cardinality = cardinality;
  }
}

class KnowledgeGraphNode {
  name: any;
  sequentialOrder: any;
  nodeType: KnowledgeGraphNodeType | null;
  source: KnowledgeGraphSource | null;
  nodeId: any;
  edges: KnowledgeGraphEdge[];
  children: KnowledgeGraphNode[];
  panel: KnowledgeGraphPanel | null;
  rules: NodeRules | null;
  practice: string;
  stage: string;
  ruleHits: { slug: string; status: string; message: string }[];
  relationships: { kind: string; nodeId: string; name: string }[];

  constructor() {
    this.name = "";
    this.sequentialOrder = 0;
    this.nodeType = null;
    this.source = null;
    this.nodeId = "";
    this.edges = [];
    this.children = [];
    this.panel = null;
    this.rules = null;
    this.practice = "";
    this.stage = "";
    this.ruleHits = [];
    this.relationships = [];
  }

  navigateTo(edge: KnowledgeGraphEdge): KnowledgeGraphNode | null {
    if (edge.from === this) {
      return edge.to;
    }
    if (edge.to === this) {
      return edge.from;
    }
    return null;
  }

  render(depth = 0, selected: KnowledgeGraphNode | null = null): string {
    const kind = this.nodeType?.name ?? "";
    const nested = this.children.map((child) => child.render(depth + 1, selected)).join("");
    const branch = nested ? `<ul class="graph-children">${nested}</ul>` : "";
    const chosen = selected === this || selected?.nodeId === this.nodeId ? " is-selected" : "";
    return `<li data-node-id="${_escape(this.nodeId)}" class="graph-node${chosen}" data-kind="${_escape(kind)}" data-depth="${depth}"><span class="node-name">${_escape(this.name)}</span>${branch}</li>`;
  }
}

class KnowledgeGraphSource {
  text: any;
  file: any;
  startLine: any;
  endLine: any;
  language: any;

  constructor(text: any, file: any, startLine: any, endLine: any, language: any) {
    this.text = text;
    this.file = file;
    this.startLine = startLine;
    this.endLine = endLine;
    this.language = language;
  }

  source(): any {
    return this.text;
  }
}

class KnowledgeGraphCallSource extends KnowledgeGraphSource {
  calls: KnowledgeGraphCall[];
  folds: KnowledgeGraphSourceFold[];

  constructor(text: any, file: any, startLine: any, endLine: any, language: any) {
    super(text, file, startLine, endLine, language);
    this.calls = [];
    this.folds = [];
  }

  source(): any {
    super.source();
    this.loadCalls();
    this.insertCalls();
    this.loadFolds();
    return this.text;
  }

  loadCalls(): void {
    this.calls = [];
    const skip = new Set(["if", "for", "while", "function", "def", "switch", "catch"]);
    String(this.text ?? "")
      .split(/\r?\n/)
      .forEach((line, index) => {
        let order = 0;
        const matcher = /((?:[A-Z][A-Za-z0-9]*\.)?[A-Za-z_][A-Za-z0-9]*)\s*\(/g;
        let found: RegExpExecArray | null = matcher.exec(line);
        while (found) {
          const name = found[1];
          if (!skip.has(name.split(".").pop() ?? "")) {
            order += 1;
            this.calls.push(new KnowledgeGraphCall(index + 1, order, name));
          }
          found = matcher.exec(line);
        }
      });
  }

  insertCalls(): void {
    const lines = String(this.text ?? "").split(/\r?\n/);
    for (const call of this.calls) {
      const index = call.line - 1;
      if (index >= 0 && index < lines.length && !lines[index].includes(`call:${call.operation}`)) {
        lines[index] = `${lines[index]} /* call:${call.operation} */`;
      }
    }
    this.text = lines.join("\n");
  }

  loadFolds(): void {
    this.folds = this.calls.map(
      (call) => new KnowledgeGraphSourceFold(call.line, call.line, String(call.operation).includes(".") ? "call" : "class"),
    );
  }
}

class KnowledgeGraphCall {
  line: any;
  sequentialOrder: any;
  operation: KnowledgeGraphNode | null;

  constructor(line: any, sequentialOrder: any, operation: KnowledgeGraphNode | null) {
    this.line = line;
    this.sequentialOrder = sequentialOrder;
    this.operation = operation;
  }
}

class KnowledgeGraphSourceFold {
  start: any;
  end: any;
  kind: any;

  constructor(start: any, end: any, kind: any) {
    this.start = start;
    this.end = end;
    this.kind = kind;
  }
}

class KnowledgeGraphPanel {
  source: KnowledgeGraphSource | null;
  language: any;
  open: any;
  theme: any;
  mount: any;

  constructor(source: KnowledgeGraphSource | null, language: any) {
    this.source = source;
    this.language = language;
    this.open = false;
    this.theme = null;
    this.mount = null;
  }

  render(): string {
    const text = this.source?.source() ?? "";
    const file = this.source?.file ?? "";
    return `<section class="knowledge-graph-panel" data-open="${this.open ? "true" : "false"}" data-file="${_escape(file)}"><pre class="panel-source">${_escape(String(text))}</pre></section>`;
  }
}

class KnowledgeGraphEdge {
  edgeType: KnowledgeGraphEdgeType | null;
  from: KnowledgeGraphNode | null;
  to: KnowledgeGraphNode | null;

  constructor(
    edgeType: KnowledgeGraphEdgeType | null,
    from: KnowledgeGraphNode | null,
    to: KnowledgeGraphNode | null,
  ) {
    this.edgeType = edgeType;
    this.from = from;
    this.to = to;
  }
}

class KnowledgeGraphStoryModel extends StoryModel {
  epicType: any;
  incrementType: any;

  constructor(source?: any) {
    super();
    this.epicType = KnowledgeGraphEpic;
    this.incrementType = KnowledgeGraphIncrement;
    this.name = source?.name ?? "StoryModel";
    this.epics = source?.epics ?? [];
  }

  name: any;
  epics: any[];

  save(): string {
    this.name = this.name ?? "StoryModel";
    return JSON.stringify({ name: this.name, epics: this.epics ?? [] });
  }

  load(path: any): void {
    this.loadContent();
    this.loadEpics();
    this.loadIncrements();
  }

  loadContent(): void {}

  loadEpics(): void {}

  loadIncrements(): void {}
}

class KnowledgeGraphIncrement {
  constructor(source?: any) {}
}

class KnowledgeGraphEpic {
  storyType: any;

  constructor(source?: any) {
    this.storyType = KnowledgeGraphStory;
    this.loadEpics();
    this.loadStories();
    this.loadExamples();
  }

  loadEpics(): void {}

  loadStories(): void {}

  loadExamples(): void {}
}

class KnowledgeGraphStory {
  scenarioType: any;

  constructor(source?: any) {
    this.scenarioType = KnowledgeGraphScenario;
    this.loadScenarios();
    this.loadBackgrounds();
  }

  loadScenarios(): void {}

  loadBackgrounds(): void {}
}

class KnowledgeGraphScenario {
  constructor(source?: any) {
    this.loadBackground();
    this.loadSteps();
    this.loadExamples();
  }

  loadBackground(): void {}

  loadSteps(): void {}

  loadExamples(): void {}
}

class KnowledgeGraphBackground {
  constructor(source?: any) {
    this.loadSteps();
  }

  loadSteps(): void {}
}

class KnowledgeGraphStep {
  constructor(source?: any) {}
}

class KnowledgeGraphExample {
  constructor(source?: any) {}
}

class KnowledgeGraphCleanEngineeringModel extends CleanEngineeringModel {
  moduleType: any;

  constructor(source?: any) {
    super();
    this.moduleType = KnowledgeGraphModule;
  }

  name: any;

  save(): string {
    this.name = this.name ?? "CleanEngineeringModel";
    return JSON.stringify({ name: this.name });
  }

  load(path: any): void {
    this.loadModules();
  }

  loadModules(): void {}
}

class KnowledgeGraphModule {
  classType: any;

  constructor(source?: any) {
    this.classType = KnowledgeGraphOoadClass;
    this.loadModules();
    this.loadClasses();
  }

  loadModules(): void {}

  loadClasses(): void {}
}

class KnowledgeGraphOoadClass {
  propertyType: any;
  operationType: any;
  relationshipType: any;

  constructor(source?: any) {
    this.propertyType = KnowledgeGraphProperty;
    this.operationType = KnowledgeGraphOperation;
    this.relationshipType = KnowledgeGraphRelationship;
    this.loadProperties();
    this.loadOperations();
    this.loadRelationships();
  }

  loadProperties(): void {}

  loadOperations(): void {}

  loadRelationships(): void {}
}

class KnowledgeGraphProperty {
  constructor(source?: any) {
    this.loadRelationship();
  }

  loadRelationship(): void {}
}

class KnowledgeGraphRelationship {
  constructor(source?: any) {}
}

class KnowledgeGraphOperation {
  constructor(source?: any) {
    this.loadParameters();
  }

  loadParameters(): void {}
}

class KnowledgeGraphParameter {
  constructor(source?: any) {}
}

class KnowledgeGraphDomainDrivenDesignModel extends DomainDrivenDesignModel {
  boundedContextType: any;

  constructor(source?: any) {
    super();
    this.boundedContextType = KnowledgeGraphBoundedContext;
  }

  name: any;

  save(): string {
    this.name = this.name ?? "DomainDrivenDesignModel";
    return JSON.stringify({ name: this.name });
  }

  load(path: any): void {
    this.loadBoundedContexts();
  }

  loadBoundedContexts(): void {}
}

class KnowledgeGraphBoundedContext extends KnowledgeGraphModule {
  constructor(source?: any) {
    super(source);
  }
}

class KnowledgeGraphAggregate {
  constructor(source?: any) {
    this.loadRoot();
  }

  loadRoot(): void {}
}

class KnowledgeGraphEntity {
  constructor(source?: any) {
    this.loadProperties();
    this.loadOperations();
  }

  loadProperties(): void {}

  loadOperations(): void {}
}

class KnowledgeGraphEntityRoot {
  constructor(source?: any) {
    this.loadProperties();
    this.loadOperations();
  }

  loadProperties(): void {}

  loadOperations(): void {}
}

class KnowledgeGraphValueObject {
  constructor(source?: any) {
    this.loadProperties();
    this.loadOperations();
  }

  loadProperties(): void {}

  loadOperations(): void {}
}

class KnowledgeGraphRepository {
  constructor(source?: any) {
    this.loadProperties();
    this.loadOperations();
  }

  loadProperties(): void {}

  loadOperations(): void {}
}

class KnowledgeGraphDomainEvent {
  constructor(source?: any) {
    this.loadProperties();
    this.loadOperations();
  }

  loadProperties(): void {}

  loadOperations(): void {}
}

class KnowledgeGraphDomainService {
  constructor(source?: any) {
    this.loadProperties();
    this.loadOperations();
  }

  loadProperties(): void {}

  loadOperations(): void {}
}

class KnowledgeGraphSpecification {
  constructor(source?: any) {}
}

class KnowledgeGraphDescription {
  constructor(source?: any) {
    this.loadContexts();
  }

  name: any;

  save(): string {
    this.name = this.name ?? "";
    return JSON.stringify({ name: this.name });
  }

  load(path: any): void {
    this.loadContexts();
  }

  loadContexts(): void {}
}

class KnowledgeGraphContext {
  constructor(source?: any) {
    this.loadObservations();
    this.loadContexts();
  }

  loadObservations(): void {}

  loadContexts(): void {}
}

class KnowledgeGraphObservation {
  constructor(source?: any) {}
}

class KnowledgeGraphFilter {
  type: any;
  selected: any[];
  available: any[];
  stageFilter: StageFilter;
  nodeFilter: NodeFilter;
  relationshipFilter: RelationshipFilter;
  ruleSetFilter: RuleSetFilter;
  ruleFilter: RuleFilter;

  constructor(practices: any[] = []) {
    this.type = "Practice";
    this.selected = practices;
    this.available = [];
    this.stageFilter = new StageFilter([]);
    this.nodeFilter = new NodeFilter([]);
    this.relationshipFilter = new RelationshipFilter([]);
    this.ruleSetFilter = new RuleSetFilter([]);
    this.ruleFilter = new RuleFilter([]);
    this.stageFilter.available(practices);
    this.nodeFilter.available(practices, this.stageFilter.selected);
    this.relationshipFilter.available(this.nodeFilter.selected);
    this.ruleSetFilter.available = ["base", "project"];
    this.ruleFilter.available(this.nodeFilter.selected);
  }

  render(): string {
    const options = this.available ?? [];
    const chosen = this.selected ?? [];
    const boxes = options
      .map((option) => {
        const on = chosen.includes(option) ? " checked" : "";
        return `<label><input type="checkbox" data-filter="${_escape(this.type)}" value="${_escape(option)}"${on}/>${_escape(option)}</label>`;
      })
      .join("");
    return `<fieldset class="filter" data-type="${_escape(this.type)}"><legend>${_escape(this.type)}</legend>${boxes}</fieldset>`;
  }
}

class PracticeFilter {
  type: any;
  selected: any[];
  available: any[];

  constructor(selected: any[] = [], available: any[] = []) {
    this.type = "Practice";
    this.selected = selected;
    this.available = available;
  }
}

class StageFilter {
  type: any;
  selected: any[];
  choices: any[];

  constructor(selected: any[] = []) {
    this.type = "Stage";
    this.selected = selected;
    this.choices = [];
  }

  available(practices: any[]): void {
    const stages: string[] = [];
    const catalog: Record<string, string[]> = {
      Stories: ["Discovery"],
      CleanEngineering: ["Specification", "Implementation"],
      Ddd: ["Specification"],
      Bdd: ["Specification"],
    };
    for (const practice of includedFilterPractices(practices)) {
      for (const stage of catalog[practice] ?? []) {
        if (!stages.includes(stage)) {
          stages.push(stage);
        }
      }
    }
    this.choices = stages;
    if (!this.selected.length) {
      this.selected = [...stages];
    }
  }
}

class NodeFilter {
  type: any;
  selected: any[];
  choices: any[];

  constructor(selected: any[] = []) {
    this.type = "Node";
    this.selected = selected;
    this.choices = [];
  }

  available(practices: any[], stages: any[]): void {
    const catalog: Record<string, Record<string, string[]>> = {
      Stories: { Discovery: ["Increment", "Epic", "Story", "Scenario", "Background", "Step", "Example"] },
      CleanEngineering: {
        Specification: ["OoadClass", "Property", "Relationship", "Operation", "Parameter"],
        Implementation: ["Module"],
      },
      Ddd: { Specification: ["BoundedContext", "Aggregate", "Entity", "EntityRoot", "ValueObject"] },
      Bdd: { Specification: ["Description", "Context", "Observation"] },
    };
    const found: string[] = [];
    for (const practice of includedFilterPractices(practices)) {
      for (const stage of stages) {
        for (const name of catalog[practice]?.[stage] ?? []) {
          if (!found.includes(name)) {
            found.push(name);
          }
        }
      }
    }
    this.choices = found;
    if (!this.selected.length) {
      this.selected = [...found];
    }
  }
}

class RelationshipFilter {
  type: any;
  selected: any[];
  choices: any[];

  constructor(selected: any[] = []) {
    this.type = "Relationship";
    this.selected = selected;
    this.choices = [];
  }

  available(nodes: any[]): void {
    const edges: Record<string, string[]> = {
      Epic: ["owns"],
      Story: ["owns", "demonstrates"],
      OoadClass: ["composition", "aggregation", "associates", "invokes"],
      Operation: ["invokes", "hasParameter", "returns"],
      Property: ["hasType"],
    };
    const found: string[] = [];
    for (const node of nodes) {
      const name = node?.name ?? node;
      for (const edge of edges[name] ?? []) {
        if (!found.includes(edge)) {
          found.push(edge);
        }
      }
    }
    this.choices = found;
    if (!this.selected.length) {
      this.selected = [...found];
    }
  }
}

class RuleSetFilter {
  type: any;
  selected: any[];
  available: any[];

  constructor(selected: any[] = []) {
    this.type = "RuleSet";
    this.selected = selected;
    this.available = ["base", "project"];
  }
}

class RuleFilter {
  type: any;
  selected: any[];
  choices: any[];

  constructor(selected: any[] = []) {
    this.type = "Rule";
    this.selected = selected;
    this.choices = [];
  }

  available(nodes: any[]): void {
    const rules: Record<string, string[]> = {
      OoadClass: ["keep-operations-small-focused"],
      Operation: ["keep-operations-small-focused"],
      Property: ["hide-inner-details"],
    };
    const found: string[] = [];
    for (const node of nodes) {
      const name = node?.name ?? node;
      for (const rule of rules[name] ?? []) {
        if (!found.includes(rule)) {
          found.push(rule);
        }
      }
    }
    this.choices = found;
    if (!this.selected.length) {
      this.selected = [...found];
    }
  }
}

class WebKnowledgeGraphNode extends KnowledgeGraphNode {
  keyword: any;
  origin: SourceRange | null;
  properties: any;
  isFile: any;
  isFolder: any;

  constructor(
    keyword: any,
    origin: SourceRange | null,
    properties: any,
    isFile: any,
    isFolder: any,
  ) {
    super();
    this.keyword = keyword;
    this.origin = origin;
    this.properties = properties;
    this.isFile = isFile;
    this.isFolder = isFolder;
  }

  render(depth = 0, selected: KnowledgeGraphNode | null = null): string {
    const mark = this.isFolder ? "folder" : this.isFile ? "file" : "node";
    const kind = this.nodeType?.name ?? this.properties?.semantic_type ?? "";
    const keyword = this.keyword ? `<span class="keyword">${_escape(this.keyword)}</span>` : "";
    const nested = this.children.map((child) => child.render(depth + 1, selected)).join("");
    const branch = nested ? `<ul class="graph-children">${nested}</ul>` : "";
    const chosen = selected === this || selected?.nodeId === this.nodeId ? " is-selected" : "";
    return `<li data-node-id="${_escape(this.nodeId)}" class="graph-node is-${mark}${chosen}" data-kind="${_escape(kind)}" data-depth="${depth}"><span class="node-name">${keyword}${_escape(this.name)}</span>${branch}</li>`;
  }
}

class PracticeGraph {
  id: any;
  name: any;
  nodes: KnowledgeGraphNode[];
  relationships: KnowledgeGraphEdge[];

  constructor(id: any, name: any, nodes: KnowledgeGraphNode[], relationships: KnowledgeGraphEdge[]) {
    this.id = id;
    this.name = name;
    this.nodes = nodes;
    this.relationships = relationships;
  }

  render(): string {
    const nodes = this.nodes.map((node) => node.render()).join("");
    return `<section class="practice-graph" data-practice="${_escape(this.name)}"><h2>${_escape(this.name)}</h2><ul class="practice-graph-tree">${nodes}</ul></section>`;
  }
}

class SourceRange {
  file: any;
  startLine: any;
  endLine: any;
  text: any;

  constructor(file: any, startLine: any, endLine: any, text: any) {
    this.file = file;
    this.startLine = startLine;
    this.endLine = endLine;
    this.text = text;
  }
}

class RuleHit {
  ruleSlug: any;
  message: any;
  body: any;
  practice: any;
  fidelity: any;
  tag: any;

  constructor(ruleSlug: any, message: any, body: any, practice: any, fidelity: any, tag: any) {
    this.ruleSlug = ruleSlug;
    this.message = message;
    this.body = body;
    this.practice = practice;
    this.fidelity = fidelity;
    this.tag = tag;
  }
}

class NodeRules {
  applicable: any;
  violations: RuleHit[];
  statuses: any;
  details: any;
  tally: any;

  constructor(applicable: any, violations: RuleHit[], statuses: any, details: any, tally: any) {
    this.applicable = applicable;
    this.violations = violations;
    this.statuses = statuses;
    this.details = details;
    this.tally = tally;
  }

  status(ruleSlug: any): any {}

  hasRule(ruleSlug: any): any {}
}

class WorkspaceFile {
  relativePath: any;
  text: any;

  constructor(relativePath: any, text: any) {
    this.relativePath = relativePath;
    this.text = text;
  }
}

export {
  CodeQL,
  StoryModel,
  CleanEngineeringModel,
  DomainDrivenDesignModel,
  KnowledgeGraph,
  KnowledgeGraphNodeType,
  KnowledgeGraphEdgeType,
  KnowledgeGraphNode,
  KnowledgeGraphSource,
  KnowledgeGraphCallSource,
  KnowledgeGraphCall,
  KnowledgeGraphSourceFold,
  KnowledgeGraphPanel,
  KnowledgeGraphEdge,
  KnowledgeGraphStoryModel,
  KnowledgeGraphIncrement,
  KnowledgeGraphEpic,
  KnowledgeGraphStory,
  KnowledgeGraphScenario,
  KnowledgeGraphBackground,
  KnowledgeGraphStep,
  KnowledgeGraphExample,
  KnowledgeGraphCleanEngineeringModel,
  KnowledgeGraphModule,
  KnowledgeGraphOoadClass,
  KnowledgeGraphProperty,
  KnowledgeGraphRelationship,
  KnowledgeGraphOperation,
  KnowledgeGraphParameter,
  KnowledgeGraphDomainDrivenDesignModel,
  KnowledgeGraphBoundedContext,
  KnowledgeGraphAggregate,
  KnowledgeGraphEntity,
  KnowledgeGraphEntityRoot,
  KnowledgeGraphValueObject,
  KnowledgeGraphRepository,
  KnowledgeGraphDomainEvent,
  KnowledgeGraphDomainService,
  KnowledgeGraphSpecification,
  KnowledgeGraphDescription,
  KnowledgeGraphContext,
  KnowledgeGraphObservation,
  KnowledgeGraphFilter,
  PracticeFilter,
  StageFilter,
  NodeFilter,
  RelationshipFilter,
  RuleSetFilter,
  RuleFilter,
  WebKnowledgeGraphNode,
  PracticeGraph,
  SourceRange,
  RuleHit,
  NodeRules,
  WorkspaceFile,
};
