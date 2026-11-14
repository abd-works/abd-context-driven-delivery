import { FileCommentsClientGenerated, type FileCommentData } from '@cdd/space/session/file-comments'

import type { FilesPage } from './files-page'

export type CommentLines = { start: number; end: number }

const NO_CHAT = 'No chat opened this page, so the comment is kept, not sent: open the Files app from the chat bar to send comments.'

// What a person does with comments on the open file, each one file-comments operation on the session's comments,
// after which the open file is read again, so its markers show the state Python answered. Sending goes to the chat
// that opened the page; a chat that cannot take it leaves the comment not sent, and the toast says why.
export class FileCommentsActions {
  private readonly comments: FileCommentsClientGenerated

  constructor(private readonly page: FilesPage) {
    this.comments = FileCommentsClientGenerated.named(page.api, page.link.sessionFile)
  }

  private get path(): string {
    return this.page.state.file?.path ?? ''
  }

  // Enter finishes a comment: it is kept on the selected lines, then added to the chat's queue.
  async addAndSend(lines: CommentLines, text: string): Promise<void> {
    const path = this.path
    if (!path || !text.trim()) return
    let added: FileCommentData | undefined
    const kept = await this.page.attempt(`The comment on ${path} was not kept`, async () => {
      const answered = await this.comments.add(path, lines.start, lines.end, text.trim())
      added = answered?.comments.at(-1)
    })
    if (kept && added) await this.send(added.anchor)
  }

  async add(lines: CommentLines, text: string): Promise<void> {
    const path = this.path
    if (!path || !text.trim()) return
    await this.page.attempt(`The comment on ${path} was not kept`, () => this.comments.add(path, lines.start, lines.end, text.trim()))
  }

  async edit(anchor: string, text: string): Promise<boolean> {
    if (!text.trim()) return false
    return this.page.attempt(`The comment ${anchor} was not saved`, () => this.comments.edit(anchor, text.trim()))
  }

  async editAndSend(anchor: string, text: string): Promise<void> {
    if (await this.edit(anchor, text)) await this.send(anchor)
  }

  async remove(anchor: string): Promise<void> {
    await this.page.attempt(`The comment ${anchor} was not deleted`, () => this.comments.remove(anchor))
  }

  async send(anchor: string): Promise<void> {
    const chat = this.page.link.chat
    if (!chat) return this.page.toast(NO_CHAT)
    await this.page.attempt(`The comment ${anchor} was not sent`, () => this.comments.send(anchor, chat))
  }

  async sendOpen(): Promise<void> {
    const chat = this.page.link.chat
    if (!chat) return this.page.toast(NO_CHAT)
    await this.page.attempt('The open comments were not sent', () => this.comments.sendOpen(chat))
  }

  async clearProcessed(): Promise<void> {
    await this.page.attempt('The processed comments were not cleared', () => this.comments.clearProcessed())
  }
}
