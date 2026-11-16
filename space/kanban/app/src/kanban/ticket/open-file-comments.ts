import type { FileCommentsClientGenerated } from '@cdd/space/session/file-comments'

import type { FilesPanelClient } from './files-panel-client'

// The comments on the file open in the files panel: each is added, removed, sent to the chat working on the ticket, and
// cleared once processed through the ticket's file comments, and the open file is read again after each, so the panel
// shows the comment's new state.
export class OpenFileComments {
  constructor(private readonly files: FilesPanelClient) {}

  async add(startLine: number, endLine: number, text: string): Promise<void> {
    const panel = this.files.panel
    if (!panel?.shown) return
    await panel.ticket.fileComments.add(panel.shown.path, startLine, endLine, text)
    await this.files.refreshShown()
  }

  async remove(anchor: string): Promise<void> {
    await this.files.panel?.ticket.fileComments.remove(anchor)
    await this.files.refreshShown()
  }

  // A comment goes to the chat working on the ticket; one the chat cannot take stays not sent, and the toast says why.
  async send(anchor: string): Promise<void> {
    await this.sentToChat((comments, chat) => comments.send(anchor, chat))
  }

  async sendOpen(): Promise<void> {
    await this.sentToChat((comments, chat) => comments.sendOpen(chat))
  }

  async clearProcessed(): Promise<void> {
    await this.files.panel?.ticket.fileComments.clearProcessed()
    await this.files.refreshShown()
  }

  // Every send names the chat working on the panel's ticket, then shows the open file as the chat left it.
  private async sentToChat(sending: (comments: FileCommentsClientGenerated, chat: string) => Promise<unknown>): Promise<void> {
    const panel = this.files.panel
    if (!panel) return
    await sending(panel.ticket.fileComments, panel.ticket.chat.id)
    await this.files.refreshShown()
  }
}
