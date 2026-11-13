// The Story UI page over the story map tools: what it draws from the story map Python sends, and what it does when the
// cdd server does not answer. The story map tools themselves are specified against a real cdd server in
// cdd_guidance/practices/stories/model/story_map_edits_spec.py; here the page's server is the only seam, answered as
// the board's server answers.
// Story: Refactor Story UI App To Web Domain Access.
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { PROJECT_HEADER } from '@cdd/cdd-shared'
import type { StoryModelData } from '@cdd/practices/stories/model/story-model'

import { SERVER_DOWN, StoryMapApi } from './story-map-api'
import { StoryMapClient } from './story-map-client'
import { StoryMapViewModel } from './story-map-view-models'
import { StoryMapWorkspaceView } from './story-map-views'

const FILE = '.context/story-map.md'
const SUB_EPIC = `${FILE}#move-work-forward-from-chat-bar.integrate-practice-content-editor-apps-in-chat-bar`
const story = (slug: string, name: string) => ({ node: `${SUB_EPIC}.${slug}`, name, story_type: 'user', scenarios: [] })

// The checkout-flow story map as the story map tools send it.
const CHECKOUT_FLOW: StoryModelData = {
  node: `${FILE}#`,
  name: 'StoryModel',
  file: FILE,
  refusal: '',
  formats: { session_file: '.sessions/checkout-flow/session.json', practice_name: 'stories', name: 'story_map', offered_formats: ['markdown', 'drawio'], chosen_formats: ['markdown', 'drawio'] },
  epics: [
    {
      node: `${FILE}#move-work-forward-from-chat-bar`,
      name: 'Move Work Forward From Chat Bar',
      stories: [],
      epics: [
        {
          node: SUB_EPIC,
          name: 'Integrate Practice Content Editor Apps In Chat Bar',
          epics: [],
          stories: [story('open-story-ui-side-panel-from-chat-bar', 'Open Story UI Side Panel From Chat Bar'), story('trace-story-through-artifacts', 'Trace Story Through Artifacts')],
        },
      ],
    },
  ],
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

describe('an edit through the story map tools', () => {
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
