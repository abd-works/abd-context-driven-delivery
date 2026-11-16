// The port an app server listens on, read the same way by every app's server: the Graph's, the Files app's, and the
// session board's. The chat that opens an app starts its server with `--port N` when the cdd server it talks to serves
// the dev lane, whose apps answer on ports of their own (harness/mcp/server_lanes.py, DEV_APP_PORT_OFFSET); the stable
// lane names no port, so the server falls back to its env variable, then to the first port its ports file gives it.
export const PORT_ARGUMENT = '--port'

export function servePort(argv: readonly string[], fallback: number): number {
  const named = argv.indexOf(PORT_ARGUMENT)
  return named >= 0 && named + 1 < argv.length ? Number(argv[named + 1]) : fallback
}
