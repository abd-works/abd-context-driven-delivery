import type { Story } from '../../story-types'

export const RequestOrderCancellation = {
  story:       'Request Order Cancellation',
  actor:       'Customer',
  domainTerms: ['Order', 'Cancellation Request', 'Cancellation Reason', 'Order Status'],
  evidence:    ['Cancellation policy doc v2 §3', 'Customer support call review 2026-05-18'],

  cancellationAcceptedBeforeShipment: {
    name: 'cancellation accepted while the order is still placed',
    given: [
      'an Order "ORD-4200080" in status placed',
    ],
    interactions: [
      {
        when: [
          'the Customer submits a Cancellation Request with reason "changed mind"',
        ],
        then: [
          'the Order status changes to cancelled',
          'And the Cancellation Request records reason "changed mind"',
        ],
      },
    ],
  },

  cancellationRejectedAfterShipment: {
    name: 'cancellation rejected once the shipment is on the way',
    given: [
      'an Order "ORD-4200081" in status shipped',
    ],
    interactions: [
      {
        when: [
          'the Customer submits a Cancellation Request',
        ],
        then: [
          'the Cancellation Request is rejected',
          'But the Order remains in status shipped',
        ],
      },
    ],
  },

} as const satisfies Story
