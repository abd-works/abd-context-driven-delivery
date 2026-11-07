import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Send commands to a chat', () => {
  it('should choose the only chat connected', async () => {
    const { page } = await board.page()
    await board.chat('chat-1').checkIn()
    await page.chat.refresh()
    expect(page.store.state.targetChat).toBe('chat-1')
  })

  // Every button that sends to a chat is off with none chosen, so the board chooses one and the picker shows which.
  it('should choose the first of several when none has been picked', async () => {
    const { page } = await board.page()
    await board.chat('chat-1').checkIn()
    await board.chat('chat-2').checkIn()
    await page.chat.refresh()
    expect(page.store.state.targetChat).toBe('chat-1')
  })

  it('should choose again the chat a person picked once it is back', async () => {
    const { page } = await board.page()
    page.chat.choose('chat-2')
    await page.chat.refresh()
    await board.chat('chat-1').checkIn()
    await board.chat('chat-2').checkIn()
    await page.chat.refresh()
    expect(page.store.state.targetChat).toBe('chat-2')
  })

  it('should send once a person picks one of several', async () => {
    const { page } = await board.page()
    await board.chat('chat-1').checkIn()
    await board.chat('chat-2').checkIn()
    await page.chat.refresh()
    page.chat.choose('chat-2')
    expect(page.chat.canSend).toBe(true)
  })

  it('should keep a picked chat while it stays connected', async () => {
    const { page } = await board.page()
    await board.chat('chat-1').checkIn()
    await board.chat('chat-2').checkIn(true)
    page.chat.choose('chat-2')
    await page.chat.refresh()
    expect(page.store.state.targetChat).toBe('chat-2')
  })

  it('should let go of a chat that has gone', async () => {
    const { page } = await board.page()
    page.chat.choose('chat-2')
    await page.chat.refresh()
    expect(page.chat.canSend).toBe(false)
  })

  it('should send nothing with no chat chosen', async () => {
    const { page, asked } = await board.page()
    await page.chat.command('/actions-validate a')
    expect(asked).toEqual([])
  })

  it('should send a skill as a command', async () => {
    const { page } = await board.page()
    const chat = await board.connectChat(page)
    await page.chat.command('/actions-validate a')
    expect(await chat.checkIn()).toEqual([{ kind: 'command', text: '/actions-validate a' }])
  })

  // The person can only see what ran when the board names the whole command and the chat it went to.
  it('should name the chat a command went to and the whole command', async () => {
    const { page } = await board.page()
    await board.chat('chat-2', 'repo · fix the board').checkIn()
    await page.chat.refresh()
    page.chat.choose('chat-2')
    await page.chat.command('/actions-validate stories-story-map session=.sessions/checkout-flow/session.json')
    expect(page.store.state.toasts[0]?.text).toBe('Sent to repo · fix the board: /actions-validate stories-story-map session=.sessions/checkout-flow/session.json')
  })

  describe("with the chat's messages", () => {
    async function sent() {
      const { page } = await board.page()
      const chat = await board.connectChat(page)
      await page.chat.command('/actions-validate a')
      await page.chat.fill('Split this')
      return { page, chat }
    }

    it('should show them, the latest first', async () => {
      const { page } = await sent()
      expect(page.store.state.messages.map(message => message.text)).toEqual(['Split this', '/actions-validate a'])
    })

    it('should show a message as waiting until the chat takes it', async () => {
      const { page } = await sent()
      expect(page.store.state.messages.map(message => message.state)).toEqual(['waiting', 'waiting'])
    })

    it('should show a message as taken, not yet shown, once the chat has taken it', async () => {
      const { page, chat } = await sent()
      await chat.checkIn()
      await page.chat.refresh()
      expect(page.store.state.messages.map(message => message.state)).toEqual(['taken', 'taken'])
    })

    it('should say why the chat could not show a message', async () => {
      const { page, chat } = await sent()
      await chat.refuseNext('the chat dropped it: a Stop stands')
      await page.chat.refresh()
      expect(page.store.state.messages.find(message => message.state === 'failed')?.reason).toBe('the chat dropped it: a Stop stands')
    })

    it('should show a message as done once the chat has finished working on it', async () => {
      const { page, chat } = await sent()
      await chat.finishNext()
      await page.chat.refresh()
      expect(page.store.state.messages.find(message => message.text === '/actions-validate a')?.state).toBe('done')
    })

    it('should put a message the chat did not show back in its queue when a person resends it', async () => {
      const { page, chat } = await sent()
      await chat.refuseNext('the chat dropped it')
      await page.chat.refresh()
      const failed = page.store.state.messages.find(message => message.state === 'failed')!
      await page.chat.resend(failed.message)
      expect(page.store.state.messages.find(message => message.message === failed.message)?.state).toBe('waiting')
    })

    it('should no longer show a message a person removes', async () => {
      const { page } = await sent()
      await page.chat.remove(page.store.state.messages[0]!.message)
      expect(page.store.state.messages.map(message => message.text)).toEqual(['/actions-validate a'])
    })
  })

  it('should tell the person a fill is queued for review', async () => {
    const { page } = await board.page()
    await board.connectChat(page)
    await page.chat.fill('Split this')
    expect(page.store.state.toasts[0]?.text).toBe('Queued for the prompt of chat-1, for you to review: Split this')
  })

  it('should say a fill waits for the turn to end while the chat is busy', async () => {
    const { page } = await board.page()
    await board.connectChat(page, 'chat-1', true)
    await page.chat.fill('Split this')
    expect(page.store.state.toasts[0]?.text).toContain('It goes in when this turn ends.')
  })

  it('should show the refusal of a chat that has gone', async () => {
    const { page } = await board.page()
    await board.connectChat(page)
    board.forgetChat('chat-1')
    await page.chat.command('/actions-validate a')
    expect(page.store.state.toasts).toMatchObject([
      { text: "cdd chat.send failed: ChatNotConnectedError: chat 'chat-1' is not connected: is the cdd-board mod loaded in it?", isFailure: true },
    ])
  })
})
