/** Pattern overlay ids from cdd_guidance/patterns and display labels in the explorer. */

export const LERN_DDD_NODE_TYPES = [
  'NodeRoot',
  'ClientRoot',
  'View',
  'Route',
  'JsonStore',
  'NodeRepository',
] as const;

export const LERN_STORY_NODE_TYPES = ['StoryShared', 'DomainSpec', 'ServerSpec', 'PlaywrightSpec'] as const;

const CATALOG_LABELS: Record<string, string> = {
  lern_domain_driven: 'Lern domain driven',
};

export function overlayCatalogLabel(patternId: string): string {
  return CATALOG_LABELS[patternId] ?? patternId.replace(/_/g, ' ');
}

export function overlayPathLabel(path: string): string {
  const trimmed = path.replace(/[/\\]+$/, '');
  const base = trimmed.split(/[/\\]/).pop() || path;
  return overlayCatalogLabel(base);
}

export function lernOverlayActive(overlays: string[]): boolean {
  return overlays.some((item) => item.replace(/\\/g, '/').includes('lern_domain_driven'));
}

export function lernNodeTypesFromCatalog(dddNodeTypes: string[]): string[] {
  const wanted = new Set<string>([...LERN_DDD_NODE_TYPES, ...LERN_STORY_NODE_TYPES]);
  return dddNodeTypes.filter((type) => wanted.has(type));
}
