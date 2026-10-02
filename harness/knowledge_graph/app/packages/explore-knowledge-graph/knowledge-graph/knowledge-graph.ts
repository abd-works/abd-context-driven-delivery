class CodeQL {
  root: any;
  database: any;

  constructor(root: any, database: any) {
    this.root = root;
    this.database = database;
  }

  populate(): void {
    storyModel.load();
    cleanEngineeringModel.load();
    domainDrivenDesignModel.load();
  }
}

class StoryModel {
}

class CleanEngineeringModel {
}

class DomainDrivenDesignModel {
}

class KnowledgeGraph {
  storyModel: any;
  ceModel: any;
  domainDrivenDesignModel: any;
  description: any;
  nodes: any;
  kinds: any;
  folder: any;
  createDatabase: any;
  copyMasterToWorkingCopy: any;
  copyWorkingCopyToMaster: any;
  filter: any;
  matching: any;
  selected: any;
  expanded: any;

  constructor(storyModel: any, ceModel: any, domainDrivenDesignModel: any, description: any, nodes: any, kinds: any, folder: any, createDatabase: any, copyMasterToWorkingCopy: any, copyWorkingCopyToMaster: any, filter: any, matching: any, selected: any, expanded: any) {
    KnowledgeGraphStoryModel storyModel();
    KnowledgeGraphCleanEngineeringModel ceModel();
    KnowledgeGraphDomainDrivenDesignModel domainDrivenDesignModel();
    KnowledgeGraphDescription description();
    this.storyModel = storyModel;
    this.ceModel = ceModel;
    this.domainDrivenDesignModel = domainDrivenDesignModel;
    this.description = description;
    this.nodes = nodes;
    this.kinds = kinds;
    this.folder = folder;
    this.createDatabase = createDatabase;
    this.copyMasterToWorkingCopy = copyMasterToWorkingCopy;
    this.copyWorkingCopyToMaster = copyWorkingCopyToMaster;
    this.filter = filter;
    this.matching = matching;
    this.selected = selected;
    this.expanded = expanded;
  }

  saveKnowledgeGraph(): void {
    CodeStoryModel.load();
    CodeCleanEngineeringModel.load();
    CodeDomainDrivenDesignModel.load();
    KnowledgeGraphStoryModel.save();
    KnowledgeGraphCleanEngineeringModel.save();
    KnowledgeGraphDomainDrivenDesignModel.save();
  }
  loadKnowledgeGraph(path): void {
    KnowledgeGraphStoryModel.load path();
    KnowledgeGraphCleanEngineeringModel.load path();
    KnowledgeGraphDomainDrivenDesignModel.load path();
    KnowledgeGraphDescription.load path();
  }
  refreshMaster(): void {
    copyWorkingCopyToMaster();
    saveKnowledgeGraph();
    loadKnowledgeGraph path();
  }
  reloadWorkingCopy(): void {
    saveKnowledgeGraph();
    copyWorkingCopyToMaster();
    loadKnowledgeGraph path();
  }
  updateWorkingCopy(paths): void {
    saveKnowledgeGraph();
    loadKnowledgeGraph path();
  }
}

class KnowledgeGraphNodeType {
  name: any;
  practice: any;
  stage: any;
  edgeTypes: any;

  constructor(name: any, practice: any, stage: any, edgeTypes: any) {
    this.name = name;
    this.practice = practice;
    this.stage = stage;
    this.edgeTypes = edgeTypes;
  }

}

class KnowledgeGraphEdgeType {
  name: any;
  fromType: any;
  toType: any;
  inverse: any;
  cardinality: any;

  constructor(name: any, fromType: any, toType: any, inverse: any, cardinality: any) {
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
  nodeType: any;
  source: any;
  nodeId: any;
  edges: any;
  panel: any;
  rules: any;

  constructor(name: any, sequentialOrder: any, nodeType: any, source: any, nodeId: any, edges: any, panel: any, rules: any) {
    source();
    panel.source();
    this.name = name;
    this.sequentialOrder = sequentialOrder;
    this.nodeType = nodeType;
    this.source = source;
    this.nodeId = nodeId;
    this.edges = edges;
    this.panel = panel;
    this.rules = rules;
  }

  navigateTo(edge): void {
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

  source(): void {
    text from the file();
  }
}

/**
 * KnowledgeGraphSource
 */
class KnowledgeGraphCallSource extends KnowledgeGraphSource {
  calls: any;
  folds: any;
  loadCalls: any;
  insertCalls: any;
  loadFolds: any;

  constructor(calls: any, folds: any, loadCalls: any, insertCalls: any, loadFolds: any) {
    this.calls = calls;
    this.folds = folds;
    this.loadCalls = loadCalls;
    this.insertCalls = insertCalls;
    this.loadFolds = loadFolds;
  }

  source(): void {
    super.source();
    loadCalls();
    insertCalls();
    loadFolds();
  }
}

class KnowledgeGraphCall {
  line: any;
  sequentialOrder: any;
  operation: any;

  constructor(line: any, sequentialOrder: any, operation: any) {
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
  source: any;
  language: any;
  open: any;
  theme: any;
  mount: any;

  constructor(source: any, language: any, open: any, theme: any, mount: any) {
    this.source = source;
    this.language = language;
    this.open = open;
    this.theme = theme;
    this.mount = mount;
  }

}

class KnowledgeGraphEdge {
  edgeType: any;
  from: any;
  to: any;

  constructor(edgeType: any, from: any, to: any) {
    this.edgeType = edgeType;
    this.from = from;
    this.to = to;
  }

}

/**
 * StoryModel : KnowledgeGraphNode
 */
class KnowledgeGraphStoryModel extends StoryModel {
  epicType: any;
  incrementType: any;

  constructor(epicType: any, incrementType: any) {
    this.epicType = epicType;
    this.incrementType = incrementType;
  }

  save(saves, a, complete, knowledge, graph): void {
  }
  load(path): void {
    loadContent();
    loadEpics();
    loadIncrements();
  }
}

/**
 * Increment : KnowledgeGraphNode
 */
class KnowledgeGraphIncrement extends Increment {

  constructor() {
  }

}

/**
 * Epic : KnowledgeGraphNode
 */
class KnowledgeGraphEpic extends Epic {
  storyType: any;

  constructor(storyType: any) {
    loadEpics();
    loadStories();
    loadExamples();
    this.storyType = storyType;
  }

}

/**
 * Story : KnowledgeGraphNode
 */
class KnowledgeGraphStory extends Story {
  scenarioType: any;

  constructor(scenarioType: any) {
    loadScenarios();
    loadBackgrounds();
    this.scenarioType = scenarioType;
  }

}

/**
 * Scenario : KnowledgeGraphNode
 */
class KnowledgeGraphScenario extends Scenario {

  constructor() {
    loadBackground();
    loadSteps();
    loadExamples();
  }

}

/**
 * Background : KnowledgeGraphNode
 */
class KnowledgeGraphBackground extends Background {

  constructor() {
    loadSteps();
  }

}

/**
 * Step : KnowledgeGraphNode
 */
class KnowledgeGraphStep extends Step {

  constructor() {
  }

}

/**
 * Example : KnowledgeGraphNode
 */
class KnowledgeGraphExample extends Example {

  constructor() {
  }

}

/**
 * CleanEngineeringModel : KnowledgeGraphNode
 */
class KnowledgeGraphCleanEngineeringModel extends CleanEngineeringModel {
  moduleType: any;
  save: any;

  constructor(moduleType: any, save: any) {
    this.moduleType = moduleType;
    this.save = save;
  }

  load(path): void {
    loadModules();
  }
}

/**
 * Module : KnowledgeGraphNode
 */
class KnowledgeGraphModule extends Module {
  classType: any;

  constructor(classType: any) {
    loadModules();
    loadClasses();
    this.classType = classType;
  }

}

/**
 * OoadClass : KnowledgeGraphNode
 */
class KnowledgeGraphOoadClass extends OoadClass {
  propertyType: any;
  operationType: any;
  relationshipType: any;

  constructor(propertyType: any, operationType: any, relationshipType: any) {
    loadProperties();
    loadOperations();
    loadRelationships();
    this.propertyType = propertyType;
    this.operationType = operationType;
    this.relationshipType = relationshipType;
  }

}

/**
 * Property : KnowledgeGraphNode
 */
class KnowledgeGraphProperty extends Property {

  constructor() {
    loadRelationship();
  }

}

/**
 * Relationship : KnowledgeGraphNode
 */
class KnowledgeGraphRelationship extends Relationship {

  constructor() {
  }

}

/**
 * Operation : KnowledgeGraphNode
 */
class KnowledgeGraphOperation extends Operation {

  constructor() {
    loadParameters();
  }

}

/**
 * Parameter : KnowledgeGraphNode
 */
class KnowledgeGraphParameter extends Parameter {

  constructor() {
  }

}

/**
 * DomainDrivenDesignModel : KnowledgeGraphNode
 */
class KnowledgeGraphDomainDrivenDesignModel extends DomainDrivenDesignModel {
  boundedContextType: any;
  save: any;

  constructor(boundedContextType: any, save: any) {
    this.boundedContextType = boundedContextType;
    this.save = save;
  }

  load(path): void {
    loadBoundedContexts();
  }
}

/**
 * BoundedContext : KnowledgeGraphNode
 */
class KnowledgeGraphBoundedContext extends BoundedContext {

  constructor() {
    super.KnowledgeGraphModule();
  }

}

/**
 * Aggregate : KnowledgeGraphNode
 */
class KnowledgeGraphAggregate extends Aggregate {

  constructor() {
    loadRoot();
  }

}

/**
 * Entity : KnowledgeGraphNode
 */
class KnowledgeGraphEntity extends Entity {

  constructor() {
    loadProperties();
    loadOperations();
  }

}

/**
 * Entity : KnowledgeGraphNode
 */
class KnowledgeGraphEntityRoot extends Entity {

  constructor() {
    loadProperties();
    loadOperations();
  }

}

/**
 * ValueObject : KnowledgeGraphNode
 */
class KnowledgeGraphValueObject extends ValueObject {

  constructor() {
    loadProperties();
    loadOperations();
  }

}

/**
 * Repository : KnowledgeGraphNode
 */
class KnowledgeGraphRepository extends Repository {

  constructor() {
    loadProperties();
    loadOperations();
  }

}

/**
 * DomainEvent : KnowledgeGraphNode
 */
class KnowledgeGraphDomainEvent extends DomainEvent {

  constructor() {
    loadProperties();
    loadOperations();
  }

}

/**
 * DomainService : KnowledgeGraphNode
 */
class KnowledgeGraphDomainService extends DomainService {

  constructor() {
    loadProperties();
    loadOperations();
  }

}

/**
 * Specification : KnowledgeGraphNode
 */
class KnowledgeGraphSpecification extends Specification {

  constructor() {
  }

}

/**
 * Description : KnowledgeGraphNode
 */
class KnowledgeGraphDescription extends Description {

  constructor() {
    loadContexts();
  }

}

/**
 * Context : KnowledgeGraphNode
 */
class KnowledgeGraphContext extends Context {

  constructor() {
    loadObservations();
    loadContexts();
  }

}

/**
 * Observation : KnowledgeGraphNode
 */
class KnowledgeGraphObservation extends Observation {

  constructor() {
  }

}

class KnowledgeGraphFilter {
  type: any;
  selected: any;
  available: any;

  constructor(type: any, selected: any, available: any) {
    StageFilter.available practices();
    NodeFilter.available practices stages();
    RelationshipFilter.available nodes();
    RuleSetFilter.available();
    RuleFilter.available nodes();
    this.type = type;
    this.selected = selected;
    this.available = available;
  }

}

/**
 * KnowledgeGraphFilter
 */
class PracticeFilter extends KnowledgeGraphFilter {
  selected: any;
  available: any;

  constructor(selected: any, available: any) {
    this.selected = selected;
    this.available = available;
  }

}

/**
 * KnowledgeGraphFilter
 */
class StageFilter extends KnowledgeGraphFilter {
  selected: any;

  constructor(selected: any) {
    this.selected = selected;
  }

  available(practices): void {
  }
}

/**
 * KnowledgeGraphFilter
 */
class NodeFilter extends KnowledgeGraphFilter {
  selected: any;

  constructor(selected: any) {
    this.selected = selected;
  }

  available(practices, stages): void {
  }
}

/**
 * KnowledgeGraphFilter
 */
class RelationshipFilter extends KnowledgeGraphFilter {
  selected: any;

  constructor(selected: any) {
    this.selected = selected;
  }

  available(nodes): void {
  }
}

/**
 * KnowledgeGraphFilter
 */
class RuleSetFilter extends KnowledgeGraphFilter {
  selected: any;
  available: any;

  constructor(selected: any, available: any) {
    this.selected = selected;
    this.available = available;
  }

}

/**
 * KnowledgeGraphFilter
 */
class RuleFilter extends KnowledgeGraphFilter {
  selected: any;

  constructor(selected: any) {
    this.selected = selected;
  }

  available(nodes): void {
  }
}

/**
 * KnowledgeGraphNode
 */
class WebKnowledgeGraphNode extends KnowledgeGraphNode {
  keyword: any;
  origin: any;
  properties: any;
  isFile: any;
  isFolder: any;

  constructor(keyword: any, origin: any, properties: any, isFile: any, isFolder: any) {
    this.keyword = keyword;
    this.origin = origin;
    this.properties = properties;
    this.isFile = isFile;
    this.isFolder = isFolder;
  }

}

class PracticeGraph {
  id: any;
  name: any;
  nodes: any;
  relationships: any;

  constructor(id: any, name: any, nodes: any, relationships: any) {
    this.id = id;
    this.name = name;
    this.nodes = nodes;
    this.relationships = relationships;
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
  violations: any;
  statuses: any;
  details: any;
  tally: any;

  constructor(applicable: any, violations: any, statuses: any, details: any, tally: any) {
    this.applicable = applicable;
    this.violations = violations;
    this.statuses = statuses;
    this.details = details;
    this.tally = tally;
  }

  status(ruleSlug): void {
  }
  hasRule(ruleSlug): void {
  }
}

class WorkspaceFile {
  relativePath: any;
  text: any;

  constructor(relativePath: any, text: any) {
    this.relativePath = relativePath;
    this.text = text;
  }

}
