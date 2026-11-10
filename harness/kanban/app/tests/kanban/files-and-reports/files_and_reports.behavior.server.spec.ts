/**
 * Runs the shared behavior on TicketAdapter, which calls the real cdd server on a throwaway project. Nothing is stubbed.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import { FidelityProgressAdapter } from '@cdd/harness/kanban/fidelity-progress'
import { SessionAdapter } from '@cdd/space/session/session'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { filesAndReportsBehavior, type FilesAndReportsDriver } from './files_and_reports.spec.shared'

const project = new CddProject()

class FilesAndReportsAdapterDriver implements FilesAndReportsDriver {
  private progress(ticket: string, fidelity: string): FidelityProgressAdapter {
    return new FidelityProgressAdapter(project.cdd, ticket, fidelity)
  }

  // A ticket's session is named by its session.json, from the project.
  private session(ticket: string): SessionAdapter {
    return new SessionAdapter(project.cdd, `.sessions/${ticket}/session.json`)
  }

  async generatedFilesOf(ticket: string, fidelity: string): Promise<string[]> {
    const formats = await this.progress(ticket, fidelity).files()
    return Object.values(formats)
      .flat()
      .filter(entry => entry.exists)
      .map(entry => entry.path)
  }

  async textOfFile(ticket: string, _fidelity: string, path: string): Promise<string> {
    return (await this.session(ticket).readFile(path)).text
  }

  async reportPathOf(ticket: string, fidelity: string): Promise<string> {
    return (await this.progress(ticket, fidelity).report()).path
  }

  async ruleNamesOf(ticket: string, fidelity: string): Promise<string[]> {
    return (await this.progress(ticket, fidelity).report()).rules.map(rule => rule.name)
  }

  async failingLineOf(ticket: string, fidelity: string): Promise<number> {
    return (await this.progress(ticket, fidelity).report()).rules[0]?.violations[0]?.line ?? 0
  }
}

let driver: FilesAndReportsAdapterDriver

beforeEach(() => {
  project.reset()
  driver = new FilesAndReportsAdapterDriver()
})

afterAll(() => project.close())

itBehavesLike(filesAndReportsBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
