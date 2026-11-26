import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import type { ChatBarDraw } from './chat-bar-view'
import { LIST_FRAME, repoListShiftOf, sessionListShiftOf } from './bar-columns'
import { MAIN_SESSION } from './chat-bar-client'
import { activateTicket, chooseSessionFolder, closeSession, createSession, openRepo, startBacklogItem } from './session-client'
import { cancelClose, chooseNewSessionFolder, losesWork, toggleBacklog, toggleBacklogParent, toggleLeaving } from './session-dialogs-client'
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
// The list and the boxes the Backlog opens share one row, its right edge under the line's end: the Backlog's items and a
// parent's child items stand beside the list rather than above it, so the chat's height holds them.
export function SessionListView($: EngineInterface, { Box, Button, Input, Text }: ElementTable, { chatBar, view, version, maxRows }: ChatBarDraw) {
  if (!view.isSessionListOpen || !chatBar.isMain) return null
  const boxes = backlogBoxesOf(chatBar, view, maxRows)
  const besideCells = boxes.reduce((cells, box) => cells + box.cells + LIST_FRAME + BOX_GAP, 0)
  return (
    <Box key="session-lists" flexDirection="row" alignItems="flex-end" gap={BOX_GAP} position="absolute" bottom={1} left={sessionListShiftOf(chatBar, version.label, sessionListCellsOf(chatBar) + besideCells)}>
      {boxes.map(box => BacklogBoxView($, { Box, Button, Text }, box, view.openBacklogParent))}
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

// One line of a box the Backlog opens: an item to start, after + N or - N when it is a parent.
type BacklogLine = { title: string; children: number }

// A box the Backlog opens beside the session list: the BACKLOG box, or the box of one parent's child items, headed by
// the parent's title. Its lines run down a column as far as the chat has rows above the line, then on in the next, so a
// long Backlog grows sideways and never past the chat's height.
type BacklogBox = { key: string; heading: string; columns: BacklogLine[][]; cells: number; rows: number }

function backlogBoxOf(key: string, heading: string, lines: BacklogLine[], maxRows: number): BacklogBox {
  const perColumn = Math.max(1, maxRows - LINE_ROWS - LIST_BORDER_ROWS - HEADING_ROWS)
  const columns: BacklogLine[][] = []
  for (let first = 0; first < lines.length; first += perColumn) columns.push(lines.slice(first, first + perColumn))
  const columnCells = columns.map(column => Math.max(...column.map(backlogLineCellsOf)))
  const cells = Math.max(heading.length, columnCells.reduce((sum, width) => sum + width, 0) + (columns.length - 1) * BOX_GAP)
  return { key, heading, columns, cells, rows: HEADING_ROWS + Math.min(perColumn, lines.length) + LIST_BORDER_ROWS }
}

// The boxes open beside the session list, left of it in the order drawn: the opened parent's child items, then the
// BACKLOG box; none while the Backlog is closed.
function backlogBoxesOf(chatBar: ChatBarDraw['chatBar'], view: ChatBarDraw['view'], maxRows: number): BacklogBox[] {
  if (!view.isBacklogOpen || !chatBar.backlogItems.length) return []
  const items = backlogBoxOf(BACKLOG_BOX, 'BACKLOG', chatBar.backlogItems.map(item => ({ title: item.title, children: item.children.length })), maxRows)
  const parent = chatBar.backlogItems.find(item => item.title === view.openBacklogParent && item.children.length)
  if (!parent) return [items]
  return [backlogBoxOf('session-backlog-children-box', shownTitleOf(parent.title), parent.children.map(child => ({ title: child.title, children: 0 })), maxRows), items]
}

const BACKLOG_BOX = 'session-backlog-box'
// The most cells a Backlog title takes in a box: a longer one is cut short and ends in an ellipsis, so a box stays
// inside the chat however long an item's title is. The whole title still starts the item.
const BACKLOG_TITLE_CELLS = 31
const shownTitleOf = (title: string): string => (title.length > BACKLOG_TITLE_CELLS ? `${title.slice(0, BACKLOG_TITLE_CELLS - 1)}…` : title)
const backlogStartLabelOf = (title: string): string => `${stageIconOf('Backlog')} ${shownTitleOf(title)}`
const backlogOpenLabelOf = (line: BacklogLine, isOpen: boolean): string => `${isOpen ? '-' : '+'} ${line.children}`
const backlogLineCellsOf = (line: BacklogLine): number => backlogStartLabelOf(line.title).length + (line.children ? backlogOpenLabelOf(line, false).length + 1 : 0)

// The Backlog's row closing the session list: its count, and which way it opens.
function backlogToggleLabelOf(chatBar: ChatBarDraw['chatBar'], isOpen: boolean): string {
  return `${isOpen ? '▸' : '◂'} ${stageIconOf('Backlog')} Backlog (${chatBar.backlogItems.length})`
}

function BacklogToggleView($: EngineInterface, { Button }: Pick<ElementTable, 'Button'>, chatBar: ChatBarDraw['chatBar'], view: ChatBarDraw['view']) {
  if (!chatBar.backlogItems.length) return null
  return <Button key="session-backlog-toggle" plain label={backlogToggleLabelOf(chatBar, view.isBacklogOpen)} onPress={() => toggleBacklog($)} />
}

// A box beside the session list: its heading, then its lines in columns. Each item is a whole button that starts it as
// the board moves an item out of the Backlog; a parent's + N opens its child items in a further box, its - N closes it.
function BacklogBoxView($: EngineInterface, { Box, Button, Text }: Pick<ElementTable, 'Box' | 'Button' | 'Text'>, box: BacklogBox, openParent: string) {
  const columnKey = box.key === BACKLOG_BOX ? 'session-backlog-column' : 'session-backlog-children-column'
  return (
    <Box key={box.key} flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      <Text key={`${box.key}-heading`} color={BRAND.muted}>{box.heading}</Text>
      <Box key={`${box.key}-columns`} flexDirection="row" gap={BOX_GAP}>
        {box.columns.map((column, place) => (
          <Box key={`${columnKey}-${place}`} flexDirection="column">
            {column.map(line => BacklogLineView($, { Box, Button }, line, line.title === openParent))}
          </Box>
        ))}
      </Box>
    </Box>
  )
}

function BacklogLineView($: EngineInterface, { Box, Button }: Pick<ElementTable, 'Box' | 'Button'>, line: BacklogLine, isOpen: boolean) {
  return (
    <Box key={`session-backlog-row-${line.title}`} flexDirection="row" gap={1}>
      {line.children ? <Button key={`session-backlog-open-${line.title}`} plain label={backlogOpenLabelOf(line, isOpen)} onPress={() => toggleBacklogParent($, line.title)} /> : null}
      <Button key={`session-backlog-start-${line.title}`} plain label={backlogStartLabelOf(line.title)} onPress={() => startBacklogItem($, line.title)} />
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
