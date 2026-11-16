import type { Monaco } from '@monaco-editor/react'

import type { SessionClientGenerated } from '@cdd/space/session/session'
import { FoldKeys } from '@source-view/source-folding'

import type { FilesNotices } from './files-notices'

// The project's own fold shortcuts, written as VS Code's and Cursor's keybindings.json writes them, beside the project's
// other settings in its .context: `[{ "key": "ctrl+m ctrl+m", "command": "editor.toggleFold" }]`.
export const KEYBINDINGS_FILE = '.context/files-app-keybindings.json'

// The fold shortcuts the Files app binds in its source views: VS Code's, each replaced by the key the project's
// keybindings file gives its command. A file not there keeps VS Code's quietly, and so does a file that is wrong, which
// the page says, naming the file and why. Read once as the page opens; bound in the Monaco the first source view loads.
export class FilesFoldKeys {
  private keys = FoldKeys.VS_CODE
  private readonly monacos: Monaco[] = []

  constructor(
    private readonly session: Pick<SessionClientGenerated, 'readFile'>,
    private readonly notices: FilesNotices,
  ) {}

  async read(): Promise<void> {
    try {
      const written = (await this.session.readFile(KEYBINDINGS_FILE))?.text ?? ''
      this.keys = written.trim() ? FoldKeys.from(written) : FoldKeys.VS_CODE
    } catch (failure) {
      this.keys = FoldKeys.fromFailure(failure instanceof Error ? failure.message : String(failure))
    }
    this.tellProblem(this.keys)
    this.monacos.forEach(monacoApi => this.bind(monacoApi))
  }

  // Binds the keys once in each Monaco, and again once the file is read, should a source view load Monaco first.
  bindIn(monacoApi: Monaco): void {
    if (this.monacos.includes(monacoApi)) return
    this.monacos.push(monacoApi)
    this.bind(monacoApi)
  }

  // A key Monaco has no code for keeps VS Code's, which the page says.
  private bind(monacoApi: Monaco): void {
    this.tellProblem(this.keys.bindIn(monacoApi))
  }

  private tellProblem(keys: FoldKeys): void {
    if (keys.problem) this.notices.toast(`${KEYBINDINGS_FILE} is not used, VS Code's fold keys are: ${keys.problem}`)
  }
}
