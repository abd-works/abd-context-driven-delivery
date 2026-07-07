// validate-destination-account-stories.ts — specification fidelity with scenario outlines.

import type { Story } from '../../../story-types'

export const VALIDATE_DESTINATION_ACCOUNT_EXAMPLES = [
  {
    scenario: 'Scenario 1',
    destination_account: 'ACH-999',
    account_registration_status: 'registered and active',
    validation_status: 'Valid',
    error_message: '',
  },
  {
    scenario: 'Scenario 2',
    destination_account: 'ACH-000',
    account_registration_status: 'not registered',
    validation_status: 'Invalid',
    error_message: 'Destination account ACH-000 is not registered',
  },
  {
    scenario: 'Scenario 3',
    destination_account: 'ACH-888',
    account_registration_status: 'registered but inactive',
    validation_status: 'Invalid',
    error_message: 'Destination account ACH-888 is inactive',
  },
] as const

export const ValidateDestinationAccount = {
  story: 'Validate destination account',
  actor: 'Treasurer',
  domainTerms: ['Transfer', 'Destination Account', 'Validation Status'],
  evidence: ['Treasury product brief §"Destination validation"'],

  destinationAccountValidationOutcome: {
    name: 'Destination account validation outcome',
    given: [
      'Transfer T-001 has Destination Account {destination_account}',
      'And Destination Account {destination_account} is {account_registration_status} in the system',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice validates the Destination Account on Transfer T-001'],
        then: [
          'Transfer T-001 has Validation Status {validation_status}',
          'And Transfer T-001 remains in status Draft',
          'But an error {error_message} is shown when Validation Status is Invalid',
        ],
      },
    ],
  },
} as const satisfies Story
