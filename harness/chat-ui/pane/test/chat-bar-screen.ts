// What a person sees of the chat bar, for the story tests: the lifecycle that opens it, lookups by key and text, and
// the assertions the stories repeat.
import { expect } from 'claude-code/testing'

import { cdd, type World } from './cdd-stub'
import type { Lifecycle } from './story-test'

export const BAR = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  surface: 'desktop',
  props: { hasSurvey: false, isWorking: false, maxRows: 24, bodyColumns: 160, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

// How long the engine is given to finish what a timer or the installer started before a step reads the chat bar.
const ENGINE_SETTLE_MILLISECONDS = 50

// Every chat bar story: the engine and cdd stubbed before the steps; once the Givens have seeded cdd, the chat starts,
// one prompt has the chat bar read the board, and the bar is mounted above the prompt.
export const CHAT_BAR: Lifecycle = {
  wire: (on, scene) => {
    scene.world = cdd(on)
  },
  mount: async $ => {
    await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
    await $.prompt.submit({ text: 'look' })
    return $.ui.mount(BAR)
  },
}

export const findText = (ui: any, text: RegExp | string) => ui.find({ type: 'Text', text })

// The props of the element drawn with this key, or undefined when nothing is.
export const drawn = async (ui: any, key: string) => ui.find({ key })

// The keys of the Buttons drawn under an element, in the order they read left to right and top to bottom.
export function buttonKeys(node: any): string[] {
  if (!node || typeof node !== 'object') return []
  const own = node.type === 'Button' ? [String(node.key ?? node.props?.key)] : []
  const children = Array.isArray(node.children) ? node.children : node.children ? [node.children] : []
  return [...own, ...children.flatMap(buttonKeys)]
}

export const settle = () => new Promise(resolve => setTimeout(resolve, ENGINE_SETTLE_MILLISECONDS))

export async function dueTimers(world: World): Promise<void> {
  const due = world.timers.splice(0)
  for (const fire of due) fire()
  await settle()
}

// A Text's words, however the test kit hands the element back, or a Button's label.
export const textOf = (node: any): string | undefined => node?.text ?? node?.children?.[0] ?? node?.props?.label

// The first Text drawn inside an element, such as a dot's mark or the health mark.
export const markOf = async (ui: any, key: string) => (await ui.find({ key }))?.children?.[0]

// A Button's label, the words a person reads on hover and a surface finds it by.
export const labelOf = async (ui: any, key: string): Promise<string | undefined> => {
  const node = await ui.find({ key })
  return node?.props?.label ?? node?.label
}

// The hover tip drawn above a keyed element, such as a dot's fidelity and state, or the action the button runs.
export async function tipOf(ui: any, key: string): Promise<string | undefined> {
  const node = await ui.find({ key })
  const tip = node?.children?.find((child: any) => child?.props?.position === 'absolute')
  return tip?.children?.map(textOf).join('')
}

// The words a Button holding Texts draws, read in order.
export async function wordsOf(ui: any, key: string): Promise<string | undefined> {
  return (await ui.find({ key }))?.children?.map(textOf).join('')
}

// Each keyed element's mark reads as given, such as { 'session-name-button': 'checkout-flow' }.
export async function expectMarks(ui: any, marks: Record<string, string>): Promise<void> {
  const read = await Promise.all(Object.keys(marks).map(async key => [key, textOf(await markOf(ui, key))]))
  expect(Object.fromEntries(read)).toEqual(marks)
}

// Each keyed element's mark reads and is coloured as given, such as { 'health-icon': ['✓', '#22C55E'] }.
export async function expectMarkLooks(ui: any, looks: Record<string, [string, string]>): Promise<void> {
  const read = await Promise.all(
    Object.keys(looks).map(async key => {
      const mark = await markOf(ui, key)
      return [key, [textOf(mark), mark?.props?.color]]
    }),
  )
  expect(Object.fromEntries(read)).toEqual(looks)
}

// Each keyed element's mark is coloured as given, such as a dot's shade.
export async function expectMarkColours(ui: any, colours: Record<string, string>): Promise<void> {
  const read = await Promise.all(Object.keys(colours).map(async key => [key, (await markOf(ui, key))?.props?.color]))
  expect(Object.fromEntries(read)).toEqual(colours)
}
