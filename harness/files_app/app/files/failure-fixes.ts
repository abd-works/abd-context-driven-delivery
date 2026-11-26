import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated } from '@cdd/harness/chat/chat'
import type { SessionFileData } from '@cdd/space/session/session'
import { FailureClientGenerated, type FailureData } from '@cdd/tools/error_display/failure'

import type { FilesStore } from './files-state'
import { reasonOf } from './reason'

// The kinds of failure Python knows the common causes of (tools/error_display FailureKind), by the names
// failure.describe takes; a failure of none of these names no kind.
export type FailureKindName = '' | 'file_display' | 'missing_link' | 'graph_view' | 'render' | 'generate' | 'session_roots'

// A failure the page shows with its Fix button: what failed, the context it failed in and its kind, as the page met it;
// once Fix is pressed, Python's description of it, with the most common causes of its kind and the command sent to the
// chat; and how far its fix has come, with why it did not get there.
export type ShownFailure = {
  failure: string
  context: string
  kind: FailureKindName
  // Whether the page's problem line already says what failed, so the band does not say it a second time.
  isOnProblemLine: boolean
  described: FailureData | null
  fix: 'not_asked' | 'asking' | 'sent' | 'not_sent'
  note: string
}

const NO_CHAT = 'No chat opened this page, so nothing was sent: copy the command into a chat to have it fixed.'

// The failures the page shows until a person dismisses them, each with Fix. Fix asks Python for the failure's most
// common causes (failure.describe), shows them, and sends the chat that opened the page the command Python answered
// with, which has the chat fix the failure with those causes to check first. The page decides none of it.
export class FailureFixes {
  // The failures a person took off the page, which a later read of the same file does not bring back.
  private readonly dismissed = new Set<string>()

  constructor(
    private readonly store: FilesStore,
    private readonly api: CddApi,
    private readonly chat: string,
  ) {}

  // A failure already shown is not shown twice, however often the page meets it again, and one dismissed stays off.
  show(failure: string, context: string, kind: FailureKindName = '', isOnProblemLine = false): void {
    if (this.dismissed.has(failure) || this.store.state.failures.some(shown => shown.failure === failure)) return
    this.store.change(state => ({ failures: [...state.failures, { failure, context, kind, isOnProblemLine, described: null, fix: 'not_asked', note: '' }] }))
  }

  // The links of the open file that lead to a file or a heading that is not there, as one failure, which says each;
  // none while every link leads somewhere. What is missing is the session's answer (session.file callouts), so a read
  // of the file with other filters replaces what the band said of it before.
  showMissingLinksOf(file: SessionFileData): void {
    const context = `Showing ${file.path} in the Files app, calling session.file`
    const missing = file.callouts.map(callout => callout.missing).filter(Boolean)
    const links = missing.length === 1 ? 'a link that leads nowhere' : `${missing.length} links that lead nowhere`
    const failure = `${file.path} has ${links}: ${missing.join('; ')}`
    const isSaidBefore = (shown: ShownFailure) => shown.kind === 'missing_link' && shown.context === context && shown.failure !== failure
    if (this.store.state.failures.some(isSaidBefore)) this.store.change(state => ({ failures: state.failures.filter(shown => !isSaidBefore(shown)) }))
    if (missing.length) this.show(failure, context, 'missing_link')
  }

  dismiss(failure: string): void {
    this.dismissed.add(failure)
    this.store.change(state => ({ failures: state.failures.filter(shown => shown.failure !== failure) }))
  }

  // A second press while the first is on its way sends nothing more.
  async fix(failure: string): Promise<void> {
    const shown = this.store.state.failures.find(each => each.failure === failure)
    if (!shown || shown.fix === 'asking') return
    this.changed(failure, { fix: 'asking', note: '' })
    try {
      const described = await FailureClientGenerated.describe(this.api, shown.failure, shown.context, shown.kind)
      if (!described) throw new Error('failure.describe answered nothing')
      this.changed(failure, { described })
      if (!this.chat) return this.changed(failure, { fix: 'not_sent', note: NO_CHAT })
      await ChatClientGenerated.named(this.api, this.chat).send('command', described.fix_command)
      this.changed(failure, { fix: 'sent', note: 'Sent to the chat that opened this page, which fixes it with these causes to check first.' })
    } catch (reason) {
      this.changed(failure, { fix: 'not_sent', note: `The fix did not reach the chat: ${reasonOf(reason)}` })
    }
  }

  private changed(failure: string, change: Partial<ShownFailure>): void {
    this.store.change(state => ({ failures: state.failures.map(shown => (shown.failure === failure ? { ...shown, ...change } : shown)) }))
  }
}
