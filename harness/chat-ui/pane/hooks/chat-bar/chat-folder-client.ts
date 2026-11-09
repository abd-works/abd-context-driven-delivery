import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ChatFolderJson } from '../../types'
import { reasonOf } from '../shared/failure'
import type { ChatBarClient } from './chat-bar-client'

// Where this chat works against where the active session's work is: the ticket's own worktree, else the repository's
// main checkout, where activating it checked its branch out. A switch made in the chat bar moves the chat there with
// Claude Code's own /cd; one made elsewhere shows in the band until the person moves it.
const chatFolder = atom({ plugin: 'cdd-board', key: 'chatFolder' } as const, { current: '', expected: '' } as ChatFolderJson)

// Windows names one folder with either slash and any case, so a folder is compared in one spelling.
const spelled = (folder: string): string => folder.split('\\').join('/').replace(/\/+$/, '').toLowerCase()
const sameFolder = (one: string, other: string): boolean => spelled(one) === spelled(other)

// Atom chatFolder, declared in pane/types/index.d.ts and kept in this file.
export async function currentChatFolder($: EngineInterface): Promise<ChatFolderJson & { isElsewhere: boolean }> {
  const folder = await read($, chatFolder)
  return { ...folder, isElsewhere: Boolean(folder.current && folder.expected && !sameFolder(folder.current, folder.expected)) }
}

// The folder holding a .git folder git names, in git's own spelling.
const spelledAsGiven = (gitFolder: string): string => gitFolder.split('\\').join('/').replace(/\/\.git$/, '')

// The repository's main checkout, which every worktree shares: the folder holding its .git.
async function mainCheckoutOf($: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'])
  return exitCode === 0 ? spelledAsGiven(stdout.trim()) : ''
}

// The folder the active session's work is in: its ticket's worktree, else the main checkout.
async function workFolderOf($: EngineInterface, chatBar: ChatBarClient): Promise<string> {
  return chatBar.worktree || (await mainCheckoutOf($))
}

// Reads where the chat is and where the active session's work is, so the band can say when they differ.
export async function checkChatFolder($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const [current, expected] = await Promise.all([$.session.root(), workFolderOf($, chatBar)])
  await update($, chatFolder, () => ({ current, expected }))
}

// Moves this chat to the folder the active session's work is in, as /cd does when the person types it.
export async function followSession($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await checkChatFolder($, chatBar)
  const { expected, isElsewhere } = await currentChatFolder($)
  if (!isElsewhere) return
  try {
    await $.command.run({ command: 'cd', args: expected })
    $.ui.toast(`This chat now works in ${expected}${chatBar.sessionName ? `, on ${chatBar.sessionName}` : ''}`)
  } catch (failure) {
    $.ui.toast(`This chat did not move to ${expected}: ${reasonOf(failure)}. Run /cd ${expected}`)
  }
  await checkChatFolder($, chatBar)
}
