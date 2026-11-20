import type { SessionClientGenerated, SessionFileData } from '@cdd/space/session/session'
import type { SourceCallout } from '@source-view/source-callouts'

import type { FilesStore } from './files-state'
import { calloutsOf, fileAnswered } from './source-of-file'

// The connector of the session's graph a step's callout follows: what the step invokes, or the example it observes.
const CONNECTOR_OF: Partial<Record<SourceCallout['kind'], string>> = { call: 'invokes', example: 'observes' }

// The callouts a file view shows, in the rendered view and the source view alike: those the session answers for the
// file (session.file), narrowed by the file view's filters as the graph view's trees are. A callout into a file of a
// practice, stage or format turned off is left out, and so is a step's callout while the graph's node filter leaves out
// its connector. The page keeps none of it: the files listed and the connectors chosen are the session's own answers.
export class FileCallouts {
  constructor(
    private readonly store: FilesStore,
    private readonly session: SessionClientGenerated,
  ) {}

  // What the filters are made of, each the same object until a filter changes, so a view draws again only then.
  get filters(): readonly unknown[] {
    const { entries, rootFiles, graph } = this.store.state
    return [entries, rootFiles, graph.filter.relationships]
  }

  // The callouts of file the filters show.
  shownOf(file: SessionFileData): SourceCallout[] {
    return calloutsOf(file).filter(callout => this.shows(callout))
  }

  // The callouts of the file at path the filters show, read as the open file is read, with or without its rules. A
  // session that does not answer the file fails the read, which the callout asking for it shows.
  async in(path: string): Promise<SourceCallout[]> {
    const { rules, crossFile } = this.store.state.reads
    const file = fileAnswered(await this.session.file(path, rules, crossFile))
    return file ? this.shownOf(file) : []
  }

  private shows(callout: SourceCallout): boolean {
    const { entries, rootFiles, graph } = this.store.state
    const connector = CONNECTOR_OF[callout.kind]
    const connectors = graph.filter.relationships
    if (connector && connectors.length && !connectors.includes(connector)) return false
    const isOfAPractice = (rootFiles ?? []).some(entry => entry.path === callout.path && entry.fidelities.length > 0)
    return !isOfAPractice || entries.some(entry => entry.path === callout.path)
  }
}
