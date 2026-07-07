import type { Story } from '../../story-types'

export const ViewCurrentOrderStatusMainFlow = {
  story:       'View Current Order Status',
  actor:       'Customer',
  domainTerms: ['Order', 'Order Status', 'Timeline Event'],
  evidence:    ['Order tracking discovery session 2026-05-11'],

  mainFlow: {
    name: 'customer sees the latest status of a placed order',
    given: [
      'an Order "ORD-4200077" in status placed',
      'And a Timeline Event "payment authorised" recorded 10 minutes ago',
    ],
    interactions: [
      {
        when: [
          'the Customer opens the order detail view',
        ],
        then: [
          'the Order status placed is displayed prominently',
          'And the Timeline shows the payment-authorised event',
        ],
      },
    ],
  },

} as const satisfies Story
