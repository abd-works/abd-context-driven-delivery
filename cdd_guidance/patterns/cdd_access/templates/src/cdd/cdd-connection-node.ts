/**
 * Starts one cdd server and carries calls to it. Names no tool: each object's adapter class does that.
 *
 * ```
 * file: src/cdd/cdd-connection-node.ts
 * ```
 */
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

import type { CddConnection } from '@cdd/cdd-connection'

const LONGEST_TOOL_MILLISECONDS = 600_000

export class CddToolError extends Error {
  constructor(tool: string, detail: string) {
    super(`cdd ${tool} failed: ${detail}`)
    this.name = 'CddToolError'
  }
}

export class CddNotConnectedError extends Error {
  constructor(detail: string) {
    super(`The cdd server is not connected: ${detail}`)
    this.name = 'CddNotConnectedError'
  }
}

export type CddServerCommand = { command: string; args: string[]; env: Record<string, string>; cwd: string }

export class CddConnectionNode implements CddConnection {
  private client: Promise<Client> | null = null

  constructor(private readonly server: CddServerCommand) {}

  private connect(): Promise<Client> {
    const transport = new StdioClientTransport({ ...this.server, stderr: 'ignore' })
    const client = new Client({ name: '{application}', version: '0.1.0' })
    transport.onclose = () => {
      this.client = null
    }
    return client.connect(transport).then(() => client)
  }

  private connected(): Promise<Client> {
    this.client ??= this.connect().catch(failure => {
      this.client = null
      throw new CddNotConnectedError(String(failure))
    })
    return this.client
  }

  async call<Result>(tool: string, args: Record<string, unknown>): Promise<Result> {
    const client = await this.connected()
    const result = await client.callTool({ name: tool, arguments: args }, undefined, { timeout: LONGEST_TOOL_MILLISECONDS })
    const text = (result.content as { text?: string }[])[0]?.text
    if (result.isError || text === undefined) throw new CddToolError(tool, text ?? 'no result')
    return this.parsed<Result>(tool, text)
  }

  // The server sends a failed operation's error as plain text, and every successful operation as JSON.
  private parsed<Result>(tool: string, text: string): Result {
    try {
      return JSON.parse(text) as Result
    } catch {
      throw new CddToolError(tool, text)
    }
  }

  async close(): Promise<void> {
    const open = this.client
    this.client = null
    if (open) await (await open).close()
  }
}
