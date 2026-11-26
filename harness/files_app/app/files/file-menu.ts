import { PracticeSessionOutputClientGenerated, type PracticeSessionOutputData } from '@cdd/space/session/practices/practice-session-output'

import type { FileBrowser } from './file-browser'
import type { FilesPage } from './files-page'
import { reasonOf } from './reason'

// The menu a right-click on a file or folder shows where the person clicked: add it to the chat's context, show it in the
// system's file browser, delete it once the person confirms, validate it, display the rules broken in it, or add it to a
// practice as a root. Each choice is one call to the session, which holds every rule of it (what may be deleted, what a
// root is); the menu keeps what it is on in the page's store, so the view draws it.
export class FileMenu {
  constructor(
    private readonly page: FilesPage,
    private readonly fileBrowser: FileBrowser,
  ) {}

  // Shown for path with its top left corner where the person clicked, in pixels from the window's left and top.
  open(path: string, left: number, top: number): void {
    this.page.store.change(() => ({ menu: { path, x: left, y: top } }))
  }

  close(): void {
    this.page.store.change(() => ({ menu: null }))
  }

  // The file the menu is on, added whole to the chat's context.
  async addToContext(): Promise<void> {
    const path = this.closed()
    if (path) await this.page.chatContext.add(path)
  }

  // The file or folder the menu is on, shown in the system's file browser.
  async reveal(): Promise<void> {
    const path = this.closed()
    if (path) await this.fileBrowser.reveal(path)
  }

  // Delete asks first, in the menu, since nothing is kept to undo it.
  askToDelete(): void {
    this.page.store.change(({ menu }) => ({ menu: menu && { ...menu, isConfirmingDelete: true } }))
  }

  // What the menu asks while it waits for the person to confirm a delete; empty otherwise.
  get confirmation(): string {
    const menu = this.page.store.state.menu
    return menu?.isConfirmingDelete ? `Delete ${menu.path}? This cannot be undone.` : ''
  }

  // The file or folder the person confirmed, deleted by the session, and the files listed again without it.
  async confirmDelete(): Promise<void> {
    const path = this.closed()
    if (!path) return
    try {
      await this.page.session.deleteFile(path)
      this.page.notices.toast(`Deleted ${path}`)
    } catch (failure) {
      this.page.notices.fail(`${path} was not deleted: ${reasonOf(failure)}`, `Deleting ${path} from the Files app's file menu, calling session.delete_file`)
    }
    await this.page.forget(path)
  }

  // The file or folder validated by each fidelity the session shows that declares it, or a file in it.
  async validate(): Promise<void> {
    const path = this.closed()
    if (!path) return
    try {
      const checked = (await this.page.session.checkChangedArtifact(path))?.checked ?? []
      this.page.notices.toast(checked.length ? `Validated ${path} with ${checked.join(', ')}` : `No fidelity the session shows declares ${path}`)
    } catch (failure) {
      this.page.notices.fail(`${path} was not validated: ${reasonOf(failure)}`, `Validating ${path} from the Files app's file menu, calling session.check_changed_artifact`)
    }
  }

  // The rules the latest reports find broken in the file or folder, displayed until the person closes them.
  async showViolations(): Promise<void> {
    const path = this.closed()
    if (!path) return
    try {
      const report = await this.page.ticket.violationsOf(path)
      if (report) this.page.store.change(() => ({ violations: { path, report } }))
    } catch (failure) {
      this.page.notices.fail(`The violations of ${path} did not read: ${reasonOf(failure)}`, `Displaying the violations of ${path}, calling ticket.violations_of`)
    }
  }

  // The file or folder added as a root of every fidelity of practice, kept in session.json; the page then shows it at
  // the top of the folder tree, as the practice's answer says.
  async addToPractice(practice: PracticeSessionOutputData): Promise<void> {
    const path = this.closed()
    if (!path) return
    try {
      const added = await new PracticeSessionOutputClientGenerated(this.page.api, practice).addRoot(path)
      if (added) this.page.store.change(({ practices }) => ({ practices: practices.map(each => (each === practice ? added.toJSON() : each)) }))
      this.page.notices.toast(`${path} added to ${practice.short_name}`)
    } catch (failure) {
      this.page.notices.fail(`${path} was not added to ${practice.short_name}: ${reasonOf(failure)}`, `Adding ${path} to ${practice.short_name} from the Files app's file menu, calling practice-session-output.add_root`)
    }
  }

  // The path the menu was on, the menu closed.
  private closed(): string {
    const path = this.page.store.state.menu?.path ?? ''
    this.close()
    return path
  }
}
