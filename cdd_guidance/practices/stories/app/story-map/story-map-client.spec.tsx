// The Story UI page over the story map tools: what it draws from the story map Python sends, and what it does when the
// cdd server does not answer. The story map tools themselves are specified against a real cdd server in
// cdd_guidance/practices/stories/model/story_map_edits_spec.py; here the page's server is the only seam, answered as
// the board's server answers.
// Stories: Refactor Story UI App To Web Domain Access; Open Story UI On Ticket Scope.
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { PROJECT_HEADER } from '@cdd/cdd-shared'
import type { StoryModelData } from '@cdd/practices/stories/model/story-model'

import { SERVER_DOWN, StoryMapApi } from './story-map-api'
import { StoryMapClient } from './story-map-client'
import { StoryMapViewModel } from './story-map-view-models'
import { StoryMapWorkspaceView } from './story-map-views'

const FILE = '.context/story-map.md'
const SUB_EPIC = `${FILE}#move-work-forward-from-chat-bar.integrate-practice-content-editor-apps-in-chat-bar`
const story = (slug: string, name: string) => ({ node: `${SUB_EPIC}.${slug}`, name, description: '', story_type: 'user', scenarios: [], acceptance_tests: [] })
const OPEN_STORY_UI = `${SUB_EPIC}.open-story-ui-side-panel-from-chat-bar`
const TRACE_STORY = `${SUB_EPIC}.trace-story-through-artifacts`
const INCREMENT = `${FILE}#increment:integrate-practice-content-editor-apps`

// The checkout-flow story map as the story map tools send it.
const CHECKOUT_FLOW: StoryModelData = {
  node: `${FILE}#`,
  name: 'StoryModel',
  description: '',
  file: FILE,
  refusal: '',
  scope: [],
  increments: [{ node: INCREMENT, name: 'Integrate Practice Content Editor Apps', description: '**Outcome:** the editor apps open on the ticket.', stories: [OPEN_STORY_UI] }],
  formats: { session_file: '.sessions/checkout-flow/session.json', practice_name: 'stories', name: 'story_map', offered_formats: ['markdown', 'drawio'], chosen_formats: ['markdown', 'drawio'] },
  epics: [
    {
      node: `${FILE}#move-work-forward-from-chat-bar`,
      name: 'Move Work Forward From Chat Bar',
      description: '',
      stories: [],
      epics: [
        {
          node: SUB_EPIC,
          name: 'Integrate Practice Content Editor Apps In Chat Bar',
          description: 'Requested (2026-11-06): the chat bar opens the editor apps.',
          epics: [],
          stories: [story('open-story-ui-side-panel-from-chat-bar', 'Open Story UI Side Panel From Chat Bar'), story('trace-story-through-artifacts', 'Trace Story Through Artifacts')],
        },
      ],
    },
  ],
}

const SCENARIO = `${OPEN_STORY_UI}.a-press-opens-the-editor`
const EXAMPLE = `${SCENARIO}.example:story-ui-editor`
const STORY_TEST = 'move-work-forward-from-chat-bar/open_story_ui_side_panel_from_chat_bar_story.test.py'
const CHAT = 'ad6c04ab-chat'
// The checkout-flow story map with a scenario of the Story UI story, its examples, and an acceptance-test file.
const WITH_EXAMPLES: StoryModelData = {
  ...CHECKOUT_FLOW,
  epics: [{
    ...CHECKOUT_FLOW.epics[0]!,
    epics: [{
      ...CHECKOUT_FLOW.epics[0]!.epics[0]!,
      stories: [{
        ...story('open-story-ui-side-panel-from-chat-bar', 'Open Story UI Side Panel From Chat Bar'),
        acceptance_tests: [STORY_TEST],
        scenarios: [{ node: SCENARIO, name: 'A press opens the editor', description: '', steps: [], examples: [{ node: EXAMPLE, name: 'Story UI editor', description: '', fields: { example: 'Story UI editor', status: 'running' } }] }],
      }],
    }],
  }],
}

type Posted = { path: string; body: Record<string, unknown> }

// The board's server as the page reaches it: it answers each path from answers, and refuses the rest as down.
function serverAnswering(answers: Record<string, unknown>, posted: Posted[] = []) {
  return async (path: string, init: RequestInit): Promise<Response> => {
    posted.push({ path, body: JSON.parse(String(init.body)) })
    const tool = Object.keys(answers).find(each => path.endsWith(each))
    if (!tool) throw new TypeError('fetch failed')
    return new Response(JSON.stringify(answers[tool]), { status: 200, headers: { 'content-type': 'application/json' } })
  }
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('the story map the Story UI draws', () => {
  it('should draw each sub-epic under its epic', () => {
    const map = StoryMapViewModel.of(CHECKOUT_FLOW)
    expect(map.epics[0]!.sub_epics.map(sub => sub.name)).toEqual(['Integrate Practice Content Editor Apps In Chat Bar'])
  })

  it('should draw each story under its sub-epic, named by the node its tools take', () => {
    const map = StoryMapViewModel.of(CHECKOUT_FLOW)
    expect(map.epics[0]!.sub_epics[0]!.stories.map(each => each.id)).toEqual([`${SUB_EPIC}.open-story-ui-side-panel-from-chat-bar`, `${SUB_EPIC}.trace-story-through-artifacts`])
  })
})

// The person's decisions of 2026-11-12: the story model's descriptions, increments and examples, and the ticket's scope.
describe('the story model the Story UI draws', () => {
  it("should draw each node's description as the story map says it", () => {
    expect(StoryMapViewModel.of(CHECKOUT_FLOW).epics[0]!.sub_epics[0]!.description).toBe('Requested (2026-11-06): the chat bar opens the editor apps.')
  })

  it('should draw the increments the story model holds, with the stories each delivers', () => {
    expect(StoryMapViewModel.of(CHECKOUT_FLOW).increments.map(each => [each.name, each.stories])).toEqual([['Integrate Practice Content Editor Apps', [OPEN_STORY_UI]]])
  })

  it("should draw a scenario's examples as the story model's one table, each row by the node its tools take", () => {
    expect(StoryMapViewModel.of(WITH_EXAMPLES).epics[0]!.sub_epics[0]!.stories[0]!.scenarios[0]!.examples).toEqual({ columns: ['example', 'status'], rows: [{ id: EXAMPLE, fields: { example: 'Story UI editor', status: 'running' } }] })
  })

  it("should draw only the stories the ticket's session names, scoped", () => {
    const scoped = StoryMapViewModel.of({ ...CHECKOUT_FLOW, scope: [TRACE_STORY] }, true)
    expect(scoped.epics.flatMap(epic => epic.sub_epics.flatMap(sub => sub.stories.map(each => each.name)))).toEqual(['Trace Story Through Artifacts'])
  })

  it('should draw the whole map when the session names no story', () => {
    const scoped = StoryMapViewModel.of(CHECKOUT_FLOW, true)
    expect(scoped.epics[0]!.sub_epics[0]!.stories.length).toBe(2)
  })
})

describe('an edit through the story map tools', () => {
  it("should change a story's description through its own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/edit-description': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await client.describeNode(TRACE_STORY, 'story', 'Requested: one trace view.')
    expect(posted).toEqual([{ path: `/api/story/${encodeURIComponent(TRACE_STORY)}/edit-description`, body: { description: 'Requested: one trace view.' } }])
  })

  it("should give a story to an increment through the increment's own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/add-story': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await client.deliverIn(INCREMENT, TRACE_STORY)
    expect(posted).toEqual([{ path: `/api/increment/${encodeURIComponent(INCREMENT)}/add-story`, body: { story: TRACE_STORY } }])
  })

  it('should rename the story through its own tool', async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/rename': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await client.renameNode(`${SUB_EPIC}.trace-story-through-artifacts`, 'story', 'Trace Story Across Artifacts')
    expect(posted).toEqual([{ path: `/api/story/${encodeURIComponent(`${SUB_EPIC}.trace-story-through-artifacts`)}/rename`, body: { name: 'Trace Story Across Artifacts' } }])
  })

  it('should move a story dropped first before the story it was dropped on', async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/move-before': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    const [first, second] = [`${SUB_EPIC}.open-story-ui-side-panel-from-chat-bar`, `${SUB_EPIC}.trace-story-through-artifacts`]
    await client.reorder([first, second], [second, first], 'story')
    expect(posted.map(each => [each.path, each.body])).toEqual([[`/api/story/${encodeURIComponent(second)}/move-before`, { other: first }]])
  })

  it("should change a cell of an example's row through that example's own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/edit-field': WITH_EXAMPLES }, posted)), WITH_EXAMPLES)
    await client.editExample(EXAMPLE, 'status', 'not running')
    expect(posted).toEqual([{ path: `/api/example/${encodeURIComponent(EXAMPLE)}/edit-field`, body: { field: 'status', value: 'not running' } }])
  })

  it("should remove an example through its own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/remove': WITH_EXAMPLES }, posted)), WITH_EXAMPLES)
    await client.removeExample(EXAMPLE)
    expect(posted).toEqual([{ path: `/api/example/${encodeURIComponent(EXAMPLE)}/remove`, body: {} }])
  })

  it("should change an epic's description through its own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/edit-description': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await client.describeNode(SUB_EPIC, 'sub-epic', 'Requested: the editor apps open from the chat bar.')
    expect(posted).toEqual([{ path: `/api/epic/${encodeURIComponent(SUB_EPIC)}/edit-description`, body: { description: 'Requested: the editor apps open from the chat bar.' } }])
  })

  it('should turn a format off for the fidelity in the session', async () => {
    const posted: Posted[] = []
    const answers = { '/choose-format': CHECKOUT_FLOW.formats, '/show': CHECKOUT_FLOW }
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering(answers, posted)), CHECKOUT_FLOW)
    await client.chooseFormat('drawio', false)
    expect(posted[0]!.body).toEqual({ format: 'drawio', is_chosen: false })
  })
})

// An edit with the cdd server down says so and is not shown as saved.
describe('a Story UI opened on a repository', () => {
  it("should name the repository its page link names on every call, so the board's server answers from that repository", async () => {
    const headers: HeadersInit[] = []
    const send = async (_path: string, init: RequestInit): Promise<Response> => {
      headers.push(init.headers ?? {})
      return new Response(JSON.stringify(CHECKOUT_FLOW), { status: 200 })
    }
    await new StoryMapApi(() => {}, send, 'C:/dev/checkout').post('/story-model/show', {})
    expect(headers[0]).toMatchObject({ [PROJECT_HEADER]: 'C:/dev/checkout' })
  })
})

// The Story UI page opened on story-map.md, its story expanded, with its server answering as the board's does.
async function openedPage(answers: Record<string, unknown>, chat: string, posted: Posted[] = []): Promise<Posted[]> {
  vi.stubGlobal('fetch', serverAnswering({ '/show': WITH_EXAMPLES, ...answers }, posted))
  render(<StoryMapWorkspaceView file={FILE} chat={chat} />)
  fireEvent.click((await screen.findAllByText('Open Story UI Side Panel From Chat Bar'))[0]!.closest('.story-card-header')!)
  return posted
}

// (S) Refactor Story UI App To Web Domain Access: a story's acceptance tests are links that open in the chat bar's file
// viewer, not in the Story UI.
describe("a story's acceptance-test link", () => {
  it("should send the file to the file viewer of the chat the page was opened beside", async () => {
    const posted = await openedPage({ '/send': { id: CHAT, name: 'checkout-flow', is_busy: false, folder: '' } }, CHAT)
    fireEvent.click(screen.getByRole('button', { name: STORY_TEST }))
    await waitFor(() => expect(posted.at(-1)).toEqual({ path: `/api/chat/${CHAT}/send`, body: { kind: 'open_file', text: STORY_TEST } }))
  })

  it('should open nothing in the Story UI itself', async () => {
    await openedPage({ '/send': { id: CHAT, name: 'checkout-flow', is_busy: false, folder: '' } }, CHAT)
    fireEvent.click(screen.getByRole('button', { name: STORY_TEST }))
    expect(screen.queryByRole('complementary')).toBeNull()
  })

  it('should say where to read the file on a page no chat opened', async () => {
    await openedPage({}, '')
    expect([screen.queryByRole('button', { name: STORY_TEST }), screen.getByRole('note').textContent]).toEqual([null, expect.stringContaining("chat's file viewer")])
  })
})

// (S) Refactor Story UI App To Web Domain Access: a scenario's example rows are edited through each example's tools.
describe("a scenario's example row on the page", () => {
  it("should save a changed cell through that example's edit_field", async () => {
    const posted = await openedPage({ '/edit-field': WITH_EXAMPLES }, CHAT)
    const cell = screen.getByRole('textbox', { name: 'status of Story UI editor' })
    fireEvent.change(cell, { target: { value: 'not running' } })
    fireEvent.blur(cell)
    await waitFor(() => expect(posted.at(-1)).toEqual({ path: `/api/example/${encodeURIComponent(EXAMPLE)}/edit-field`, body: { field: 'status', value: 'not running' } }))
  })
})

// (S) Refactor Story UI App To Web Domain Access: an epic's and a sub-epic's descriptions are edited on screen.
describe("an epic's description on the page", () => {
  it("should save a changed description through the sub-epic's own tool", async () => {
    const posted = await openedPage({ '/edit-description': WITH_EXAMPLES }, CHAT)
    fireEvent.click(screen.getAllByText('SUB-EPIC')[0]!)
    const description = screen.getByRole('textbox', { name: 'Description of Integrate Practice Content Editor Apps In Chat Bar' })
    fireEvent.change(description, { target: { value: 'Requested: the editor apps open from the chat bar.' } })
    fireEvent.blur(description)
    await waitFor(() => expect(posted.at(-1)).toEqual({ path: `/api/epic/${encodeURIComponent(SUB_EPIC)}/edit-description`, body: { description: 'Requested: the editor apps open from the chat bar.' } }))
  })

  it("should show the epic's description once the epic is opened", async () => {
    await openedPage({}, CHAT)
    fireEvent.click(screen.getAllByText('EPIC')[0]!)
    expect(screen.getByRole('textbox', { name: 'Description of Move Work Forward From Chat Bar' })).toBeTruthy()
  })
})

describe('with the cdd server not answering', () => {
  it('should say the cdd server is not answering and how to start it', async () => {
    const failures: string[] = []
    await new StoryMapApi(message => failures.push(message), serverAnswering({})).post('/story/x/rename', { name: 'Trace' })
    expect(failures).toEqual([SERVER_DOWN])
  })

  it('should keep the story map as Python last sent it', async () => {
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({})), CHECKOUT_FLOW)
    await client.renameNode(`${SUB_EPIC}.trace-story-through-artifacts`, 'story', 'Trace Story Across Artifacts')
    expect(StoryMapViewModel.of(client.toJSON()).epics[0]!.sub_epics[0]!.stories[1]!.name).toBe('Trace Story Through Artifacts')
  })

  it('should show the page what failed, still showing the story as it was', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.stubGlobal('fetch', serverAnswering({ '/show': CHECKOUT_FLOW }))
    render(<StoryMapWorkspaceView file={FILE} />)
    await screen.findAllByText('Trace Story Through Artifacts')
    vi.stubGlobal('fetch', serverAnswering({}))
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2_000)
    })
    expect([screen.getByRole('alert').textContent, screen.getAllByText('Trace Story Through Artifacts').length > 0]).toEqual([`${SERVER_DOWN}Dismiss`, true])
    vi.useRealTimers()
  })
})
