// A stand-in for the part of the Claude app the cdd-board mod runs in, so the mod's own hooks, views and clients run
// unchanged in a plain browser page a test drives. It is the module the mod imports as 'claude-code' (atom, read,
// update), the engine interface `$` the mod's hooks are handed, the global JSX factory `h`, and the drawing surface
// that turns the mod's element trees into the page. It is the only fake: a cdd tool call goes to a real cdd server
// through the page's own server (`/cdd/call`), and what the mod sends to the chat (prompts, slash commands, calls to
// the app's other servers, toasts) is recorded on `window.chatBarPage.sent` for a test to read.
//
// It draws in character cells as the app does: a column is one `ch` and a row is one line.

type Ref = { plugin: string; key: string }
type Atom<T> = { ref: Ref; initial: T }
type Hook = ($: Engine, e: Record<string, unknown>, next: (e: Record<string, unknown>) => Promise<unknown>) => unknown
type Registered = { event: string; matcher: Record<string, unknown>; hook: Hook }
type RenderNode = { tag: string; props: Record<string, unknown>; children: unknown[] }
type Sent = { kind: string; text: string }
type Engine = Record<string, Record<string, unknown> | unknown>

const PLUGIN = 'cdd-board'
// The cdd plugin's server, as the app names it; a call to any other server is the app's own, recorded and answered ok.
const CDD_SERVER = 'plugin:cdd:cdd'
const CDD_TOOL_PREFIX = 'mcp__plugin_cdd_cdd__'
const TAGS = ['Box', 'Text', 'Button', 'Input', 'Markdown', 'Progress', 'Svg', 'Link']
// The band's room: the cells its tree is laid out in, and the rows it may take before it scrolls.
const BODY_COLUMNS = 150
const MAX_ROWS = 40
const TOAST_SHOWN_MILLISECONDS = 8000
const COLUMN_PROPS = ['width', 'minWidth', 'left', 'right', 'paddingX', 'marginX', 'marginLeft']
const ROW_PROPS = ['height', 'top', 'bottom']
const SAME_NAME_PROPS = ['flexDirection', 'alignItems', 'justifyContent', 'flexGrow', 'flexShrink', 'flexWrap', 'position', 'backgroundColor']

const values = new Map<string, unknown>()
const hooks: Registered[] = []
const sent: Sent[] = []
const panes = new Map<string, string>()
const typed = new Map<string, string>()
let pointer: Element | null = null
let isDrawing = false
let isDrawDue = false

function keyOf(ref: Ref): string {
  return `${ref.plugin}:${ref.key}`
}

// --- the module the mod imports as 'claude-code'

export function atom<T>(ref: Ref, initial: T, _options?: unknown): Atom<T> {
  return { ref, initial }
}

export async function read<T>(_$: unknown, source: Atom<T>): Promise<T> {
  const key = keyOf(source.ref)
  return values.has(key) ? (values.get(key) as T) : source.initial
}

// A write redraws what reads it, as the engine does.
export async function update<T>(_$: unknown, target: Atom<T>, change: (value: T) => T): Promise<T> {
  const changed = change(await read(_$, target))
  values.set(keyOf(target.ref), changed)
  drawSoon()
  return changed
}

// --- the JSX factory: plain data from a tag of the element table, or from a component

function h(tag: string | ((props: Record<string, unknown>) => unknown), props: Record<string, unknown> | null, ...children: unknown[]): unknown {
  const flat = children.flat(Infinity)
  if (typeof tag === 'function') return tag({ ...(props ?? {}), children: flat })
  return { tag, props: props ?? {}, children: flat }
}

function Fragment(props: { children?: unknown[] }): RenderNode {
  return { tag: 'Box', props: { flexDirection: 'column' }, children: props.children ?? [] }
}

// --- events: each hook is ($, e, next), and next runs the hooks beneath and then the app's own behaviour

function matches(matcher: Record<string, unknown>, e: Record<string, unknown>): boolean {
  return Object.entries(matcher).every(([name, value]) => e[name] === value)
}

async function fire(event: string, e: Record<string, unknown>, own: (e: Record<string, unknown>) => unknown): Promise<unknown> {
  const chain = hooks.filter(each => each.event === event && matches(each.matcher, e))
  const run = (index: number, input: Record<string, unknown>): Promise<unknown> =>
    Promise.resolve(index < chain.length ? chain[index].hook(engine, input, later => run(index + 1, later)) : own(input))
  return run(0, e)
}

function record(kind: string, text: string): void {
  sent.push({ kind, text })
  const line = document.createElement('div')
  line.className = `sent sent-${kind}`
  line.textContent = `${kind}: ${text}`
  document.getElementById('transcript')?.append(line)
}

function showToast(text: string): void {
  const toast = document.createElement('div')
  toast.className = 'toast'
  toast.textContent = text
  document.getElementById('toasts')?.append(toast)
  setTimeout(() => toast.remove(), TOAST_SHOWN_MILLISECONDS)
}

async function post(path: string, body: unknown): Promise<Record<string, unknown>> {
  const answer = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  return (await answer.json()) as Record<string, unknown>
}

const query = new URLSearchParams(location.search)
const project = query.get('project') ?? ''
const chat = query.get('chat') ?? 'chat-bar-page'

// --- the engine interface: every call the mod makes on the app

const engine: Engine = {
  ui: {
    resolve: () => Object.fromEntries(TAGS.map(tag => [tag, tag])),
    toast: (text: string) => {
      record('toast', text)
      showToast(text)
    },
    log: (text: string) => record('log', text),
    status: (text?: string) => {
      const line = document.getElementById('status-line')
      if (line) line.textContent = text ?? ''
    },
    open: async ({ id, title }: { id: string; title: string }) => {
      panes.set(id, title)
      record('pane', title)
      drawSoon()
      return { isPlaced: true }
    },
    invalidate: async () => undefined,
  },
  session: { root: async () => project, id: async () => chat, messages: async () => [] },
  mcp: {
    call: async (server: string, tool: string, args: Record<string, unknown>) => {
      if (server !== CDD_SERVER) {
        record('app-call', `${server} ${tool} ${JSON.stringify(args)}`)
        return { content: [{ type: 'text', text: '{}' }], isError: false }
      }
      const answer = await post('/cdd/call', { tool, args, project, chat })
      if (typeof answer.unreachable === 'string') throw new Error(answer.unreachable)
      return { content: [{ type: 'text', text: answer.text }], isError: answer.isError }
    },
  },
  clock: {
    after: (milliseconds: number, then: () => void) => void setTimeout(then, milliseconds),
    every: (milliseconds: number, then: () => void) => void setInterval(then, milliseconds),
    sleep: (milliseconds: number) => new Promise(resolve => setTimeout(resolve, milliseconds)),
  },
  prompt: {
    submit: async ({ text }: { text: string }) => {
      record('prompt', text)
      return {}
    },
    fill: async ({ text, mode }: { text: string; mode?: string }) => {
      const box = document.getElementById('prompt-box') as HTMLTextAreaElement
      box.value = mode === 'append' && box.value ? `${box.value} ${text}` : text
      record('filled', text)
      return { isFilled: true }
    },
  },
  command: {
    run: async ({ command, args }: { command: string; args?: string }) => {
      record('command', `/${command}${args ? ` ${args}` : ''}`)
      return {}
    },
    list: async () => [],
    register: async () => undefined,
  },
  process: {
    // The chat works in the project's own checkout; any other program the mod runs is recorded, never run.
    run: async (argv: string[]) => {
      if (argv.join(' ') === 'git rev-parse --show-toplevel') return { exitCode: 0, stdout: `${project}\n`, stderr: '' }
      record('process', argv.join(' '))
      return { exitCode: 0, stdout: '', stderr: '' }
    },
    spawn: ({ argv }: { argv: string[] }) => {
      record('process', argv.join(' '))
      return (async function* () {})()
    },
  },
  // CDD is installed in the folder the chat works in, and the mod was published with an install command.
  fs: { exists: async () => true, read: async () => JSON.stringify({ command: ['python', 'scripts/install.py', '--ide', 'Claude', '--from-chat'] }) },
  tool: {
    list: async () => {
      const answer = await fetch('/cdd/tools')
      return ((await answer.json()) as string[]).map(name => ({ name: `${CDD_TOOL_PREFIX}${name}` }))
    },
  },
  plugin: { root: '/cdd-board' },
}

// --- the drawing surface: the mod's element trees as the page

function cells(value: unknown, unit: string): string {
  return typeof value === 'number' ? `calc(${value} * ${unit})` : String(value)
}

function styleBox(box: HTMLElement, props: Record<string, unknown>): void {
  const style = box.style as unknown as Record<string, string>
  style.display = props.display === 'none' ? 'none' : 'flex'
  style.flexDirection = 'row'
  style.position = 'relative'
  for (const name of SAME_NAME_PROPS) if (props[name] !== undefined) style[name] = String(props[name])
  for (const name of COLUMN_PROPS) if (props[name] !== undefined) applyCells(style, name, props[name], '1ch')
  for (const name of ROW_PROPS) if (props[name] !== undefined) applyCells(style, name, props[name], 'var(--row)')
  if (props.gap !== undefined) style.gap = `${cells(props.gap, 'var(--row)')} ${cells(props.gap, '1ch')}`
  if (props.borderStyle) style.border = `1px solid ${String(props.borderColor ?? 'currentColor')}`
}

function applyCells(style: Record<string, string>, name: string, value: unknown, unit: string): void {
  const size = cells(value, unit)
  if (name === 'paddingX') style.paddingLeft = style.paddingRight = size
  else if (name === 'marginX') style.marginLeft = style.marginRight = size
  else style[name] = size
}

function drawBox(node: RenderNode, site: string): HTMLElement {
  const box = document.createElement('div')
  box.className = 'box'
  styleBox(box, node.props)
  if (typeof node.props.key === 'string') box.dataset.boxKey = node.props.key
  if (node.props.hover) box.dataset.hover = JSON.stringify(node.props.hover)
  box.append(...drawAll(node.children, site))
  return box
}

function drawText(node: RenderNode, site: string): HTMLElement {
  const text = document.createElement('span')
  text.className = 'text'
  if (node.props.color) text.style.color = String(node.props.color)
  if (node.props.weight) text.style.fontWeight = node.props.weight === 'semibold' ? '600' : String(node.props.weight)
  if (node.props.underline) text.style.textDecoration = 'underline'
  if (String(node.props.wrap ?? '').startsWith('truncate')) text.classList.add('truncate')
  text.append(...drawAll(node.children, site))
  return text
}

// A press is the app's ui.press event, whose own behaviour runs the closure the mod gave the button.
function drawButton(node: RenderNode, site: string): HTMLElement {
  const button = document.createElement('button')
  const key = typeof node.props.key === 'string' ? node.props.key : ''
  button.className = `button${node.props.plain ? ' plain' : ''}${node.props.variant === 'primary' ? ' primary' : ''}`
  button.dataset.key = key
  if (node.props.label !== undefined) button.append(String(node.props.label))
  button.append(...drawAll(node.children, site))
  button.addEventListener('click', () => {
    const [component, requestId = ''] = site.split(':')
    void fire('ui.press', { plugin: PLUGIN, element: key, component, requestId, surface: 'desktop' }, () => (node.props.onPress as (() => unknown) | undefined)?.()).then(drawSoon)
  })
  return button
}

function drawInput(node: RenderNode): HTMLElement {
  const input = document.createElement('input')
  const key = String(node.props.key ?? '')
  input.className = 'input'
  input.dataset.key = key
  input.placeholder = String(node.props.placeholder ?? '')
  input.value = typed.get(key) ?? String(node.props.value ?? '')
  input.addEventListener('input', () => typed.set(key, input.value))
  input.addEventListener('keydown', pressed => {
    if (pressed.key !== 'Enter') return
    typed.delete(key)
    void Promise.resolve((node.props.onSubmit as ((value: string) => unknown) | undefined)?.(input.value)).then(drawSoon)
  })
  return input
}

function drawOther(node: RenderNode): HTMLElement {
  const element = document.createElement('div')
  element.className = node.tag.toLowerCase()
  if (typeof node.props.key === 'string') element.dataset.key = node.props.key
  if (node.tag === 'Svg') element.innerHTML = String(node.props.source ?? '')
  else element.textContent = String(node.props.text ?? node.props.label ?? '')
  return element
}

function drawAll(children: unknown[], site: string): (Node | string)[] {
  return children.flat(Infinity).flatMap(child => {
    if (child === null || child === undefined || child === false || child === true) return []
    if (typeof child !== 'object') return [String(child)]
    const node = child as RenderNode
    if (node.tag === 'Box') return [drawBox(node, site)]
    if (node.tag === 'Text') return [drawText(node, site)]
    if (node.tag === 'Button') return [drawButton(node, site)]
    if (node.tag === 'Input') return [drawInput(node)]
    return [drawOther(node)]
  })
}

async function drawSite(place: string, component: string, requestId: string, props: Record<string, unknown>): Promise<void> {
  const site = requestId ? `${component}:${requestId}` : component
  const tree = await fire('ui.render', { component, requestId, surface: 'desktop', props }, () => null)
  const holder = document.getElementById(place)
  if (!holder) return
  const focused = document.activeElement instanceof HTMLInputElement ? document.activeElement.dataset.key : undefined
  holder.replaceChildren(...drawAll([tree], site))
  if (focused) (holder.querySelector(`input[data-key="${focused}"]`) as HTMLInputElement | null)?.focus()
}

async function drawHint(): Promise<void> {
  const hint = await fire('ui.render', { component: 'PromptHint', surface: 'desktop', props: { hint: '' } }, e => (e.props as { hint: string }).hint)
  const line = document.getElementById('prompt-hint')
  if (line) line.textContent = typeof hint === 'string' ? hint : ''
}

async function draw(): Promise<void> {
  await drawSite('above-prompt', 'AbovePrompt', '', { bodyColumns: BODY_COLUMNS, maxRows: MAX_ROWS, hasSurvey: false })
  await drawHint()
  const beside = document.getElementById('panes')
  for (const [id, title] of panes) {
    if (!document.getElementById(`pane-${id}`)) {
      const pane = document.createElement('section')
      pane.innerHTML = `<h2></h2><div id="pane-${id}"></div>`
      pane.querySelector('h2')!.textContent = title
      beside?.append(pane)
    }
    await drawSite(`pane-${id}`, 'Pane', id, {})
  }
  applyHover()
}

// One draw at a time; a change during a draw draws once more after it.
function drawSoon(): void {
  isDrawDue = true
  if (isDrawing) return
  isDrawing = true
  void (async () => {
    while (isDrawDue) {
      isDrawDue = false
      await draw().catch(failure => record('draw-failed', String(failure)))
    }
    isDrawing = false
  })()
}

// The surface applies a Box's hover overrides while the pointer is over its nearest keyed Box, or, given a scope,
// over any Box of that group; no hook runs.
function applyHover(): void {
  for (const box of document.querySelectorAll<HTMLElement>('[data-hover]')) {
    const hover = JSON.parse(box.dataset.hover ?? '{}') as { scope?: string; display?: string }
    if (hover.display === undefined) continue
    const group = hover.scope ? [...document.querySelectorAll<HTMLElement>('[data-hover], [data-box-key]')].filter(each => inScope(each, hover.scope!)) : [box.closest('[data-box-key]')]
    const isOver = pointer !== null && group.some(member => member?.contains(pointer))
    box.style.display = isOver ? hover.display : 'none'
  }
}

function inScope(box: HTMLElement, scope: string): boolean {
  return box.dataset.boxKey === scope || (JSON.parse(box.dataset.hover ?? '{}') as { scope?: string }).scope === scope
}

// --- the page: the mod's hooks registered and the chat started, as the app starts a chat with the mod loaded

export async function startChat(register: (on: (event: string, a: unknown, b?: unknown) => void) => void): Promise<void> {
  Object.assign(globalThis, { h, Fragment, chatBarPage: { sent, values } })
  register((event, a, b) => hooks.push(b ? { event, matcher: a as Record<string, unknown>, hook: b as Hook } : { event, matcher: {}, hook: a as Hook }))
  document.addEventListener('mouseover', moved => {
    pointer = moved.target as Element
    applyHover()
  })
  document.getElementById('prompt-box')?.addEventListener('input', () => void fire('prompt.change', { text: (document.getElementById('prompt-box') as HTMLTextAreaElement).value }, () => ({})))
  await fire('session.start', { cwd: project, surface: 'desktop', isInteractive: true }, e => ({ cwd: e.cwd }))
  drawSoon()
}
