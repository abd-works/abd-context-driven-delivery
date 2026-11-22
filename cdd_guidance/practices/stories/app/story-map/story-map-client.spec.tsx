// The Story UI page over the story map tools: what it draws from the story map Python sends, and what it does when the
// cdd server does not answer. The story map tools themselves are specified against a real cdd server in
// cdd_guidance/practices/stories/model/story_map_edits_spec.py; here the page's server is the only seam, answered as
// the board's server answers.
// Stories: Refactor Story UI App To Web Domain Access; Open Story UI On Ticket Scope.
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { PROJECT_HEADER } from '@cdd/cdd-shared'
import type { StoryMapData } from '@cdd/practices/stories/model/story-map'

import { SERVER_DOWN, StoryMapApi, type Send } from './story-map-api'
import { StoryMapClient } from './story-map-client'
import { StoryMapFailures } from './story-map-failures'
import { StoryMapFailureView, StoryMapWorkspaceView } from './story-map-views'

const FILE = '.context/story-map.md'
const SUB_EPIC = `${FILE}#move-work-forward-from-chat-bar.integrate-practice-content-editor-apps-in-chat-bar`
const story = (slug: string, name: string) => ({ node: `${SUB_EPIC}.${slug}`, name, description: '', story_type: 'user', scenarios: [], acceptance_tests: [] })
const OPEN_STORY_UI = `${SUB_EPIC}.open-story-ui-side-panel-from-chat-bar`
const TRACE_STORY = `${SUB_EPIC}.trace-story-through-artifacts`
const INCREMENT = `${FILE}#increment:integrate-practice-content-editor-apps`

// The checkout-flow story map as the story map tools send it.
const CHECKOUT_FLOW: StoryMapData = {
  node: `${FILE}#`,
  name: 'StoryMap',
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
const WITH_EXAMPLES: StoryMapData = {
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

// The map the Story UI holds for state, answering nothing: its nodes as the page makes them.
const mapOf = (state: StoryMapData, send: Send = serverAnswering({}), posted?: Posted[]) => new StoryMapClient(new StoryMapApi(() => {}, posted ? serverAnswering({}, posted) : send), state)
const rowsOf = (client: StoryMapClient) => client.epicsOnPage[0]!.subEpics
const storyNamed = (client: StoryMapClient, name: string) => rowsOf(client).flatMap(row => row.stories).find(each => each.name === name)!

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
    expect(rowsOf(mapOf(CHECKOUT_FLOW)).map(sub => sub.name)).toEqual(['Integrate Practice Content Editor Apps In Chat Bar'])
  })

  it('should draw each story under its sub-epic, named by the node its tools take', () => {
    expect(rowsOf(mapOf(CHECKOUT_FLOW))[0]!.stories.map(each => each.id)).toEqual([`${SUB_EPIC}.open-story-ui-side-panel-from-chat-bar`, `${SUB_EPIC}.trace-story-through-artifacts`])
  })

  it('should make its nodes once from each answer, so reading them again draws the same nodes', () => {
    const client = mapOf(CHECKOUT_FLOW)
    expect(client.epicsOnPage).toBe(client.epicsOnPage)
  })
})

// The person's decisions of 2026-11-12: the story model's descriptions, increments and examples, and the ticket's scope.
describe('the story model the Story UI draws', () => {
  it("should draw each node's description as the story map says it", () => {
    expect(rowsOf(mapOf(CHECKOUT_FLOW))[0]!.description).toBe('Requested (2026-11-06): the chat bar opens the editor apps.')
  })

  it('should draw the increments the story model holds, each knowing the stories it delivers', () => {
    const client = mapOf(CHECKOUT_FLOW)
    const [increment] = client.incrementsOnPage
    expect([increment!.name, rowsOf(client)[0]!.stories.filter(story => increment!.delivers(story)).map(story => story.id)]).toEqual(['Integrate Practice Content Editor Apps', [OPEN_STORY_UI]])
  })

  it('should give each story the increment that delivers it', () => {
    const client = mapOf(CHECKOUT_FLOW)
    expect([storyNamed(client, 'Open Story UI Side Panel From Chat Bar').increment?.id, storyNamed(client, 'Trace Story Through Artifacts').increment]).toEqual([INCREMENT, undefined])
  })

  it("should draw a scenario's examples as the story model's one table, each row by the node its tools take", () => {
    const scenario = rowsOf(mapOf(WITH_EXAMPLES))[0]!.stories[0]!.scenarios[0]!
    expect([scenario.exampleColumns, scenario.examples.map(example => [example.id, example.fields])]).toEqual([['example', 'status'], [[EXAMPLE, { example: 'Story UI editor', status: 'running' }]]])
  })

  it("should draw only the stories the ticket's session names, scoped", () => {
    const scoped = mapOf({ ...CHECKOUT_FLOW, scope: [TRACE_STORY] }).epicsShown(true)
    expect(scoped.flatMap(epic => epic.subEpics.flatMap(sub => sub.stories.map(each => each.name)))).toEqual(['Trace Story Through Artifacts'])
  })

  it('should keep editing a scoped sub-epic through the sub-epic itself', () => {
    const scoped = mapOf({ ...CHECKOUT_FLOW, scope: [TRACE_STORY] }).epicsShown(true)
    expect(scoped[0]!.subEpics[0]!.id).toBe(SUB_EPIC)
  })

  it('should draw the whole map when the session names no story', () => {
    expect(mapOf(CHECKOUT_FLOW).epicsShown(true)[0]!.subEpics[0]!.stories.length).toBe(2)
  })
})

describe('an edit through the story map tools', () => {
  it("should change a story's description through its own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/edit-description': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await storyNamed(client, 'Trace Story Through Artifacts').describe('Requested: one trace view.')
    expect(posted).toEqual([{ path: `/api/story/${encodeURIComponent(TRACE_STORY)}/edit-description`, body: { description: 'Requested: one trace view.' } }])
  })

  it("should give a story to an increment through the increment's own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/add-story': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await client.incrementsOnPage[0]!.deliver(storyNamed(client, 'Trace Story Through Artifacts'))
    expect(posted).toEqual([{ path: `/api/increment/${encodeURIComponent(INCREMENT)}/add-story`, body: { story: TRACE_STORY } }])
  })

  it('should rename the story through its own tool', async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/rename': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await storyNamed(client, 'Trace Story Through Artifacts').rename('Trace Story Across Artifacts')
    expect(posted).toEqual([{ path: `/api/story/${encodeURIComponent(`${SUB_EPIC}.trace-story-through-artifacts`)}/rename`, body: { name: 'Trace Story Across Artifacts' } }])
  })

  it('should move a story dropped first before the story it was dropped on', async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/move-before': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    const [first, second] = [`${SUB_EPIC}.open-story-ui-side-panel-from-chat-bar`, `${SUB_EPIC}.trace-story-through-artifacts`]
    await client.reorder(rowsOf(client)[0]!.stories, [second, first])
    expect(posted.map(each => [each.path, each.body])).toEqual([[`/api/story/${encodeURIComponent(second)}/move-before`, { other: first }]])
  })

  it("should change a cell of an example's row through that example's own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/edit-field': WITH_EXAMPLES }, posted)), WITH_EXAMPLES)
    await rowsOf(client)[0]!.stories[0]!.scenarios[0]!.examples[0]!.editField('status', 'not running')
    expect(posted).toEqual([{ path: `/api/example/${encodeURIComponent(EXAMPLE)}/edit-field`, body: { field: 'status', text: 'not running' } }])
  })

  it("should remove an example through its own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/remove': WITH_EXAMPLES }, posted)), WITH_EXAMPLES)
    await rowsOf(client)[0]!.stories[0]!.scenarios[0]!.examples[0]!.remove()
    expect(posted).toEqual([{ path: `/api/example/${encodeURIComponent(EXAMPLE)}/remove`, body: {} }])
  })

  it("should change an epic's description through its own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/edit-description': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await rowsOf(client)[0]!.describe('Requested: the editor apps open from the chat bar.')
    expect(posted).toEqual([{ path: `/api/epic/${encodeURIComponent(SUB_EPIC)}/edit-description`, body: { description: 'Requested: the editor apps open from the chat bar.' } }])
  })

  it('should add a story before the story it is added ahead of, moving the new story there', async () => {
    const posted: Posted[] = []
    const added = `${SUB_EPIC}.new-story`
    const withNew: StoryMapData = { ...CHECKOUT_FLOW, epics: [{ ...CHECKOUT_FLOW.epics[0]!, epics: [{ ...CHECKOUT_FLOW.epics[0]!.epics[0]!, stories: [...CHECKOUT_FLOW.epics[0]!.epics[0]!.stories, story('new-story', 'New Story')] }] }] }
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/new-story': withNew, '/move-before': withNew }, posted)), CHECKOUT_FLOW)
    const row = rowsOf(client)[0]!
    await row.newStory('New Story', row.stories[1])
    expect(posted.map(each => [each.path, each.body])).toEqual([
      [`/api/epic/${encodeURIComponent(SUB_EPIC)}/new-story`, { name: 'New Story' }],
      [`/api/story/${encodeURIComponent(added)}/move-before`, { other: TRACE_STORY }],
    ])
  })

  it('should add a story last when it is added ahead of none', async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/new-story': CHECKOUT_FLOW }, posted)), CHECKOUT_FLOW)
    await rowsOf(client)[0]!.newStory('New Story')
    expect(posted.map(each => each.path)).toEqual([`/api/epic/${encodeURIComponent(SUB_EPIC)}/new-story`])
  })

  it("should write a new And step as a Then, through its scenario's own tool", async () => {
    const posted: Posted[] = []
    const client = new StoryMapClient(new StoryMapApi(() => {}, serverAnswering({ '/new-step': WITH_EXAMPLES }, posted)), WITH_EXAMPLES)
    await rowsOf(client)[0]!.stories[0]!.scenarios[0]!.newStep('and', 'the editor shows')
    expect(posted).toEqual([{ path: `/api/scenario/${encodeURIComponent(SCENARIO)}/new-step`, body: { step_type: 'then', text: 'the editor shows' } }])
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
    await new StoryMapApi(() => {}, send, 'C:/dev/checkout').post('/story-map/show', {})
    expect(headers[0]).toMatchObject({ [PROJECT_HEADER]: 'C:/dev/checkout' })
  })
})

// The api a page's failures tell its chat through, sending each call with send, else the page's fetch.
const apiSending = (send?: Send) => (notTold: (reason: string) => void) => new StoryMapApi(notTold, send)

// The Story UI page opened on story-map.md, its story expanded, with its server answering as the board's does.
async function openedPage(answers: Record<string, unknown>, chat: string, posted: Posted[] = []): Promise<Posted[]> {
  vi.stubGlobal('fetch', serverAnswering({ '/show': WITH_EXAMPLES, ...answers }, posted))
  render(<StoryMapWorkspaceView file={FILE} failures={new StoryMapFailures(chat, apiSending())} />)
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
    await waitFor(() => expect(posted.at(-1)).toEqual({ path: `/api/example/${encodeURIComponent(EXAMPLE)}/edit-field`, body: { field: 'status', text: 'not running' } }))
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
    await storyNamed(client, 'Trace Story Through Artifacts').rename('Trace Story Across Artifacts')
    expect(rowsOf(client)[0]!.stories[1]!.name).toBe('Trace Story Through Artifacts')
  })

  it('should show the page what failed, still showing the story as it was', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.stubGlobal('fetch', serverAnswering({ '/show': CHECKOUT_FLOW }))
    render(<StoryMapWorkspaceView file={FILE} failures={new StoryMapFailures('', apiSending())} />)
    await screen.findAllByText('Trace Story Through Artifacts')
    vi.stubGlobal('fetch', serverAnswering({}))
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2_000)
    })
    expect([screen.getByRole('alert').textContent, screen.getAllByText('Trace Story Through Artifacts').length > 0]).toEqual([`${SERVER_DOWN}Dismiss`, true])
    vi.useRealTimers()
  })
})

// Every failure the page meets goes to the chat that opened it, as the Files app sends its own.
describe('a failure on a Story UI page a chat opened', () => {
  const failuresSent = (posted: Posted[]) => posted.filter(post => post.path === `/api/chat/${CHAT}/send` && post.body.kind === 'failure').map(post => JSON.parse(String(post.body.text)))

  it('should send the failure and where it happened to that chat', async () => {
    const posted: Posted[] = []
    const failures = new StoryMapFailures(CHAT, apiSending(serverAnswering({ '/send': { id: CHAT, name: 'checkout-flow', is_busy: false, folder: '' } }, posted)))
    await new StoryMapApi(failures.fail, serverAnswering({})).post('/story/x/rename', { name: 'Trace' })
    await waitFor(() => expect(failuresSent(posted)).toEqual([{ failure: SERVER_DOWN, context: 'Calling /story/x/rename from the Story UI' }]))
  })

  it('should show the failure on the page', async () => {
    const failures = new StoryMapFailures(CHAT, apiSending(serverAnswering({ '/send': { id: CHAT, name: 'checkout-flow', is_busy: false, folder: '' } })))
    await new StoryMapApi(failures.fail, serverAnswering({})).post('/story/x/rename', { name: 'Trace' })
    expect(failures.shown).toBe(SERVER_DOWN)
  })

  describe('that the read every two seconds meets again', () => {
    it('should send the failure to the chat once', async () => {
      vi.useFakeTimers({ shouldAdvanceTime: true })
      const posted: Posted[] = []
      const failures = new StoryMapFailures(CHAT, apiSending(serverAnswering({ '/send': { id: CHAT, name: 'checkout-flow', is_busy: false, folder: '' } }, posted)))
      vi.stubGlobal('fetch', serverAnswering({ '/show': CHECKOUT_FLOW }))
      render(<StoryMapWorkspaceView file={FILE} failures={failures} />)
      await screen.findAllByText('Trace Story Through Artifacts')
      vi.stubGlobal('fetch', serverAnswering({}))
      await act(async () => {
        await vi.advanceTimersByTimeAsync(6_000)
      })
      expect(failuresSent(posted)).toHaveLength(1)
      vi.useRealTimers()
    })
  })

  describe('with a view that throws', () => {
    it('should send what the view threw to that chat', async () => {
      const posted: Posted[] = []
      const failures = new StoryMapFailures(CHAT, apiSending(serverAnswering({ '/send': { id: CHAT, name: 'checkout-flow', is_busy: false, folder: '' } }, posted)))
      const Broken = (): React.ReactNode => {
        throw new Error('a view broke')
      }
      vi.spyOn(console, 'error').mockImplementation(() => {})
      render(<StoryMapFailureView failures={failures}><Broken /></StoryMapFailureView>)
      await waitFor(() => expect(failuresSent(posted).map(sent => sent.failure)).toEqual(['a view broke']))
    })
  })
})
