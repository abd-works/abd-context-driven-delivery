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
