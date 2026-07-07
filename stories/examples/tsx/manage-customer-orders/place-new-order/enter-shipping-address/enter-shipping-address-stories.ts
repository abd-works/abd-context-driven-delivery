import type { Story } from '../../story-types'

export const EnterShippingAddress = {
  story:       'Enter Shipping Address',
  actor:       'Customer',
  domainTerms: ['Shipping Address', 'Address Line', 'Postal Code', 'Country'],
  evidence:    [],

} as const satisfies Story
