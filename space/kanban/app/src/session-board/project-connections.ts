import type { Request } from 'express'
import { resolve } from 'node:path'

import { CddConnection } from '@cdd/cdd-connection'

// The request header that names the repository a call is about: the page sends its ?project= folder, a chat its own
// repository's folder. A call without it is about the project this server was started with.
export const PROJECT_HEADER = 'x-cdd-project'

// One board server serves every repository on this machine, each through a cdd connection of its own, so /board from any
// chat shows that chat's tickets rather than those of the repository the server happened to start in.
export class ProjectConnections {
  private readonly connections = new Map<string, CddConnection>()

  constructor(
    private readonly started: CddConnection,
    private readonly connect: (folder: string) => CddConnection = folder => new CddConnection(folder),
  ) {}

  of(request: Request): CddConnection {
    const named = request.get(PROJECT_HEADER)?.trim()
    if (!named) return this.started
    const folder = resolve(named)
    let connection = this.connections.get(folder)
    if (!connection) {
      connection = this.connect(folder)
      this.connections.set(folder, connection)
    }
    return connection
  }

  async close(): Promise<void> {
    await Promise.all([this.started, ...this.connections.values()].map(connection => connection.close()))
  }
}
