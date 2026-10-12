import type { InventoryBundle, PracticeInventory } from './filter/FilterClient';

export function normalizeInventoryBundle(raw: unknown): InventoryBundle {
  if (raw && typeof raw === 'object' && 'practices' in raw) {
    const bundle = raw as InventoryBundle;
    return {
      practices: bundle.practices ?? {},
      overlays: bundle.overlays ?? [],
      available_overlays: bundle.available_overlays ?? [],
    };
  }
  return {
    practices: (raw ?? {}) as Record<string, PracticeInventory>,
    overlays: [],
    available_overlays: [],
  };
}
