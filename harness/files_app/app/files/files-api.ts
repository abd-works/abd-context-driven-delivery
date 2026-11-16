import { PROJECT_HEADER, projectOfPage, type CddApi } from '@cdd/cdd-shared'

import { API_ROOT, FILES_HEADER } from './files-paths'

export class FilesCallFailure extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'FilesCallFailure'
  }
}

type Failure = { error?: string }

// Every call the page makes to its own server, naming the project the page was opened on, so each works in the session
// open there. A failed call throws what failed, so the page shows it where the person acted.
export class FilesApi implements CddApi {
  constructor(readonly project: string = projectOfPage()) {}

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    const response = await fetch(`${API_ROOT}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', [FILES_HEADER]: '1', ...(this.project ? { [PROJECT_HEADER]: this.project } : {}) },
      body: JSON.stringify(body),
    })
    const raw = await response.text()
    const answer = raw.trim() ? this.parsed(path, response.status, raw) : null
    if (!response.ok) throw new FilesCallFailure((answer as Failure | null)?.error || `${path} failed (HTTP ${response.status})`)
    return answer as Result | null
  }

  private parsed(path: string, status: number, raw: string): unknown {
    try {
      return JSON.parse(raw)
    } catch (cause) {
      throw new FilesCallFailure(`Invalid JSON from ${path} (HTTP ${status}): ${cause instanceof Error ? cause.message : String(cause)}`)
    }
  }
}
