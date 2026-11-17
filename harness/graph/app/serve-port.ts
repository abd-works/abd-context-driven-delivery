// The port an app server listens on, and the cdd home it talks to, read the same way by every app's server: the
// Graph's, the Files app's, and the session board's. The chat that opens an app starts its server with `--port N` and
// `--cdd-home H` when the cdd server it talks to serves the dev lane, whose apps answer on ports of their own
// (harness/mcp/server_lanes.py, DEV_APP_PORT_OFFSET) and talk to the dev lane's server; the stable lane names neither,
// so the server falls back to its env variables, then to the first port its ports file gives it.
export const PORT_ARGUMENT = '--port'
export const CDD_HOME_ARGUMENT = '--cdd-home'

export function servePort(argv: readonly string[], fallback: number): number {
  const named = argument(argv, PORT_ARGUMENT)
  return named === undefined ? fallback : Number(named)
}

// A server started outside the chat's environment, as WMI starts one outside a chat's Windows job, holds no CDD_HOME
// or the stable lane's, so a dev-lane app would ask the stable lane's server, running main's code.
export function serveLaneHome(argv: readonly string[], environment: Record<string, string | undefined> = process.env): void {
  const named = argument(argv, CDD_HOME_ARGUMENT)
  if (named !== undefined) environment.CDD_HOME = named
}

function argument(argv: readonly string[], name: string): string | undefined {
  const named = argv.indexOf(name)
  return named >= 0 && named + 1 < argv.length ? argv[named + 1] : undefined
}
