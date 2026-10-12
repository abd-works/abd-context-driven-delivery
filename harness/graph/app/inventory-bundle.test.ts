import { expect, it } from 'vitest';
import { normalizeInventoryBundle } from './inventory-bundle';

it('should read a practices bundle from the inventory api', () => {
  const bundle = normalizeInventoryBundle({
    practices: { stories: { tree: { type: 'Practice', name: 'stories', node_id: 'p', children: [] } } },
    overlays: ['lern_domain_driven'],
    available_overlays: ['lern_domain_driven'],
  });
  expect(bundle.practices.stories?.tree?.name).toBe('stories');
  expect(bundle.overlays).toEqual(['lern_domain_driven']);
});

it('should accept a legacy flat practice map', () => {
  const bundle = normalizeInventoryBundle({
    stories: { tree: { type: 'Practice', name: 'stories', node_id: 'p', children: [] } },
  });
  expect(bundle.practices.stories?.tree?.name).toBe('stories');
  expect(bundle.overlays).toEqual([]);
});
