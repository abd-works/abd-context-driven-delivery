import type { Monaco } from '@monaco-editor/react'

import type { SessionClientGenerated } from '@cdd/space/session/session'
import { FoldKeys, type FoldKey } from '@source-view/source-folding'

import type { FilesNotices } from './files-notices'

// The project's own fold shortcuts, written as VS Code's and Cursor's keybindings.json writes them, beside the project's
// other settings in its .context: `[{ "key": "ctrl+m ctrl+m", "command": "editor.toggleFold" }]`.
export const KEYBINDINGS_FILE = '.context/files-app-keybindings.json'

// Cursor's own fold shortcuts on Windows and Linux: VS Code's, with the chord leader Cursor moved off Ctrl+K, which it
// keeps for inline edit, to Ctrl+M (Cmd+R on a Mac, which Monaco's ctrl already reads as Cmd).
export const CURSOR_FOLD_KEYS: FoldKey[] = [
  { key: 'ctrl+m ctrl+0', command: 'editor.foldAll' },
  { key: 'ctrl+m ctrl+j', command: 'editor.unfoldAll' },
  { key: 'ctrl+m ctrl+[', command: 'editor.foldRecursively' },
  { key: 'ctrl+m ctrl+]', command: 'editor.unfoldRecursively' },
  { key: 'ctrl+m ctrl+l', command: 'editor.toggleFold' },
  { key: 'ctrl+shift+[', command: 'editor.fold' },
  { key: 'ctrl+shift+]', command: 'editor.unfold' },
  ...[1, 2, 3, 4, 5, 6, 7].map(level => ({ key: `ctrl+m ctrl+${level}`, command: `editor.foldLevel${level}` })),
]

const CURSOR = FoldKeys.from(JSON.stringify(CURSOR_FOLD_KEYS))

// Cursor's keys, each replaced by the key a keybindings file gives its command; a file that is not a list is left as
// written, for FoldKeys to say why it is not used.
function onCursorsKeys(written: string): string {
  try {
    const given: unknown = JSON.parse(written)
    if (!Array.isArray(given)) return written
    const commands = new Set(given.map(each => each?.command))
    return JSON.stringify([...CURSOR_FOLD_KEYS.filter(each => !commands.has(each.command)), ...given])
  } catch {
    return written
  }
}

// The fold shortcuts the Files app binds in its source views: Cursor's, each replaced by the key the project's
// keybindings file gives its command. A file not there keeps Cursor's quietly, and so does a file that is wrong, which
// the page says, naming the file and why. Read once as the page opens; bound in the Monaco the first source view loads.
export class FilesFoldKeys {
  private keys = CURSOR
  private readonly monacos: Monaco[] = []

  constructor(
    private readonly session: Pick<SessionClientGenerated, 'readFile'>,
    private readonly notices: FilesNotices,
  ) {}

  async read(): Promise<void> {
    try {
      const written = (await this.session.readFile(KEYBINDINGS_FILE))?.text ?? ''
      this.keys = written.trim() ? FoldKeys.from(onCursorsKeys(written)) : CURSOR
    } catch (failure) {
      this.keys = FoldKeys.fromFailure(failure instanceof Error ? failure.message : String(failure))
    }
    this.tellProblem(this.keys)
    if (this.keys.problem) this.keys = CURSOR
    this.monacos.forEach(monacoApi => this.bind(monacoApi))
  }

  // Binds the keys once in each Monaco, and again once the file is read, should a source view load Monaco first.
  bindIn(monacoApi: Monaco): void {
    if (this.monacos.includes(monacoApi)) return
    this.monacos.push(monacoApi)
    this.bind(monacoApi)
  }

  // A key Monaco has no code for keeps Cursor's, which the page says.
  private bind(monacoApi: Monaco): void {
    const bound = this.keys.bindIn(monacoApi)
    this.tellProblem(bound)
    if (bound.problem) CURSOR.bindIn(monacoApi)
  }

  private tellProblem(keys: FoldKeys): void {
    if (keys.problem) this.notices.toast(`${KEYBINDINGS_FILE} is not used, Cursor's fold keys are: ${keys.problem}`)
  }
}
