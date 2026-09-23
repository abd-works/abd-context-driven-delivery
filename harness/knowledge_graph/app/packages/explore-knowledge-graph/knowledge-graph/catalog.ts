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
    'Keep each operation short enough to read as one thought — under 20 lines. When it grows, extract a private helper whose name says why that slice exists.',
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
