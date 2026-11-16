import type { InventoryData, PracticeInventoryData } from '@cdd/harness/graph/graph';

export function normalizeInventoryBundle(raw: unknown): InventoryData {
  if (raw && typeof raw === 'object' && 'practices' in raw) {
    const bundle = raw as InventoryData;
    return {
      practices: bundle.practices ?? {},
      overlays: bundle.overlays ?? [],
      available_overlays: bundle.available_overlays ?? [],
    };
  }
  return {
    practices: (raw ?? {}) as Record<string, PracticeInventoryData>,
    overlays: [],
    available_overlays: [],
  };
}
