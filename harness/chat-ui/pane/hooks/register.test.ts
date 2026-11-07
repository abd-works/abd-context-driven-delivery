import { expect, test } from 'claude-code/testing'

// Organised by story. A test whose name starts `should` has the same signature as a Mamba example in
// harness/diagnostics/server_health_spec.py; the others cover what a person sees and presses on the band.
const BAND = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  surface: 'desktop',
  props: { hasSurvey: false, isWorking: false, maxRows: 12, bodyColumns: 120, scroll: { offset: 0, bodyRows: 12 }, view: {} },
} as const

const HEALTHY = { kanban_app_port: 8778, graph_app_port: 5173, is_hook_server_running: false }
const CDD_TOOLS = Array.from({ length: 116 }, (_, index) => ({ name: `mcp__plugin_cdd_cdd__tool_${index}`, description: '', mcp: true }))

type Engine = { serverLost: boolean; report: unknown; rawText: string | null; calls: string[] }

const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false } })

// Stands in for the engine and the cdd server beneath the plugin.
const engine = (on: any): Engine => {
  const stub: Engine = { serverLost: false, report: HEALTHY, rawText: null, calls: [] }
  on('command.register', () => ({ value: undefined }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('clock.every', () => ({ value: () => undefined }))
  // A timer that never comes due: a test ends before one would fire.
  on('clock.after', () => new Promise(() => undefined))
  on('tool.list', () => ({ value: CDD_TOOLS }))
  on('mcp.call', (_: unknown, e: { tool: string }) => {
    stub.calls.push(e.tool)
    if (stub.serverLost) throw new Error('no connected MCP tool on a server named "plugin:cdd:cdd"')
    if (e.tool !== 'server-health.report') return { value: { content: [], isError: true } }
    if (stub.rawText !== null) return { value: { content: [{ type: 'text', text: stub.rawText }], isError: false } }
    return answer(stub.report)
  })
  on('prompt.submit', (_: unknown, e: { text: string }) => ({ text: e.text }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  return stub
}

const mountBand = async ($: any) => {
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.prompt.submit({ text: 'look' })
  return $.ui.mount(BAND)
}

const pinnedBand = async ($: any) => {
  const ui = await mountBand($)
  await ui.press({ key: 'health-icon' })
  return ui
}

const expandedOf = async (ui: any) => (await ui.find({ key: 'session-card' }))?.children?.[0]

const findText = (ui: any, text: RegExp | string) => ui.find({ type: 'Text', text })

// (E) Server Health Band

test('should report the port the Kanban app answers on', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  expect((await findText(ui, 'running :8778'))?.text).toBe('running :8778')
  await ui.unmount()
})

test('should report no Kanban app port', async ($, on) => {
  const stub = engine(on)
  stub.report = { ...HEALTHY, kanban_app_port: null, graph_app_port: 5173 }
  const ui = await pinnedBand($)

  expect((await findText(ui, 'not running'))?.text).toBe('not running')
  await ui.unmount()
})

test('should report the port the graph app answers on', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  expect((await findText(ui, 'running :5173'))?.text).toBe('running :5173')
  await ui.unmount()
})

test('should report no graph app port', async ($, on) => {
  const stub = engine(on)
  stub.report = { ...HEALTHY, graph_app_port: null }
  const ui = await pinnedBand($)

  expect((await findText(ui, 'not running'))?.text).toBe('not running')
  await ui.unmount()
})

test('should report the hook server is not running', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  expect((await findText(ui, 'not installed'))?.text).toBe('not installed')
  await ui.unmount()
})

test('connected draws one check mark until it is pinned', async ($, on) => {
  engine(on)
  const ui = await mountBand($)

  expect((await expandedOf(ui))?.props?.display).toBe('none')
  await ui.unmount()
})

test('the expanded band reveals itself on hover', async ($, on) => {
  engine(on)
  const ui = await mountBand($)

  const panel = await expandedOf(ui)
  expect(panel?.hover).toEqual({ display: 'flex', scope: 'session-card' })
  await ui.unmount()
})

test('connected shows all five parts with the count of loaded tools', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  expect((await findText(ui, '116 loaded'))?.text).toBe('116 loaded')
  await ui.unmount()
})

test('a part shows its name only while the pointer is over it', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  const name = (await ui.find({ key: 'Kanban app' }))?.children?.[2]
  expect([name?.props?.display, name?.hover?.display, name?.children?.[0]?.children?.[0]]).toEqual(['none', 'flex', 'Kanban app'])
  await ui.unmount()
})

test('connected has no heading above the five parts', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  expect(await findText(ui, 'Connected')).toBeFalsy()
  await ui.unmount()
})

test('a second press on the icon collapses the band', async ($, on) => {
  engine(on)
  const ui = await pinnedBand($)

  await ui.press({ key: 'health-icon' })

  expect((await expandedOf(ui))?.props?.display).toBe('none')
  await ui.unmount()
})

test('a lost server shows Disconnected', async ($, on) => {
  const stub = engine(on)
  stub.serverLost = true
  const ui = await pinnedBand($)

  expect((await findText(ui, 'Disconnected'))?.text).toBe('Disconnected')
  await ui.unmount()
})

test('a server from another checkout shows Tools missing with the count', async ($, on) => {
  const stub = engine(on)
  stub.rawText = "KeyError: 'server-health.report'"
  const ui = await pinnedBand($)

  expect((await findText(ui, /116 loaded, server-health.report/))?.text).toBe('116 loaded, server-health.report is not one of them.')
  await ui.unmount()
})

test('Reconnect that succeeds reads the active ticket again', async ($, on) => {
  const stub = engine(on)
  stub.serverLost = true
  const ui = await pinnedBand($)
  stub.serverLost = false
  stub.calls.length = 0

  await ui.press({ key: 'health-reconnect' })

  expect(stub.calls).toContain('board.show')
  await ui.unmount()
})

test('Reconnect on a server still lost shows the try it is on', async ($, on) => {
  const stub = engine(on)
  stub.serverLost = true
  const ui = await pinnedBand($)

  await ui.press({ key: 'health-reconnect' })

  expect((await findText(ui, /Try 1 of 3/))?.text).toBe('Waiting for plugin:cdd:cdd to answer. Try 1 of 3.')
  await ui.unmount()
})

test('Details lists the failing tool, the error and the fix', async ($, on) => {
  const stub = engine(on)
  stub.serverLost = true
  const ui = await pinnedBand($)

  await ui.press({ key: 'health-details' })

  expect((await findText(ui, /Press Reconnect/))?.text).toBe('Press Reconnect. If that fails, press Run install.')
  await ui.unmount()
})

test('the health band yields to a survey', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  // Beneath the plugins nothing draws, so a band that passed the survey through finds nothing to mount.
  await expect($.ui.mount({ ...BAND, props: { ...BAND.props, hasSurvey: true } })).rejects.toThrow('no implementation for ui.render')
})

// (E) Record Session Action

test('should send the chat id with a cdd tool call', async ($, on) => {
  engine(on)
  let sent: Record<string, unknown> = {}
  on('tool.call', (_: unknown, e: Record<string, unknown>) => {
    sent = e
    return { result: {} }
  })

  await $.tool.call({ tool: 'mcp__plugin_cdd_cdd__validate_validate', paths: 'cart.py' } as any)

  expect(sent.conversation_id).toBe('chat-1')
})

test('should send another tool its own arguments only', async ($, on) => {
  engine(on)
  let sent: Record<string, unknown> = {}
  on('tool.call', (_: unknown, e: Record<string, unknown>) => {
    sent = e
    return { result: {} }
  })

  await $.tool.call({ tool: 'Bash', command: 'ls' })

  expect(sent.conversation_id).toBeUndefined()
})
