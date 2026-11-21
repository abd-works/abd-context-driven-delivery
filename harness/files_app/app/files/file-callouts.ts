import type { SessionClientGenerated, SessionFileData } from '@cdd/space/session/session'
import { nodeFilter } from '@graph-app/filter/filter-selection'
import type { SourceCallout } from '@source-view/source-callouts'

import type { FilesStore } from './files-state'
import { calloutsOf, fileAnswered } from './source-of-file'

// The file view's filters as the page sends them with each read of a file: the files its stages, practices and formats
// list, none until the session's files are read, and the graph view's node filter as the session's graph takes it.
export type FileViewFilters = { paths: string[] | null; nodeFilter: Record<string, unknown> }

// The files a file view shows, read through the session with the file view's filters (session.file), in the rendered
// view and the source view alike. Which callouts a file holds for those filters is the session's answer, decided in
// Python by the filter that narrows the graph view's trees: the page sends the filters, draws the callouts answered,
// and reads the open files again when a filter changes. It keeps no rule of its own.
export class FileCallouts {
  constructor(
    private readonly store: FilesStore,
    private readonly session: SessionClientGenerated,
  ) {}

  // The filters sent with a read: the files the page lists and the node filter the person chose in the graph view.
  get filters(): FileViewFilters {
    const { entries, rootFiles, graph } = this.store.state
    return { paths: rootFiles ? entries.map(entry => entry.path) : null, nodeFilter: nodeFilter(graph.filter) }
  }

  // What a file was read for: the same text until a filter changes, so the page reads its open files again only then.
  get readFor(): string {
    return JSON.stringify(this.filters)
  }

  // The file at path as the session answers it for the filters, with its own rules, the working copy's, or neither. A
  // session that does not answer the file fails the read.
  async file(path: string, rules: boolean, crossFile: boolean): Promise<SessionFileData | null> {
    const { paths, nodeFilter: chosen } = this.filters
    return fileAnswered(await this.session.file(path, rules, crossFile, false, paths, chosen))
  }

  // The callouts of the file at path, read as the open file is read, which a section opened in place shows on its lines.
  async in(path: string): Promise<SourceCallout[]> {
    const { rules, crossFile } = this.store.state.reads
    const file = await this.file(path, rules, crossFile)
    return file ? calloutsOf(file) : []
  }
}
