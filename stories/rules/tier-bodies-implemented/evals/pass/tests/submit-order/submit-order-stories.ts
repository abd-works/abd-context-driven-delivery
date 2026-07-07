import type { Story } from '../story-types'

export const SubmitOrder = {
  story:       'Submit Order',
  actor:       'Customer',
  domainTerms: ['Order', 'Cart'],
  evidence:    [],

  orderAccepted: {
    name: 'order accepted for a valid cart',
    given: ['a Cart CART-1 with one Item'],
    interactions: [
      {
        when: ['the Customer submits the Order'],
        then: ['the Order is Confirmed'],
      },
    ],
  },
} as const satisfies Story
