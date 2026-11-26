import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import type { ChatBarDraw } from './chat-bar-view'
import { LIST_FRAME, repoListShiftOf, sessionListShiftOf } from './bar-columns'
import { MAIN_SESSION } from './chat-bar-client'
import { activateTicket, chooseSessionFolder, closeSession, createSession, openRepo, startBacklogItem } from './session-client'
import { cancelClose, chooseNewSessionFolder, losesWork, showBacklogFrom, toggleBacklog, toggleLeaving } from './session-dialogs-client'
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
// The cells of the field that names a new session with its ◂ folder button, and of the repo list's fields, as drawn.
const NEW_SESSION_ROW_CELLS = 30
const REPO_FIELD_CELLS = 26

// Each open ticket's label, its stage icon and name, padded to the longest so the buttons share one width.
function sessionLabels(tickets: { name: string; stage: string }[]): { name: string; label: string }[] {
  const labels = tickets.map(ticket => ({ name: ticket.name, label: `${stageIconOf(ticket.stage)} ${ticket.name}` }))
  const width = Math.max(0, ...labels.map(({ label }) => label.length))
  return labels.map(({ name, label }) => ({ name, label: label.padEnd(width) }))
}

// In the main chat, the tickets a person can open, each after its stage's orange icon, a field to name a new one, and
// the Backlog, closed, saying how many items it holds. Main is listed first as the session this chat works on; opening a
// ticket finds its chat or starts one in its worktree. A ticket's own chat works only on that ticket, so it has no list.
// The list and the BACKLOG box share one row, its right edge under the line's end: the Backlog's items stand beside the
// list rather than above it, a page at a time, so the chat's height holds them.
export function SessionListView($: EngineInterface, { Box, Button, Input, Text }: ElementTable, { chatBar, view, version, maxRows }: ChatBarDraw) {
  if (!view.isSessionListOpen || !chatBar.isMain) return null
  const boxes = backlogBoxesOf(chatBar, view, maxRows)
  const besideCells = boxes.reduce((cells, box) => cells + box.cells + LIST_FRAME + BOX_GAP, 0)
  return (
    <Box key="session-lists" flexDirection="row" alignItems="flex-end" gap={BOX_GAP} position="absolute" bottom={1} left={sessionListShiftOf(chatBar, version.label, sessionListCellsOf(chatBar) + besideCells)}>
      {boxes.map(box => BacklogBoxView($, { Box, Button, Text }, box))}
      <Box key="session-list" flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
        <Box key="session-row-main" flexDirection="row" gap={1}>
          <Text color={BRAND.muted}>⌂</Text>
          <Text color={BRAND.accent}>{MAIN_SESSION}</Text>
        </Box>
        {TicketChoicesView($, { Box, Button, Input, Text }, { chatBar, view })}
        {BacklogToggleView($, { Button }, chatBar, view)}
      </Box>
    </Box>
  )
}

// How many rows the open session list takes, its border included: main, the tickets, the new session's field, the folder
// chosen for it, and the Backlog's row; or the tallest box the Backlog opened beside it; none while it is closed.
export function sessionListRowsOf({ chatBar, view, maxRows }: ChatBarDraw): number {
  if (!view.isSessionListOpen || !chatBar.isMain) return 0
  const tickets = chatBar.openTickets.length + 1 + (view.newSessionFolder ? 1 : 0)
  const listRows = 1 + tickets + (chatBar.backlogItems.length ? 1 : 0) + LIST_BORDER_ROWS
  return Math.max(listRows, ...backlogBoxesOf(chatBar, view, maxRows).map(box => box.rows))
}

// The widest line of the session list: the new session's field, a ticket, or the Backlog's row.
function sessionListCellsOf(chatBar: ChatBarDraw['chatBar']): number {
  return Math.max(NEW_SESSION_ROW_CELLS, backlogToggleLabelOf(chatBar, false).length, ...sessionLabels(chatBar.openTickets).map(({ label }) => label.length))
}

// Each ticket is a whole button, its stage icon in its label: a see-through Button laid over the name took no press in
// the desktop app, which left the list open and deaf. Every label is padded to the longest, so each button spans the
// list and a press anywhere on its line opens it. A ticket opens in its own worktree and chat, so only a git repository
// offers them. Before the new session's name, a folder button picks the folder of the repository it will work on, its
// arrow on the left and pointing the way the Backlog's does, so the two lines read alike.
function TicketChoicesView($: EngineInterface, elements: Pick<ElementTable, 'Box' | 'Button' | 'Input' | 'Text'>, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Input } = elements
  return [
    ...sessionLabels(chatBar.openTickets).map(({ name, label }) => <Button key={`session-${name}`} plain label={label} onPress={() => activateTicket($, name)} />),
    <Box key="new-session-row" flexDirection="row" gap={1}>
      <Button key="new-session-folder" plain label="◂ folder" onPress={() => chooseSessionFolder($, chatBar)} />
      <Input key="new-session" placeholder="New session name" value="" onSubmit={value => (value.trim() ? createSession($, value.trim()) : undefined)} />
    </Box>,
    NewSessionFolderView($, elements, chatBar.folder, view.newSessionFolder),
  ]
}

// The gap between the session list and each box the Backlog opens beside it.
const BOX_GAP = 1
// The line every box rests on, and a box's heading, which its items' rows leave room for.
const LINE_ROWS = 1
const HEADING_ROWS = 1

// The BACKLOG box the Backlog opens beside the session list, its lines the titles of the Backlog's own items; a parent
// is one line, and starts with its child items. It shows as many lines as the chat has rows above the line; with more, its heading says which
// of how many it shows, and its ▲ and ▼ show the page before and the page after, so a long Backlog never grows past the
// chat's height or its left edge. first is the place of the first line shown, and page how many it shows.
type BacklogBox = { key: string; heading: string; lines: string[]; total: number; first: number; page: number; cells: number; rows: number }

const PAGE_UP = '▲'
const PAGE_DOWN = '▼'
const pagedOf = (first: number, shown: number, total: number): string => `${first + 1}–${first + shown} of ${total}`
const isPaged = (box: BacklogBox): boolean => box.total > box.page

function backlogBoxOf(key: string, heading: string, lines: string[], maxRows: number, asked: number): BacklogBox {
  const page = Math.max(1, maxRows - LINE_ROWS - LIST_BORDER_ROWS - HEADING_ROWS)
  const first = Math.max(0, Math.min(asked, lines.length - page))
  const pagingCells = lines.length > page ? PAGE_UP.length + PAGE_DOWN.length + pagedOf(lines.length - 1, 1, lines.length).length + 3 * BOX_GAP : 0
  const cells = Math.max(heading.length + pagingCells, ...lines.map(backlogLineCellsOf))
  return { key, heading, lines: lines.slice(first, first + page), total: lines.length, first, page, cells, rows: HEADING_ROWS + Math.min(page, lines.length) + LIST_BORDER_ROWS }
}

// The box open beside the session list, left of it; none while the Backlog is closed.
function backlogBoxesOf(chatBar: ChatBarDraw['chatBar'], view: ChatBarDraw['view'], maxRows: number): BacklogBox[] {
  if (!view.isBacklogOpen || !chatBar.backlogItems.length) return []
  return [backlogBoxOf(BACKLOG_BOX, 'BACKLOG', chatBar.backlogItems.map(item => item.title), maxRows, view.backlogFirst)]
}

const BACKLOG_BOX = 'session-backlog-box'
// The most cells a Backlog title takes in a box: a longer one is cut short and ends in an ellipsis, so a box stays
// inside the chat however long an item's title is. The whole title still starts the item.
const BACKLOG_TITLE_CELLS = 31
const shownTitleOf = (title: string): string => (title.length > BACKLOG_TITLE_CELLS ? `${title.slice(0, BACKLOG_TITLE_CELLS - 1)}…` : title)
const backlogStartLabelOf = (title: string): string => `${stageIconOf('Backlog')} ${shownTitleOf(title)}`
const backlogLineCellsOf = (title: string): number => backlogStartLabelOf(title).length

// The Backlog's row closing the session list: its count, and which way it opens.
function backlogToggleLabelOf(chatBar: ChatBarDraw['chatBar'], isOpen: boolean): string {
  return `${isOpen ? '▸' : '◂'} ${stageIconOf('Backlog')} Backlog (${chatBar.backlogItems.length})`
}

function BacklogToggleView($: EngineInterface, { Button }: Pick<ElementTable, 'Button'>, chatBar: ChatBarDraw['chatBar'], view: ChatBarDraw['view']) {
  if (!chatBar.backlogItems.length) return null
  return <Button key="session-backlog-toggle" plain label={backlogToggleLabelOf(chatBar, view.isBacklogOpen)} onPress={() => toggleBacklog($)} />
}

// The box beside the session list: its heading, then its lines. Each item is a whole button that starts it as the board
// moves an item out of the Backlog. A box with more lines than it shows has ▲ and ▼ beside its heading, each a page's
// step, and says which lines it shows.
function BacklogBoxView($: EngineInterface, { Box, Button, Text }: Pick<ElementTable, 'Box' | 'Button' | 'Text'>, box: BacklogBox) {
  return (
    <Box key={box.key} flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      <Box key={`${box.key}-heading-row`} flexDirection="row" gap={BOX_GAP}>
        <Text key={`${box.key}-heading`} color={BRAND.muted}>{box.heading}</Text>
        {isPaged(box) ? <Button key={`${box.key}-up`} plain label={PAGE_UP} onPress={() => showBacklogFrom($, Math.max(0, box.first - box.page))} /> : null}
        {isPaged(box) ? <Button key={`${box.key}-down`} plain label={PAGE_DOWN} onPress={() => showBacklogFrom($, Math.min(box.total - box.page, box.first + box.page))} /> : null}
        {isPaged(box) ? <Text key={`${box.key}-paged`} color={BRAND.muted}>{pagedOf(box.first, box.lines.length, box.total)}</Text> : null}
      </Box>
      {box.lines.map(title => <Button key={`session-backlog-start-${title}`} plain label={backlogStartLabelOf(title)} onPress={() => startBacklogItem($, title)} />)}
    </Box>
  )
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
// name creates the repository, private.

// Each repository's label: whether it has CDD, its name, and its branch.
const repoLabelOf = (repo: { name: string; has_cdd: boolean; branch: string }): string =>
  `${repo.has_cdd ? '◆' : '◇'} ${repo.name}${repo.branch ? ` · ${repo.branch}` : ''}`

export function RepoListView($: EngineInterface, elements: ElementTable, { chatBar, view, version }: ChatBarDraw) {
  const { Box, Button, Input, Text } = elements
  if (!view.isRepoListOpen || !chatBar.isMain) return null
  const widest = Math.max(REPO_FIELD_CELLS, ...(view.repos ?? []).map(repo => repoLabelOf(repo).length))
  return (
    <Box key="repo-list" flexDirection="column" position="absolute" bottom={1} left={repoListShiftOf(chatBar, version.label, widest)} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
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

// The Ticket's warning and the files it means, shown while the choices made would delete the worktree or the branch
// without a commit, so the person sees what goes before pressing Close session.
function LosingWorkView({ Box, Text }: ElementTable, view: ChatBarDraw['view']) {
  if (!losesWork(view)) return null
  return (
    <Box key="close-warning" flexDirection="column">
      <Text color={BRAND.error}>{view.leaveWarning}</Text>
      {view.leaveUnsavedWork.map(file => (
        <Text key={`unsaved-${file}`} color={BRAND.text}>{`  • ${file}`}</Text>
      ))}
    </Box>
  )
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
      {LosingWorkView(elements, view)}
      <Box flexDirection="row" gap={1}>
        <Button key="close-cancel" label="Cancel" onPress={() => cancelClose($)} />
        <Button key="close-confirm" label="Close session" variant="primary" onPress={() => closeSession($, chatBar)} />
      </Box>
    </Box>
  )
}
