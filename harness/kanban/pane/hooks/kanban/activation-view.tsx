import type { EngineInterface } from 'claude-code'

import type { ActivationJson } from '../../types'
import { ActionButtonView } from './action-button'
import { BRAND } from './brand'
import { cancelActivation, confirmActivation, toggleLeaving, toggleOpening } from './ticket-client'
import type { ViewContext } from './view-context'

const checkbox = (isOn: boolean): string => (isOn ? '[x]' : '[ ]')

function LeaveOptionsView($: EngineInterface, view: ViewContext, open: ActivationJson) {
  const { Box, Text } = view.elements
  const options = [
    { key: 'commit', label: `Commit changes on ${open.leavingTitle}` },
    { key: 'push', label: `Push ${open.leavingTitle} to origin` },
    { key: 'merge', label: `Merge ${open.leavingTitle} into main` },
  ]
  return (
    <Box key="leave" flexDirection="column">
      <Text color={BRAND.muted}>{open.isClosing ? 'CLOSE' : 'LEAVE'}</Text>
      {options.map(option =>
        ActionButtonView(view, `leave-${option.key}`, `${checkbox(open.leaving.includes(option.key))} ${option.label}`, () => toggleLeaving($, option.key)),
      )}
    </Box>
  )
}

function OpenOptionsView($: EngineInterface, view: ViewContext, open: ActivationJson) {
  const { Box, Text } = view.elements
  const { has_branch: hasBranch, has_worktree: hasWorktree } = open.workspace
  return (
    <Box key="open" flexDirection="column">
      <Text color={BRAND.muted}>OPEN</Text>
      {ActionButtonView(view, 'open-branch', hasBranch ? `Branch ${open.ticket} already exists` : `${checkbox(open.opening.includes('branch'))} Create branch ${open.ticket}`, hasBranch ? null : () => toggleOpening($, 'branch'))}
      {ActionButtonView(view, 'open-worktree', hasWorktree ? 'Worktree already exists' : `${checkbox(open.opening.includes('worktree'))} Create worktree for ${open.ticket}`, hasWorktree ? null : () => toggleOpening($, 'worktree'))}
    </Box>
  )
}

const headingOf = (open: ActivationJson): string => {
  if (open.isClosing) return `Close session ${open.title}`
  return open.leavingTitle ? `Switch from ${open.leavingTitle} to ${open.title}` : `Activate ${open.title}`
}

// Asked before the session changes, because leaving can commit, push, and merge work.
export function ActivationView($: EngineInterface, view: ViewContext, open: ActivationJson) {
  const { Box, Text } = view.elements
  return (
    <Box key="activation" flexDirection="column" gap={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised} paddingX={1}>
      <Text bold color={BRAND.text}>
        {headingOf(open)}
      </Text>
      {open.leavingTitle ? LeaveOptionsView($, view, open) : null}
      {open.isClosing ? null : OpenOptionsView($, view, open)}
      <Box key="activation-actions" flexDirection="row" columnGap={1}>
        {ActionButtonView(view, 'confirm-activation', open.isClosing ? 'Close session' : 'Activate', () => confirmActivation($, open), true)}
        {ActionButtonView(view, 'cancel-activation', 'Cancel', () => cancelActivation($))}
      </Box>
    </Box>
  )
}
