import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { TipView } from '../shared/tip-view'
import type { ChatBarDraw } from './chat-bar-view'
import { repoListShiftOf, sessionListShiftOf } from './bar-columns'
import { MAIN_SESSION } from './chat-bar-client'
import { activateTicket, chooseFolder, chooseSessionFolder, closeSession, createSession, openFolder, openRepo } from './session-client'
import { cancelClose, chooseNewSessionFolder, toggleLeaving } from './session-dialogs-client'
import { stageIconOf } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// One choice of a dialog: a press turns it on or off, and its box shows which.
type Choice = { key: string; label: string; isChosen: boolean; onPress: () => unknown }

function ChoiceView({ Button }: ElementTable, choice: Choice) {
  return <Button key={choice.key} plain label={`${choice.isChosen ? '☑' : '☐'} ${choice.label}`} onPress={choice.onPress} />
}

// A dialog's group of choices, after its heading, such as LEAVE.
function ChoicesView(elements: ElementTable, heading: string, choices: Choice[]) {
  const { Box, Text } = elements
  return (
    <Box key={`choices-${heading}`} flexDirection="row" gap={1} flexWrap="wrap" alignItems="center">
      <Text color={BRAND.text}>{heading}</Text>
      {choices.map(choice => ChoiceView(elements, choice))}
    </Box>
  )
}

// Each choice the Ticket offers for leaving a session, by the word TicketCheckout.leave reads, as the dialog words it
// for the branch it acts on.
function leaveLabelOf(word: string, branch: string): string {
  const labels: Record<string, string> = {
    handoff: 'Create handoff',
    commit: 'commit',
    push: 'push',
    merge: 'merge into main',
    delete_branch: `delete branch ${branch} and close the session`,
    delete_worktree: 'delete worktree',
  }
  return labels[word] ?? word
}

function leavingChoices($: EngineInterface, prefix: string, view: ChatBarDraw['view']): Choice[] {
  return view.leaveChoices.map(word => ({ key: `${prefix}-${word}`, label: leaveLabelOf(word, view.leaveOwnBranch), isChosen: view.leaving.includes(word), onPress: () => toggleLeaving($, word) }))
}

// The LEAVE line names the session being left and the branch its work is on.
function leaveHeadingOf(session: string, branch: string): string {
  return `LEAVE ${session}${branch ? ` on ${branch}` : ''}`
}

// A list box's round border, a row above and below its lines.
const LIST_BORDER_ROWS = 2
// The cells of the field that names a new session with its ▸ folder button, and of the repo list's fields, as drawn.
const NEW_SESSION_ROW_CELLS = 30
const REPO_FIELD_CELLS = 26
// The folder row: ▸ Choose a folder… with the folder path's field beside it, as drawn.
const FOLDER_ROW_CELLS = 40

// Each open ticket's label, its stage icon and name, padded to the longest so the buttons share one width.
function sessionLabels(tickets: { name: string; stage: string }[]): { name: string; label: string }[] {
  const labels = tickets.map(ticket => ({ name: ticket.name, label: `${stageIconOf(ticket.stage)} ${ticket.name}` }))
  const width = Math.max(0, ...labels.map(({ label }) => label.length))
  return labels.map(({ name, label }) => ({ name, label: label.padEnd(width) }))
}

// In the main chat, the tickets a person can open, each after its stage's orange icon, and a field to name a new one,
// its left edge under the start of "main +", the button after the repository's name that opens it.
// Main is listed first as the session this chat works on; opening a ticket finds its chat or starts one in its worktree.
// A ticket's own chat works only on that ticket, so it has no list.
export function SessionListView($: EngineInterface, { Box, Button, Input, Text }: ElementTable, { chatBar, view, version }: ChatBarDraw) {
  if (!view.isSessionListOpen || !chatBar.isMain) return null
  const widest = Math.max(NEW_SESSION_ROW_CELLS, ...sessionLabels(chatBar.openTickets).map(({ label }) => label.length))
  return (
    <Box key="session-list" flexDirection="column" position="absolute" bottom={1} left={sessionListShiftOf(chatBar, version.label, widest)} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      <Box key="session-row-main" flexDirection="row" gap={1}>
        <Text color={BRAND.muted}>⌂</Text>
        <Text color={BRAND.accent}>{MAIN_SESSION}</Text>
      </Box>
      {chatBar.isClone ? TicketChoicesView($, { Box, Button, Input, Text }, { chatBar, view }) : <Text key="session-no-git" color={BRAND.muted}>No git here, so no ticket chats</Text>}
    </Box>
  )
}

// How many rows the open session list takes, its border included: main, the tickets, the new session's field, and the
// folder chosen for it; none while it is closed.
export function sessionListRowsOf({ chatBar, view }: ChatBarDraw): number {
  if (!view.isSessionListOpen || !chatBar.isMain) return 0
  const tickets = chatBar.isClone ? chatBar.openTickets.length + 1 + (view.newSessionFolder ? 1 : 0) : 1
  return 1 + tickets + LIST_BORDER_ROWS
}

// Each ticket is a whole button, its stage icon in its label: a see-through Button laid over the name took no press in
// the desktop app, which left the list open and deaf. Every label is padded to the longest, so each button spans the
// list and a press anywhere on its line opens it. A ticket opens in its own worktree and chat, so only a git repository
// offers them. Beside the new session's name, a folder button picks the folder of the repository it will work on.
function TicketChoicesView($: EngineInterface, elements: Pick<ElementTable, 'Box' | 'Button' | 'Input' | 'Text'>, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Input } = elements
  return [
    ...sessionLabels(chatBar.openTickets).map(({ name, label }) => <Button key={`session-${name}`} plain label={label} onPress={() => activateTicket($, name)} />),
    <Box key="new-session-row" flexDirection="row" gap={1}>
      <Input key="new-session" placeholder="New session name" value="" onSubmit={value => (value.trim() ? createSession($, value.trim()) : undefined)} />
      <Button key="new-session-folder" plain label="▸ folder" onPress={() => chooseSessionFolder($, chatBar)} />
    </Box>,
    NewSessionFolderView($, elements, chatBar.folder, view.newSessionFolder),
  ]
}

// The folder of the repository the new session will work on, from the repository's top, and a button to go back to
// the whole repository; nothing while none is chosen.
function NewSessionFolderView($: EngineInterface, { Box, Button, Text }: Pick<ElementTable, 'Box' | 'Button' | 'Text'>, repository: string, chosen: string) {
  if (!chosen) return null
  return (
    <Box key="new-session-folder-row" flexDirection="row" gap={1}>
      <Text color={BRAND.muted} wrap="truncate-start">in {folderFromTop(repository, chosen)}</Text>
      <Button key="new-session-folder-clear" plain label="×" onPress={() => chooseNewSessionFolder($, '')} />
    </Box>
  )
}

// A folder named from the repository's top, as the session will save it; one outside the repository in full, which
// Python then refuses when the session is created.
function folderFromTop(repository: string, folder: string): string {
  const slashed = (path: string): string => path.replace(/\\/g, '/').replace(/\/$/, '')
  const top = slashed(repository)
  const path = slashed(folder)
  if (path.toLowerCase() === top.toLowerCase()) return '(whole repository)'
  return path.toLowerCase().startsWith(`${top.toLowerCase()}/`) ? path.slice(top.length + 1) : path
}

// In the main chat, the repositories beside this one, opened from the repository's own button before "main +",
// alone, so the bar stays in view, its left edge under the start of that button. Opening one starts a top-level chat on it; a new
// name creates the repository, private. Folder Only (No Repo), above them, opens any folder as it is in a top-level
// chat, chosen with the system's folder picker or typed, and creates nothing there; its tip says when to choose it.
const FOLDER_ONLY_TIP = "Choose a path if you don't want to work with a repository and want to just work within your local file system"

// Each repository's label: whether it has CDD, its name, and its branch.
const repoLabelOf = (repo: { name: string; has_cdd: boolean; branch: string }): string =>
  `${repo.has_cdd ? '◆' : '◇'} ${repo.name}${repo.branch ? ` · ${repo.branch}` : ''}`

// Folder Only (No Repo): the system's folder picker, or a typed path, opens a folder as it is.
function FolderOnlyView($: EngineInterface, elements: ElementTable) {
  const { Box, Button, Input, Text } = elements
  return [
    <Box key="folder-heading-box">
      <Text key="folder-heading" color={BRAND.muted}>Folder Only (No Repo)</Text>
      {TipView(elements, FOLDER_ONLY_TIP, '', BRAND.muted)}
    </Box>,
    <Box key="repo-folder-row" flexDirection="row" gap={1}>
      <Button key="repo-folder-choose" plain label="▸ Choose a folder…" onPress={() => chooseFolder($)} />
      <Input key="repo-folder-path" placeholder="Folder path" value="" onSubmit={value => (value.trim() ? openFolder($, value.trim()) : undefined)} />
    </Box>,
  ]
}

export function RepoListView($: EngineInterface, elements: ElementTable, { chatBar, view, version }: ChatBarDraw) {
  const { Box, Button, Input, Text } = elements
  if (!view.isRepoListOpen || !chatBar.isMain) return null
  const widest = Math.max(REPO_FIELD_CELLS, FOLDER_ROW_CELLS, ...(view.repos ?? []).map(repo => repoLabelOf(repo).length))
  return (
    <Box key="repo-list" flexDirection="column" position="absolute" bottom={1} left={repoListShiftOf(chatBar, version.label, widest)} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {FolderOnlyView($, elements)}
      <Text key="repos-heading" color={BRAND.muted}>REPOS</Text>
      {/* A chat bar whose view was saved before repos existed has none. Each repository is a whole button: a
          see-through one laid over its name took no press. */}
      {(view.repos ?? []).map(repo => (
        <Button
          key={`repo-${repo.name}`}
          plain
          label={repoLabelOf(repo)}
          onPress={() => openRepo($, repo.name)}
        />
      ))}
      <Input key="new-repo" placeholder="New repo name (private)" value="" onSubmit={value => (value.trim() ? openRepo($, value.trim()) : undefined)} />
    </Box>
  )
}

// How many rows the open repo list takes, its border included: the folder heading, the folder row, the REPOS heading,
// each repository, and the new repository's field; none while it is closed.
export function repoListRowsOf({ chatBar, view }: ChatBarDraw): number {
  if (!view.isRepoListOpen || !chatBar.isMain) return 0
  return 3 + (view.repos ?? []).length + 1 + LIST_BORDER_ROWS
}

// Closing offers what ticket.close_choices answers: a handoff always, and a commit and a push of the branch the
// session's work is on while it is checked out, named beside each.
export function CloseView($: EngineInterface, elements: ElementTable, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Text } = elements
  if (!view.closing) return null
  const { branch } = view.closing
  const choices = leavingChoices($, 'close', view)
  return (
    <Box key="close" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.error} backgroundColor={BRAND.errorWash}>
      <Text weight="semibold" color={BRAND.text}>{`Close session ${chatBar.title}`}</Text>
      {ChoicesView(elements, leaveHeadingOf(chatBar.sessionName, view.leaveBranch), choices)}
      {branch ? null : <Text color={BRAND.muted}>Nothing checked out is this session's, so nothing is committed.</Text>}
      <Box flexDirection="row" gap={1}>
        <Button key="close-cancel" label="Cancel" onPress={() => cancelClose($)} />
        <Button key="close-confirm" label="Close session" variant="primary" onPress={() => closeSession($, chatBar)} />
      </Box>
    </Box>
  )
}
