/** Practice names, CDD stages, and relationship kinds for explorer filters. */

export const PRACTICES = [
  'bdd',
  'clean_engineering',
  'ddd',
  'stories',
] as const;

export const STAGES = [
  'discovery',
  'specification',
  'implementation',
] as const;

export const RELATIONSHIP_KINDS = [
  'owns',
  'belongsTo',
  'associates',
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
  'describes',
  'namesState',
  'observes',
  'usedBy',
] as const;

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

export function stageFor(fidelity: string | null | undefined): string {
  if (!fidelity) {
    return '';
  }
  if ((STAGES as readonly string[]).includes(fidelity)) {
    return fidelity;
  }
  return STAGE_BY_FIDELITY[fidelity] ?? '';
}
