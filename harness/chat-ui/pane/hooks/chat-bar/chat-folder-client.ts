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

// Moves this chat to the main checkout, before a worktree it may be working in is deleted.
export async function moveToMainCheckout($: EngineInterface): Promise<void> {
  const [current, main] = await Promise.all([$.session.root(), mainCheckoutOf($)])
  if (!main || sameFolder(current, main)) return
  await moveChatTo($, main)
}

// Claude Code's /cd moves the chat where the session offers it. The desktop app offers no /cd: there the chat's folder
// changes through the app's change_directory tool, which only the agent can call, so the agent is asked to.
async function moveChatTo($: EngineInterface, folder: string): Promise<boolean> {
  try {
    const hasCd = (await $.command.list()).some(command => command.name === 'cd')
    if (hasCd) await $.command.run({ command: 'cd', args: folder })
    else await askAgentToMove($, folder)
    return true
  } catch (failure) {
    $.ui.toast(`This chat did not move to ${folder}: ${reasonOf(failure)}`)
    return false
  }
}

async function askAgentToMove($: EngineInterface, folder: string): Promise<void> {
  const answer = await $.prompt.submit({ text: `Move this chat to ${folder}: call the change_directory tool with that path, and do nothing else.`, asUser: true })
  if (answer.drop !== undefined) throw new Error(answer.drop || 'the chat did not take the request')
}

// Moves this chat to the folder the active session's work is in, as /cd does when the person types it.
export async function followSession($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await checkChatFolder($, chatBar)
  const { expected, isElsewhere } = await currentChatFolder($)
  if (!isElsewhere) return
  if (await moveChatTo($, expected)) $.ui.toast(`Moving this chat to ${expected}${chatBar.sessionName ? `, for ${chatBar.sessionName}` : ''}`)
  await checkChatFolder($, chatBar)
}
