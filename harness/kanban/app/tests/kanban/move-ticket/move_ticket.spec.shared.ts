/**
 * States each behavior of Move Ticket once. Reaches the tier only through its driver, so every tier runs these same
 * signatures. The sentences match kanban_tools_spec.py.
 */
import { shareBehavior } from 'test-utils/behavior-test/behavior-test'

export type TicketPlace = { column: string; isDone: boolean }

export type MoveTicketDriver = {
  moveNext: (ticket: string) => Promise<void>
  movePrevious: (ticket: string) => Promise<void>
  dragTo: (ticket: string, stage: string, done: boolean) => Promise<void>
  placeOf: (ticket: string) => Promise<TicketPlace>
  isOnTheStages: (ticket: string) => Promise<boolean>
  backlogTitles: () => Promise<string[]>
}

export const moveTicketBehavior = shareBehavior<MoveTicketDriver>(({ describe, it, before, expect, driver }) => {
  describe('a ticket', () => {
    describe('that a person has moved to the next column', () => {
      before(() => driver().moveNext('ready-to-move'))

      it('should show the ticket in the next stage', async () => {
        expect((await driver().placeOf('ready-to-move')).column).toEqual('Specification')
      })

      it('should show the ticket in progress there', async () => {
        expect((await driver().placeOf('ready-to-move')).isDone).toEqual(false)
      })
    })

    describe("with that stage's work not done", () => {
      before(() => driver().moveNext('move-me'))

      it("should show the ticket in that stage's Done all the same", async () => {
        expect(await driver().placeOf('move-me')).toEqual({ column: 'Discovery', isDone: true })
      })

      describe('and back from Done', () => {
        before(() => driver().movePrevious('move-me'))

        it('should show the ticket in progress in that stage', async () => {
          expect(await driver().placeOf('move-me')).toEqual({ column: 'Discovery', isDone: false })
        })
      })
    })

    describe("that a person has dragged into a later stage's Done", () => {
      before(() => driver().dragTo('move-me', 'Implementation', true))

      it("should show the ticket in that stage's Done", async () => {
        expect(await driver().placeOf('move-me')).toEqual({ column: 'Implementation', isDone: true })
      })
    })

    describe('that a person has moved back to the previous column', () => {
      before(() => driver().movePrevious('pricing-rules'))

      it('should show the ticket in Discovery', async () => {
        expect((await driver().placeOf('pricing-rules')).column).toEqual('Discovery')
      })

      it("should show the ticket in Discovery's Done", async () => {
        expect((await driver().placeOf('pricing-rules')).isDone).toEqual(true)
      })
    })

    describe('that a person has moved back out of Discovery', () => {
      before(() => driver().movePrevious('back-to-backlog'))

      it("should show an item in the Backlog with the ticket's title", async () => {
        expect(await driver().backlogTitles()).toContain('Back to backlog')
      })

      it("should take the ticket off the board's stages", async () => {
        expect(await driver().isOnTheStages('back-to-backlog')).toEqual(false)
      })
    })

    describe('that a person has moved past Implementation', () => {
      before(() => driver().moveNext('almost-shipped'))

      it('should close the ticket', async () => {
        expect((await driver().placeOf('almost-shipped')).column).toEqual('Complete')
      })

      describe('and back again', () => {
        before(() => driver().movePrevious('almost-shipped'))

        it('should reopen the ticket in Implementation', async () => {
          expect((await driver().placeOf('almost-shipped')).column).toEqual('Implementation')
        })
      })
    })
  })
})
