import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { {Object}Data } from '@cdd/{source-folders}/{object}'

const SERVER = 'cdd'

// The last JSON the tool returned. An atom holds values, because $.state outlives a reload and a class instance would not.
const {object}State = atom({ plugin: 'cdd-{domain}', key: '{object}' } as const, null as {Object}Data | null)

// Mirrors the Python {Object} for display. It holds no $, because the engine refuses $ passed to a constructor or a method.
export class {Object}Client {
  constructor(private readonly json: {Object}Data) {}

  get name(): string {
    return this.json.name
  }

  get nextAction(): string | null {
    return this.json.next_action
  }
}

// The atom stays in this file, because the engine's scan cannot follow an atom imported from another file.
export async function current{Object}($: EngineInterface): Promise<{Object}Client | null> {
  const json = await read($, {object}State)
  return json === null ? null : new {Object}Client(json)
}

// The mod's only MCP call, so a failure is shown to the person in one place.
async function callTool($: EngineInterface, tool: string, args: Record<string, unknown>): Promise<{Object}Data | null> {
  let result
  try {
    result = await $.mcp.call(SERVER, tool, args)
  } catch (failure) {
    $.ui.status(`cdd {domain}: ${String(failure)}`)
    return null
  }
  const text = result.content[0]?.text
  if (result.isError || text === undefined) {
    $.ui.toast(`cdd ${tool} failed${text ? `: ${text}` : ''}`)
    return null
  }
  return JSON.parse(text) as {Object}Data
}

// One action, one MCP tool, one domain operation, all with the same verb.
export async function moveNext($: EngineInterface, {object}: {Object}Client): Promise<void> {
  const moved = await callTool($, '{object}.move_next', { {object}: {object}.name })
  if (moved !== null) await update($, {object}State, () => moved)
}
