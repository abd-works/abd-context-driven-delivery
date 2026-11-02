import type { EngineInterface } from 'claude-code'

import type { ActivationJson } from '../../types'
import { ActionButtonView } from './action-button'
import { BRAND } from './brand'
import { cancelActivation, confirmActivation, toggleLeaving, toggleOpening } from './ticket-client'
import type { ViewContext } from './view-context'

const DIALOG_WIDTH = 60
// The dialog's edges, heading, buttons, and gaps, then each group's heading, facts, and options.
const DIALOG_FRAME_ROWS = 10
const LEAVE_GROUP_ROWS = 8
const OPEN_GROUP_ROWS = 7
const NONE_YET = 'none yet'

const checkbox = (isOn: boolean): string => (isOn ? '☑' : '☐')

function OptionView({ elements: { Button, Text } }: ViewContext, key: string, label: string, onPress: (() => unknown) | null) {
  return (
    <Button key={key} plain dimColor={!onPress} onPress={onPress ?? (() => undefined)}>
      <Text color={onPress ? BRAND.text : BRAND.muted}>{label}</Text>
    </Button>
  )
}

function SessionFactsView({ elements: { Box, Text } }: ViewContext, session: string, branch: string) {
  const fact = (name: string, value: string) => (
    <Box key={name} flexDirection="row" columnGap={1}>
      <Box key={`${name}-name`} width={8} flexShrink={0}>
        <Text mono size="footnote" color={BRAND.muted}>
          {name}
        </Text>
      </Box>
      <Text mono size="footnote" weight="semibold" color={BRAND.text}>
        {value}
      </Text>
    </Box>
  )
  return (
    <Box key="facts" flexDirection="column" borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised} paddingX={1}>
      {fact('session', session)}
      {fact('branch', branch)}
    </Box>
  )
}

function GroupHeadingView({ elements: { Text } }: ViewContext, heading: string) {
  return (
    <Text mono size="caption" weight="semibold" color={BRAND.muted}>
      {heading}
    </Text>
  )
}

function LeaveOptionsView($: EngineInterface, view: ViewContext, open: ActivationJson) {
  const { Box } = view.elements
  // Commit, push, and merge act on what is checked out, so with no branch of its own there is nothing to act on.
  const hasBranch = open.workspace.leaving_has_branch
  const options = [
    { key: 'commit', label: `Commit changes on ${open.leavingTitle}` },
    { key: 'push', label: `Push ${open.leavingTitle} to origin` },
    { key: 'merge', label: `Merge ${open.leavingTitle} into main` },
  ]
  return (
    <Box key="leave" flexDirection="column" flexShrink={0} rowGap={1}>
      {GroupHeadingView(view, open.isClosing ? 'CLOSE' : 'LEAVE')}
      {SessionFactsView(view, open.leavingTitle, hasBranch ? open.leavingTitle : NONE_YET)}
      {options.map(option => OptionView(view, `leave-${option.key}`, `${checkbox(open.leaving.includes(option.key))} ${option.label}`, hasBranch ? () => toggleLeaving($, option.key) : null))}
    </Box>
  )
}

function OpenOptionsView($: EngineInterface, view: ViewContext, open: ActivationJson) {
  const { Box } = view.elements
  const { has_branch: hasBranch, has_worktree: hasWorktree } = open.workspace
  return (
    <Box key="open" flexDirection="column" flexShrink={0} rowGap={1}>
      {GroupHeadingView(view, 'OPEN')}
      {SessionFactsView(view, open.title, hasBranch ? open.ticket : NONE_YET)}
      {OptionView(view, 'open-branch', hasBranch ? `${checkbox(false)} Branch ${open.ticket} already exists` : `${checkbox(open.opening.includes('branch'))} Create branch ${open.ticket}`, hasBranch ? null : () => toggleOpening($, 'branch'))}
      {OptionView(view, 'open-worktree', hasWorktree ? `${checkbox(false)} Worktree already exists` : `${checkbox(open.opening.includes('worktree'))} Create worktree for ${open.ticket}`, hasWorktree ? null : () => toggleOpening($, 'worktree'))}
    </Box>
  )
}

const headingOf = (open: ActivationJson): string => {
  if (open.isClosing) return `Close session ${open.title}`
  return open.leavingTitle ? `Switch from ${open.leavingTitle} to ${open.title}` : `Activate ${open.title}`
}

const dialogRowsOf = (open: ActivationJson): number => DIALOG_FRAME_ROWS + (open.leavingTitle ? LEAVE_GROUP_ROWS : 0) + (open.isClosing ? 0 : OPEN_GROUP_ROWS)

// Asked before the session changes, because leaving can commit, push, and merge work. Drawn last from the pane's root,
// because a Box paints over only what was drawn before it.
export function ActivationView($: EngineInterface, view: ViewContext, open: ActivationJson) {
  const { Box, Text } = view.elements
  const { bodyColumns, bodyRows } = view
  const width = Math.min(DIALOG_WIDTH, Math.max(bodyColumns - 2, 1))
  return (
    <Box
      key="activation"
      position="absolute"
      top={Math.max(Math.round((bodyRows - dialogRowsOf(open)) / 2), 0)}
      left={Math.max(Math.round((bodyColumns - width) / 2), 0)}
      width={width}
      flexDirection="column"
      rowGap={1}
      borderStyle="single"
      borderColor={BRAND.border}
      backgroundColor={BRAND.surface}
      padding={1}
    >
      <Text size="heading" weight="semibold" color={BRAND.text}>
        {headingOf(open)}
      </Text>
      {open.leavingTitle ? LeaveOptionsView($, view, open) : null}
      {open.isClosing ? null : OpenOptionsView($, view, open)}
      <Box key="activation-actions" flexDirection="row" justifyContent="flex-end" columnGap={1}>
        {ActionButtonView(view, 'cancel-activation', 'Cancel', () => cancelActivation($))}
        {ActionButtonView(view, 'confirm-activation', open.isClosing ? 'Close session' : 'Activate', () => confirmActivation($, open), true)}
      </Box>
    </Box>
  )
}
