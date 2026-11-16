import type { ChatContext } from './chat-context'
import type { FileBrowser } from './file-browser'
import type { FilesStore } from './files-state'

// The menu a right-click on a file or folder shows where the person clicked: add it to the chat's context, or show it in
// the system's file browser. It keeps what it is on in the page's store, so the view draws it.
export class FileMenu {
  constructor(
    private readonly store: FilesStore,
    private readonly chatContext: ChatContext,
    private readonly fileBrowser: FileBrowser,
  ) {}

  // Shown for path with its top left corner where the person clicked, in pixels from the window's left and top.
  open(path: string, left: number, top: number): void {
    this.store.change(() => ({ menu: { path, x: left, y: top } }))
  }

  close(): void {
    this.store.change(() => ({ menu: null }))
  }

  // The file the menu is on, added whole to the chat's context.
  async addToContext(): Promise<void> {
    const path = this.closed()
    if (path) await this.chatContext.add(path)
  }

  // The file or folder the menu is on, shown in the system's file browser.
  async reveal(): Promise<void> {
    const path = this.closed()
    if (path) await this.fileBrowser.reveal(path)
  }

  // The path the menu was on, the menu closed.
  private closed(): string {
    const path = this.store.state.menu?.path ?? ''
    this.close()
    return path
  }
}
