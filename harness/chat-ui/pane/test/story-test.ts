// Given / When / Then on `claude plugin test`, the stories template's story-test helpers for a Claude Code mod.
// Each Scenario is one engine test, so every step gets the same `$` and stubbed MCP, and its steps run in order.
import { test } from 'claude-code/testing'

// scene carries what one step leaves for the next, such as the stubbed cdd server and the mounted chat bar.
type Step = ($: any, on: any, scene: any) => unknown
type StepWords = {
  given: (text: string, run?: Step) => void
  when: (text: string, run?: Step) => void
  then: (text: string, run?: Step) => void
  and: (text: string, run?: Step) => void
  but: (text: string, run?: Step) => void
}

let storyName = ''

export function story(name: string, build: () => void): void {
  storyName = name
  build()
}

export function scenario(name: string, build: (words: StepWords) => void): void {
  const steps: Step[] = []
  const add = (_text: string, run: Step = () => undefined) => { steps.push(run) }
  build({ given: add, when: add, then: add, and: add, but: add })
  test(`${storyName} › ${name}`, async ($, on) => {
    const scene = {}
    for (const run of steps) await run($, on, scene)
  })
}
