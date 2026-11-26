import type { InventoryData } from '@cdd/harness/graph/graph';

// The inventory the graph answers, with nothing in each part it left out.
export function normalizeInventoryBundle(raw: unknown): InventoryData {
  const bundle = (raw ?? {}) as Partial<InventoryData>;
  return {
    practices: bundle.practices ?? {},
    overlays: bundle.overlays ?? [],
    available_overlays: bundle.available_overlays ?? [],
  };
}
