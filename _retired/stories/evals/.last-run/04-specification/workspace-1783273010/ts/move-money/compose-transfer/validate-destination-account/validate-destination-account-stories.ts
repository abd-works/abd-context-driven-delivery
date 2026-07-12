import type { Story } from '../../../story-types'

export const ValidateDestinationAccount = {
  story:       'Validate destination account',
  actor:       'Treasurer',
  domainTerms: [],
  evidence:    [],

  treasurerValidatesARegisteredDestinationAccount: {
    name: 'Treasurer validates a registered destination account',
    given: [
      'Transfer T-001 has Destination Account ACH-999',
      'And Destination Account ACH-999 is registered and active in the system',
    ],
    interactions: [
      {
        when: [
          'the Treasurer Alice validates the Destination Account on Transfer T-001',
        ],
        then: [
          'Transfer T-001 has Validation Status Valid',
          'And Transfer T-001 remains in status Draft',
        ],
      },
    ],
  },
} as const satisfies Story
