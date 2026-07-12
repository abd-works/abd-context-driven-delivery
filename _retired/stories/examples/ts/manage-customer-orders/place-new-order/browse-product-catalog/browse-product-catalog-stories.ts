import type { Story } from '../../story-types'

export const BrowseProductCatalog = {
  story:       'Browse Product Catalog',
  actor:       'Customer',
  domainTerms: ['Product Catalog', 'Product', 'Category'],
  evidence:    [],

} as const satisfies Story
