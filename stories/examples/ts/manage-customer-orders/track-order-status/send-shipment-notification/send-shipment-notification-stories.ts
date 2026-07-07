import type { Story } from '../../story-types'

export const SendShipmentNotification = {
  story:       'Send Shipment Notification',
  actor:       'System',
  domainTerms: ['Shipment', 'Shipment Notification', 'Tracking Number', 'Notification Channel'],
  evidence:    [],

} as const satisfies Story
