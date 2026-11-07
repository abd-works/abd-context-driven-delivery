/**
 * States each behavior of Add Backlog Item and Start Backlog Item once. Reaches the tier only through its driver.
 * The sentences match kanban_tools_spec.py.
 */
import { shareBehavior } from 'test-utils/behavior-test/behavior-test'

export type BacklogItemsDriver = {
  add: (title: string, text: string) => Promise<void>
  start: (title: string) => Promise<void>
  moveToBacklog: (ticket: string) => Promise<void>
  textOf: (title: string) => Promise<string>
  isInBacklog: (title: string) => Promise<boolean>
  columnOfTicket: (title: string) => Promise<string>
  stateOfWork: (title: string, fidelity: string) => Promise<string>
}

export const backlogItemsBehavior = shareBehavior<BacklogItemsDriver>(({ describe, it, before, expect, driver }) => {
  describe('a backlog item', () => {
    describe('that a person has added', () => {
      before(() => driver().add('Gift cards', 'Sell them at the till.'))

      it('should show the item in the Backlog with its text', async () => {
        expect(await driver().textOf('Gift cards')).toEqual('Sell them at the till.')
      })
    })

    describe('that a person has started', () => {
      before(() => driver().start('Search the catalog'))

      it('should return the new ticket in Discovery', async () => {
        expect(await driver().columnOfTicket('Search the catalog')).toEqual('Discovery')
      })

      it('should take the item off the Backlog', async () => {
        expect(await driver().isInBacklog('Search the catalog')).toEqual(false)
      })
    })

    describe('that holds a ticket moved back out of Discovery', () => {
      before(async () => {
        await driver().moveToBacklog('back-to-backlog')
        await driver().start('Back to backlog')
      })

      it('should bring the ticket back with its work', async () => {
        expect(await driver().stateOfWork('Back to backlog', 'stories-story-map')).toEqual('in_progress')
      })
    })
  })
})
