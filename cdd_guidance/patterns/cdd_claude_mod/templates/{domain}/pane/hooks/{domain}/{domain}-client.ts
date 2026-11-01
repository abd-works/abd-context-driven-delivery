import { atom, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { {Domain}Json } from '../../types'

const SERVER = 'cdd'

// The last JSON the tool returned. An atom holds values, because $.state outlives a reload and a class instance would not.
export const {domain}State = atom({ plugin: 'cdd-{domain}', key: '{domain}' } as const, null as {Domain}Json | null)

// Mirrors the Python {Domain}: properties a view paints, operations a person triggers. It decides nothing.
export class {Domain}Client {
  constructor(
    private readonly $: EngineInterface,
    private readonly json: {Domain}Json,
  ) {}

  get name(): string {
    return this.json.name
  }

  get nextAction(): string | null {
    return this.json.next_action
  }

  // One operation, one MCP tool, one domain operation, all with the same verb.
  async moveNext(): Promise<void> {
    const moved = await this.call('{domain}.move_next', { name: this.name })
    if (moved !== null) update(this.$, {domain}State, () => moved)
  }

  // The mod's only MCP call, so a failure is shown to the person in one place.
  private async call(tool: string, args: Record<string, unknown>): Promise<{Domain}Json | null> {
    let result
    try {
      result = await this.$.mcp.call(SERVER, tool, args)
    } catch (failure) {
      this.$.ui.status(`cdd {domain}: ${String(failure)}`)
      return null
    }
    const text = result.content[0]?.text
    if (result.isError || text === undefined) {
      this.$.ui.toast(`cdd ${tool} failed${text ? `: ${text}` : ''}`)
      return null
    }
    return JSON.parse(text) as {Domain}Json
  }
}
