import type { CddConnection } from './cdd-connection'

// What a request sent, in whatever framework received it.
export type CddRequest = { params?: unknown; query?: unknown; body?: unknown }

// How a browser object reaches the server: the page hands its own, so the install needs no HTTP package.
// It answers null once it has shown the person a failure, so the object keeps its state and the page stops there.
export type CddApi = { post<Result>(path: string, body: Record<string, unknown>): Promise<Result | null> }

// One tool's route, as plain data any server framework can mount.
export type CddRoute = { path: string; run: (cdd: CddConnection, request: CddRequest) => Promise<unknown> }

// The repository a page shows, which its ?project= link names; every call the page makes names it in this header, so
// the server answers the call on that repository's cdd connection (ProjectConnections), in the session open there.
export const PROJECT_QUERY = 'project'
export const PROJECT_HEADER = 'x-cdd-project'

// The folder the page's ?project= link names; empty for a page opened without one, which shows the server's own project.
export const projectOfPage = (search: string = (globalThis as { location?: { search: string } }).location?.search ?? ''): string => new URLSearchParams(search).get(PROJECT_QUERY) ?? ''

// The chat a page was opened beside, which its ?chat= link names, so the page can show a file in that chat's file viewer
// (Chat.send open_file); empty for a page no chat opened.
export const CHAT_QUERY = 'chat'
export const chatOfPage = (search: string = (globalThis as { location?: { search: string } }).location?.search ?? ''): string => new URLSearchParams(search).get(CHAT_QUERY) ?? ''

// The newest step a running call has reported, such as which file a long load is reading.
export type CddProgress = { tool: string; message: string }

// What the running calls are doing, for a page waiting on one. Mount it beside the objects' routes.
export const cddProgressRoutes: CddRoute[] = [{ path: '/cdd/progress', run: async cdd => cdd.progress() }]

// The part of a tool's published JSON Schema that says what one argument may be.
export type ArgumentSchema = { type?: string; items?: ArgumentSchema; anyOf?: ArgumentSchema[] }

export class CddRequestError extends Error {
  constructor(detail: string) {
    super(`The request does not fit the operation: ${detail}`)
    this.name = 'CddRequestError'
  }
}

export class CddNotReadError extends Error {
  constructor(object: string) {
    super(`This ${object} has no state yet: call one of its operations before reading it.`)
    this.name = 'CddNotReadError'
  }
}

const FITS_TYPE: Record<string, (value: unknown) => boolean> = {
  string: value => typeof value === 'string',
  integer: value => Number.isInteger(value),
  number: value => typeof value === 'number',
  boolean: value => typeof value === 'boolean',
  null: value => value === null,
  object: value => typeof value === 'object' && value !== null && !Array.isArray(value),
  array: value => Array.isArray(value),
}

const fits = (value: unknown, schema: ArgumentSchema): boolean => {
  if (schema.anyOf) return schema.anyOf.some(option => fits(value, option))
  if (!schema.type) return true
  if (!(FITS_TYPE[schema.type]?.(value) ?? true)) return false
  const items = schema.items
  return schema.type !== 'array' || !items || (value as unknown[]).every(item => fits(item, items))
}

const recordOf = (sent: unknown): Record<string, unknown> => (typeof sent === 'object' && sent !== null ? (sent as Record<string, unknown>) : {})

// The path wins over the query and the body, so an address in the path cannot be overridden by what was posted.
export function readArguments<Arguments>(request: CddRequest, properties: Record<string, ArgumentSchema>, required: string[]): Arguments {
  const sent = { ...recordOf(request.body), ...recordOf(request.query), ...recordOf(request.params) }
  const missing = required.filter(name => sent[name] === undefined)
  if (missing.length > 0) throw new CddRequestError(`missing ${missing.join(', ')}`)
  const wrong = Object.keys(properties).filter(name => sent[name] !== undefined && !fits(sent[name], properties[name] ?? {}))
  if (wrong.length > 0) throw new CddRequestError(`wrong type for ${wrong.join(', ')}`)
  return Object.fromEntries(Object.keys(properties).map(name => [name, sent[name]])) as Arguments
}
