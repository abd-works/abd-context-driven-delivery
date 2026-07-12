import type { Story } from '../../story-types'

export const ProcessCancellationRefund = {
  story:       'Process Cancellation Refund',
  actor:       'System',
  domainTerms: ['Cancellation', 'Refund', 'Refund Amount', 'Payment Method'],
  evidence:    [],

} as const satisfies Story
