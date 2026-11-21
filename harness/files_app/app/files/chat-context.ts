import type { SessionClientGenerated } from '@cdd/space/session/session'

import type { FilesNotices } from './files-notices'
import { reasonOf } from './reason'

// The context of the chat that opened the page: a file, or lines of it, the session puts in that chat's prompt box, to go
// with the person's next prompt, as Claude's own file viewer does.
export class ChatContext {
  constructor(
    private readonly session: SessionClientGenerated,
    private readonly chat: string,
    private readonly notices: FilesNotices,
  ) {}

  async add(path: string, lines?: { start: number; end: number }): Promise<void> {
    const name = path.split('/').at(-1) ?? path
    try {
      await this.session.addToChatContext(this.chat, path, lines?.start, lines?.end)
      this.notices.toast(`${name} added to the chat's context`)
    } catch (failure) {
      this.notices.fail(`${name} was not added to the chat's context: ${reasonOf(failure)}`, `Adding ${path} to the chat's context`)
    }
  }
}
