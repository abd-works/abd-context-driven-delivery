/** Practice names, CDD stages, and relationship kinds for explorer filters. */

export const PRACTICES = [
  'bdd',
  'clean_engineering',
  'ddd',
  'stories',
] as const;

/** Types each practice view lists, including types a workspace has not tagged yet. */
export const NODE_TYPES_BY_PRACTICE: Record<string, string[]> = {
  clean_engineering: [
    'Module',
    'Package',
    'OoadClass',
    'Property',
    'Operation',
    'Parameter',
    'FieldGroup',
    'File',
    'CleanEngineeringModel',
  ],
  stories: [
    'Epic',
    'SubEpic',
    'Story',
    'Background',
    'Scenario',
    'Step',
    'Example',
    'StoryModel',
  ],
  ddd: [
    'BoundedContext',
    'Aggregate',
    'EntityRoot',
    'Entity',
    'ValueObject',
    'Repository',
    'DomainEvent',
    'DomainService',
    'Specification',
    'OoadClass',
    'Property',
    'Operation',
    'Parameter',
    'FieldGroup',
  ],
  bdd: ['Description', 'Context', 'Observation'],
};

export const STAGES = [
  'discovery',
  'specification',
  'implementation',
] as const;

export const RELATIONSHIP_KINDS = [
  'owns',
  'belongsTo',
  'associates',
  'composition',
  'aggregation',
  'dependsOn',
  'hasType',
  'hasParameter',
  'returns',
  'invokes',
  'hasIdentity',
  'root',
  'accesses',
  'scopes',
  'scopedBy',
  'uses',
  'demonstrates',
  'demonstratedThrough',
  'relative',
  'loads',
  'retrievedUsing',
  'describes',
  'namesState',
  'observes',
  'usedBy',
] as const;

/** Connectors a node type can carry. The filter lists these, not only edges already stored. */
export const CONNECTORS_BY_TYPE: Record<string, readonly string[]> = {
  Module: ['owns', 'belongsTo'],
  Package: ['owns', 'belongsTo'],
  Epic: ['owns', 'demonstrates'],
  SubEpic: ['owns'],
  Story: ['owns', 'demonstrates', 'demonstratedThrough'],
  Scenario: ['owns'],
  Step: ['owns', 'invokes'],
  Example: ['demonstratedThrough'],
  OoadClass: ['owns', 'relative', 'composition', 'aggregation', 'associates', 'invokes', 'dependsOn'],
  Operation: ['owns', 'invokes', 'hasParameter', 'returns'],
  Property: ['hasType'],
  Parameter: ['hasType'],
  BoundedContext: ['owns'],
  Aggregate: ['owns', 'accesses'],
  Entity: ['hasIdentity', 'relative'],
  EntityRoot: ['hasIdentity', 'root', 'relative'],
  Description: ['observes'],
  Context: ['scopes'],
  Observation: ['observes'],
};

export const INVERSE_KIND: Record<string, string> = {
  owns: 'belongsTo',
  belongsTo: 'owns',
  demonstrates: 'demonstratedThrough',
  demonstratedThrough: 'demonstrates',
  scopes: 'scopedBy',
  scopedBy: 'scopes',
  uses: 'usedBy',
  usedBy: 'uses',
  associates: 'associates',
  composition: 'composition',
  aggregation: 'aggregation',
};

/** Fidelity → stage from each practice markdown **Stage:** block. */
export const STAGE_BY_FIDELITY: Record<string, string> = {
  modules: 'discovery',
  language: 'discovery',
  story_map: 'discovery',
  bounded_context: 'discovery',
  ia: 'discovery',
  model: 'specification',
  scenarios: 'specification',
  building_blocks: 'specification',
  mockup: 'specification',
  behavior: 'specification',
  code: 'implementation',
  acceptance_tests: 'implementation',
  tactics: 'implementation',
  front_end_code: 'implementation',
};

export const RULE_GUIDANCE: Record<string, string> = {
  'keep-operations-small-focused':
    'Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.',
  'prefer-class-operations':
    'Put operations on a class. Do not leave functions or variables hanging off the module or package.',
  'prefer-instance-operations':
    'Keep operations on the instance. Do not mark them @staticmethod or @classmethod. A single creation method — instance, create, or from_* — may be static so callers can obtain the object.',
  'extensions-live-with-the-domain':
    'Domain extensions of a framework belong in the domain module — a nested package under that domain is fine. Do not host them in the base framework package.',
};

const FIDELITY_ORDER: Record<string, string[]> = {
  stories: ['acceptance_tests', 'scenarios', 'story_map'],
  clean_engineering: ['code', 'model', 'modules', 'language'],
  ddd: ['tactics', 'building_blocks', 'bounded_context'],
  bdd: ['behavior'],
  ux: ['front_end_code', 'mockup', 'ia'],
};

const FIDELITY_SCOPE: Record<string, Record<string, string[]>> = {
  stories: {
    acceptance_tests: ['Step', 'Example'],
    scenarios: ['Scenario', 'Background', 'Step', 'Example'],
    story_map: ['Epic', 'Story', 'StoryModel'],
  },
  clean_engineering: {
    code: ['OoadClass', 'Property', 'Operation', 'Parameter', 'FieldGroup', 'Module', 'File'],
    model: ['Module', 'File', 'OoadClass', 'Property', 'Operation', 'Parameter', 'FieldGroup', 'CleanEngineeringModel'],
    modules: ['Module', 'CleanEngineeringModel'],
    language: ['Module', 'CleanEngineeringModel'],
  },
  ddd: {
    tactics: ['Entity', 'EntityRoot', 'ValueObject', 'Repository', 'DomainEvent', 'DomainService', 'OoadClass', 'Property', 'Operation', 'Parameter', 'FieldGroup'],
    building_blocks: ['Entity', 'EntityRoot', 'ValueObject', 'Repository', 'DomainEvent', 'DomainService', 'Aggregate', 'BoundedContext', 'OoadClass', 'Property', 'Operation', 'Parameter', 'FieldGroup'],
    bounded_context: ['BoundedContext', 'Aggregate', 'Module'],
  },
  bdd: {
    behavior: ['Description', 'Context', 'Observation'],
  },
  ux: {
    front_end_code: ['Screen'],
    mockup: ['Screen'],
    ia: ['Screen'],
  },
};

export function closestFidelity(practice: string, semanticType: string): string {
  for (const fidelity of FIDELITY_ORDER[practice] ?? []) {
    if ((FIDELITY_SCOPE[practice]?.[fidelity] ?? []).includes(semanticType)) {
      return fidelity;
    }
  }
  return '';
}

function expandPractices(practices: string[]): string[] {
  const found = [...practices];
  if (found.includes('ddd') && !found.includes('clean_engineering')) {
    found.push('clean_engineering');
  }
  return found;
}

export function stagesForPractices(practices: string[]): string[] {
  const found = new Set<string>();
  for (const practice of expandPractices(practices)) {
    for (const fidelity of FIDELITY_ORDER[practice] ?? []) {
      const stage = stageFor(fidelity);
      if (stage) {
        found.add(stage);
      }
    }
  }
  return STAGES.filter((stage) => found.has(stage));
}

/** Every node type the practices define. A narrower stage list keeps only that stage's types. */
export function nodeTypesFor(practices: string[], stages: string[] | null): string[] {
  const found: string[] = [];
  const push = (name: string) => {
    if (name && !found.includes(name)) {
      found.push(name);
    }
  };
  for (const practice of expandPractices(practices)) {
    const catalog = NODE_TYPES_BY_PRACTICE[practice] ?? [];
    const practiceStages = stagesForPractices([practice]);
    const limit =
      stages && stages.length > 0 && stages.length < practiceStages.length ? stages : null;
    if (!limit) {
      for (const name of catalog) {
        push(name);
      }
      continue;
    }
    for (const fidelity of FIDELITY_ORDER[practice] ?? []) {
      if (!limit.includes(stageFor(fidelity))) {
        continue;
      }
      for (const name of FIDELITY_SCOPE[practice]?.[fidelity] ?? []) {
        push(name);
      }
    }
  }
  return found;
}

export function stageFor(fidelity: string | null | undefined): string {
  if (!fidelity) {
    return '';
  }
  if ((STAGES as readonly string[]).includes(fidelity)) {
    return fidelity;
  }
  return STAGE_BY_FIDELITY[fidelity] ?? '';
}
