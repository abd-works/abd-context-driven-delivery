import { expect, it } from 'vitest';
import { normalizeInventoryBundle } from './inventory-bundle';

it('should read a practices bundle from the inventory api', () => {
  const bundle = normalizeInventoryBundle({
    practices: { stories: { node_counts: { Story: 3 }, edge_count: 2, node_types: ['Story'], edge_types: [], rules: [] } },
    overlays: ['lern_domain_driven'],
    available_overlays: ['lern_domain_driven'],
  });
  expect(bundle.practices.stories?.node_counts).toEqual({ Story: 3 });
  expect(bundle.overlays).toEqual(['lern_domain_driven']);
});

it('should accept a legacy flat practice map', () => {
  const bundle = normalizeInventoryBundle({
    stories: { node_counts: { Story: 3 }, edge_count: 2, node_types: ['Story'], edge_types: [], rules: [] },
  });
  expect(bundle.practices.stories?.node_counts).toEqual({ Story: 3 });
  expect(bundle.overlays).toEqual([]);
});
