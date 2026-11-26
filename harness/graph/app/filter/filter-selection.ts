import type { FilterChoicesData } from '@cdd/harness/graph/graph';

export type FilterSelection = {
  practices: string[];
  overlays: string[];
  node_types: string[];
  relationships: string[];
  rules: string[];
  violations: boolean;
};

// The graph's node filter for what a person chose: node types as types, and rules only once violations are asked for.
export function nodeFilter(selection: FilterSelection): Record<string, unknown> {
  return {
    ...(selection.practices.length ? { practices: selection.practices } : {}),
    ...(selection.node_types.length ? { types: selection.node_types } : {}),
    ...(selection.relationships.length ? { relationships: selection.relationships } : {}),
    ...(selection.violations ? { violations: true, rules: selection.rules } : {}),
  };
}

// A selection that filters nothing, and the choices offered before Python's Filter answers any.
export const NO_FILTER: FilterSelection = { practices: [], overlays: [], node_types: [], relationships: [], rules: [], violations: false };
export const NO_CHOICES: FilterChoicesData = { node_types: [], offered_node_types: [], relationships: [], rules: [] };

// The selection with the node types, relationships, and rules Python's Filter chose for it.
export function chosen(next: FilterSelection, choices: FilterChoicesData): FilterSelection {
  return { ...next, node_types: choices.node_types, relationships: choices.relationships, rules: choices.rules };
}
