// Given / When / Then on `claude plugin test`, the stories template's story-test helpers for a Claude Code mod.
// Each Scenario is one engine test, so every step gets the same `$` and stubbed MCP, and its steps run in order.
import { test } from 'claude-code/testing'

// scene carries what one step leaves for the next, such as the stubbed cdd server and the mounted pane.
type Step = ($: any, on: any, scene: any) => unknown
type StepWords = {
  given: (text: string, run?: Step) => void
  when: (text: string, run?: Step) => void
  then: (text: string, run?: Step) => void
  and: (text: string, run?: Step) => void
  but: (text: string, run?: Step) => void
}

// The infrastructure every scenario of a story runs on, kept out of its steps: wire stubs the engine and the systems
// beneath the pane, before any step; mount opens the pane a person sees, once the Givens have seeded those systems;
// check asserts what every scenario of the story leaves true, once its steps have passed.
export type Lifecycle = {
  wire: (on: any, scene: any) => void
  mount: ($: any) => Promise<any>
  check?: (scene: any) => void
}

type Word = keyof StepWords
// When and Then act on the pane, so the pane is open from the first of them; And and But carry on the word before.
const ACTING: Word[] = ['when', 'then']

let storyName = ''
let storyLifecycle: Lifecycle

export function story(name: string, lifecycle: Lifecycle, build: () => void): void {
  storyName = name
  storyLifecycle = lifecycle
  build()
}

export function scenario(name: string, build: (words: StepWords) => void): void {
  const lifecycle = storyLifecycle
  const steps: { word: Word; run: Step }[] = []
  const words = Object.fromEntries((['given', 'when', 'then', 'and', 'but'] as Word[]).map(word => [word, (_text: string, run: Step = () => undefined) => steps.push({ word, run })]))
  build(words as StepWords)
  test(`${storyName} › ${name}`, async ($, on) => {
    let mounted: any
    const open = async () => (mounted ??= await lifecycle.mount($))
    // scene.ui opens the pane the first time a step uses it, such as a Given that seeds what a person pressed, and the
    // pane is open from the first When or Then either way.
    // It has no `then`, so awaiting it never reads as a promise.
    const forward = (method: string) => (method === 'then' ? undefined : async (...args: unknown[]) => (await open())[method](...args))
    const scene: any = { ui: new Proxy({}, { get: (_, method: string) => forward(method) }) }
    lifecycle.wire(on, scene)
    try {
      for (const { word, run } of steps) {
        if (ACTING.includes(word)) await open()
        await run($, on, scene)
      }
      lifecycle.check?.(scene)
    } finally {
      await mounted?.unmount()
    }
  })
}
