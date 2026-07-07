// submit-order-stories.ts
//
// One Story constant per file — the reference architecture shape. This file
// stays fully regeneratable: no test-framework calls, no user-authored logic,
// just literal scenario data. Tier implementations live next door in
// `submit-order-<tier>.ts` (write-once, hand-owned after scaffolding).
//
// Fidelity progression across scenarios (Exploration → Specification):
//
//   1. `submissionSucceeds`              — Exploration happy path (one when-then)
//   2. `submissionRejectedForDeclinedCard` — Specification negative flow
//   3. `submissionOutlineByPaymentStatus`  — Specification outline (multi-then)

import type { Story } from '../../story-types'

export const SubmitOrder = {
  story:       'Submit Order',
  actor:       'Customer',
  domainTerms: ['Order', 'Cart', 'Payment Method', 'Order Number', 'Order Status'],
  evidence: [
    'Checkout workshop 2026-05-04 — happy-path wall walk',
    'API spec v3 — POST /orders §"submission errors"',
  ],

  submissionSucceeds: {
    name: 'order accepted for a valid cart and payment method',
    given: [
      'a Cart CART-9001 containing 3 Items totalling 149.98 USD',
      'And a Payment Method Visa 4242 with status authorised',
    ],
    interactions: [
      {
        when: ['the Customer submits the Order'],
        then: [
          'an Order is created with status placed',
          'And an Order Number matching ORD-<7 digits> is returned',
          'And the Cart is emptied',
        ],
      },
    ],
  },

  submissionRejectedForDeclinedCard: {
    name: 'order rejected when the payment method is declined',
    given: [
      'a Cart CART-9002 totalling 89.50 USD',
      'And a Payment Method MasterCard 5150 in status declined',
    ],
    interactions: [
      {
        when: ['the Customer submits the Order'],
        then: [
          'the Order is rejected with reason payment_declined',
          'But the Cart contents are preserved for retry',
        ],
      },
    ],
  },

  submissionOutlineByPaymentStatus: {
    name: 'submission outcome varies with payment method status',
    given: [
      'a Cart with a known total and currency',
      'And a Payment Method with a known status',
    ],
    interactions: [
      {
        when: ['the Customer submits the Order'],
        then: [
          'the Order status is set for an authorised payment to placed',
          'And the Order status is set for a declined payment to rejected',
          'And the Order status is set for an expired payment to rejected',
        ],
      },
    ],
  },
} as const satisfies Story
