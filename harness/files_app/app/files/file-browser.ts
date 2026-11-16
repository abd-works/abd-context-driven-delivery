import type { CddApi } from '@cdd/cdd-shared'

import type { FilesNotices } from './files-notices'
import { REVEAL_PATH } from './files-paths'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The system's file browser on this machine, which the Files server starts: Explorer, Finder, or the desktop's file
// manager.
export class FileBrowser {
  constructor(
    private readonly api: CddApi,
    private readonly notices: FilesNotices,
  ) {}

  // Shows path, a file or folder named from the project, in the file browser.
  async reveal(path: string): Promise<void> {
    try {
      await this.api.post(REVEAL_PATH, { path })
    } catch (failure) {
      this.notices.fail(`${path} did not open in the file browser: ${reasonOf(failure)}`, `Opening ${path} in the file browser`)
    }
  }
}
