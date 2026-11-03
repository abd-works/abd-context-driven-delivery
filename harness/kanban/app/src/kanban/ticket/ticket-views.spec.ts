import { createElement } from 'react'
import { renderToString } from 'react-dom/server'
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import { TicketClientGenerated } from '@cdd/harness/kanban/ticket'
import { TicketViewGenerated } from '@cdd/harness/kanban/ticket-views'
import { ticketJson } from 'test-utils/board-examples'

const answering = (answer: unknown): CddApi => ({ post: <Result>() => Promise.resolve(answer as Result) })
const NO_ANSWER = answering(null)

const drawn = (client: TicketClientGenerated, fields = {}): string => renderToString(createElement(TicketViewGenerated, { client, fields }))

describe('a generated ticket view', () => {
  const ticket = new TicketClientGenerated(NO_ANSWER, ticketJson('sign-up', { title: 'Sign up', column: 'Discovery' }))

  it('should show a field no operation changes as read-only', () => {
    expect(drawn(ticket)).toContain('<span class="cdd-field-value">Discovery</span>')
  })

  it('should offer an operation with no arguments as a button', () => {
    expect(drawn(ticket)).toContain('>Move next</button>')
  })

  it('should give an operation with arguments a form for them', () => {
    expect(drawn(ticket)).toContain('Stage')
  })

  describe('with a field the page draws itself', () => {
    it('should draw the page’s own field in its place', () => {
      expect(drawn(ticket, { title: () => createElement('h1', null, 'Sign up, the page’s way') })).toContain('<h1>Sign up, the page’s way</h1>')
    })
  })
})

describe('a generated ticket client', () => {
  describe('that an operation has answered with new state', () => {
    it('should tell what is drawing it to draw again', async () => {
      const ticket = new TicketClientGenerated(answering(ticketJson('sign-up', { column: 'Specification' })), ticketJson('sign-up'))
      let draws = 0
      ticket.onChanged(() => draws++)
      await ticket.moveNext()
      expect(draws).toBe(1)
    })
  })

  describe('that the page has stopped listening to', () => {
    it('should not tell it again', async () => {
      const ticket = new TicketClientGenerated(answering(ticketJson('sign-up')), ticketJson('sign-up'))
      let draws = 0
      const stop = ticket.onChanged(() => draws++)
      stop()
      await ticket.moveNext()
      expect(draws).toBe(0)
    })
  })
})
