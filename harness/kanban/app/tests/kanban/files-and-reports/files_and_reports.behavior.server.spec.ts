/**
 * Runs the shared behavior on TicketNodeAdapter, which calls the real cdd server on a throwaway project. Nothing is stubbed.
 */
import { afterAll, beforeEach, describe, expect, it } from 'vitest'

import { TicketNodeAdapter } from '@cdd/harness/kanban/ticket-node-adapter'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { CddProject } from 'test-utils/behavior-test/cdd-project'

import { filesAndReportsBehavior, type FilesAndReportsDriver } from './files_and_reports.spec.shared'

const project = new CddProject()

class FilesAndReportsNodeAdapterDriver implements FilesAndReportsDriver {
  private ticket(name: string): TicketNodeAdapter {
    return new TicketNodeAdapter(project.cdd, name)
  }

  async generatedFilesOf(ticket: string, fidelity: string): Promise<string[]> {
    const formats = (await this.ticket(ticket).files([fidelity]))[fidelity] ?? {}
    return Object.values(formats)
      .flat()
      .filter(entry => entry.exists)
      .map(entry => entry.path)
  }

  async textOfFile(ticket: string, _fidelity: string, path: string): Promise<string> {
    return (await this.ticket(ticket).readFile(path)).text
  }

  async reportPathOf(ticket: string, fidelity: string): Promise<string> {
    return (await this.ticket(ticket).report(fidelity)).path
  }

  async ruleNamesOf(ticket: string, fidelity: string): Promise<string[]> {
    return (await this.ticket(ticket).report(fidelity)).rules.map(rule => rule.name)
  }

  async failingLineOf(ticket: string, fidelity: string): Promise<number> {
    return (await this.ticket(ticket).report(fidelity)).rules[0]?.violations[0]?.line ?? 0
  }
}

let driver: FilesAndReportsNodeAdapterDriver

beforeEach(() => {
  project.reset()
  driver = new FilesAndReportsNodeAdapterDriver()
})

afterAll(() => project.close())

itBehavesLike(filesAndReportsBehavior, { describe, it, before: beforeEach, expect, driver: () => driver })
