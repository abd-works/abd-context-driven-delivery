import type { Story } from '../../story-types'

export const AddItemToCart = {
  story:       'Add Item To Cart',
  actor:       'Customer',
  domainTerms: ['Cart', 'Product', 'Cart Item', 'Quantity'],
  evidence:    [],

} as const satisfies Story
