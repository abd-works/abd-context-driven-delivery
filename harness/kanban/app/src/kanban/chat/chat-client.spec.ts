import { describe, expect, it } from 'vitest'

import { boardJson, discovery } from 'test-utils/board-examples'
import { pageOn, withChat } from 'test-utils/board-page-support'

describe('Send commands to a chat', () => {
  it('should choose the only chat connected', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('GET /api/chats', [{ id: 'chat-1', name: '', isBusy: false }])
    await page.chat.refresh()
    expect(page.store.state.targetChat).toBe('chat-1')
  })

  it('should choose none among several', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('GET /api/chats', [
      { id: 'chat-1', name: '', isBusy: false },
      { id: 'chat-2', name: '', isBusy: false },
    ])
    await page.chat.refresh()
    expect(page.chat.canSend).toBe(false)
  })

  it('should send once a person picks one of several', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('GET /api/chats', [
      { id: 'chat-1', name: '', isBusy: false },
      { id: 'chat-2', name: '', isBusy: false },
    ])
    await page.chat.refresh()
    page.chat.choose('chat-2')
    expect(page.chat.canSend).toBe(true)
  })

  it('should keep a picked chat while it stays connected', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('GET /api/chats', [
      { id: 'chat-1', name: '', isBusy: false },
      { id: 'chat-2', name: '', isBusy: true },
    ])
    page.chat.choose('chat-2')
    await page.chat.refresh()
    expect(page.store.state.targetChat).toBe('chat-2')
  })

  it('should let go of a chat that has gone', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    server.answer('GET /api/chats', [])
    page.chat.choose('chat-2')
    await page.chat.refresh()
    expect(page.chat.canSend).toBe(false)
  })

  it('should send nothing with no chat chosen', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    await page.chat.command('/actions-validate a')
    expect(server.requests).toEqual([])
  })

  it('should send a skill as a command', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    withChat(page, server)
    await page.chat.command('/actions-validate a')
    expect(server.posted('/api/chats/chat-1/commands')[0]?.body).toEqual({ kind: 'command', text: '/actions-validate a' })
  })

  it('should tell the person a fill is queued for review', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    withChat(page, server)
    await page.chat.fill('Split this')
    expect(page.store.state.toasts[0]?.text).toBe('Queued for the prompt, for you to review: Split this')
  })

  it('should say a fill waits for the turn to end while the chat is busy', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    withChat(page, server, { id: 'chat-1', name: '', isBusy: true })
    await page.chat.fill('Split this')
    expect(page.store.state.toasts[0]?.text).toContain('It goes in when this turn ends.')
  })

  it('should show the refusal of a chat that has gone', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    withChat(page, server)
    server.answer('POST /api/chats/chat-1/commands', { error: 'That chat is not connected: is the cdd-board mod loaded in it?' }, 409)
    await page.chat.command('/actions-validate a')
    expect(page.store.state.toasts).toMatchObject([{ text: 'That chat is not connected: is the cdd-board mod loaded in it?', isFailure: true }])
  })
})
