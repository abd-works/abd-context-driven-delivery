import type { SessionFileData } from '@cdd/space/session/session'
import type { SourceCallout } from '@source-view/source-callouts'

import type { FileCallouts } from './file-callouts'
import type { FilesNotices } from './files-notices'
import type { FilesStore } from './files-state'
import { reasonOf } from './reason'

// Whether a Go to file follows a link: a section a markdown link names, which opens beside the file it was followed from.
// A call, class or example a callout shows is no link, so it opens in its own file as the graph view opens a node.
export const followsALink = (callout: SourceCallout): boolean => callout.kind === 'section' || Boolean(callout.link)

const anchorOfLink = (link: string): string => link.split('#')[1] ?? ''

// The file a link opened beside the open file, so a person reads a scenario and the class a term links to side by side.
// There is only one: a link followed from either file replaces it, and the open file stays. It is read as the open file
// is read, with the file view's filters and the reads chosen, and again whenever the open file is.
export class LinkedFile {
  constructor(
    private readonly store: FilesStore,
    private readonly callouts: FileCallouts,
    private readonly notices: FilesNotices,
  ) {}

  // Opens the file the link of callout names beside the open file, at the heading it names.
  async open(callout: SourceCallout): Promise<void> {
    const anchor = anchorOfLink(callout.link ?? '')
    const lines = anchor ? [{ start: callout.startLine, end: callout.endLine }] : []
    this.store.change(() => ({ linked: { path: callout.path, anchor, lines, file: null } }))
    await this.readAgain()
  }

  close(): void {
    this.store.change(() => ({ linked: null }))
  }

  // The linked file read again through the session, while it is still the one beside the open file.
  async readAgain(): Promise<void> {
    const path = this.store.state.linked?.path
    if (!path) return
    const { rules, crossFile } = this.store.state.reads
    try {
      const read = await this.callouts.file(path, rules, crossFile)
      const file = read && !rules && !crossFile ? { ...read, violations: [] } : read
      this.shown(path, file)
    } catch (failure) {
      this.notices.fail(`The Files app did not open ${path}: ${reasonOf(failure)}`, `Opening ${path} beside the open file, calling session.file`, { kind: 'file_display' })
    }
  }

  private shown(path: string, file: SessionFileData | null): void {
    this.store.change(({ linked }) => (linked?.path === path ? { linked: { ...linked, file } } : {}))
  }
}
