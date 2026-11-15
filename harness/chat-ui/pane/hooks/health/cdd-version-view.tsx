import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { TipView } from '../shared/tip-view'
import type { CddVersionClient } from './cdd-version-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

export type VersionActions = { askToUpdate: () => unknown; cancelUpdate: () => unknown; updateToLatest: () => unknown }

// The version badge at the end of the line: the version in its standing's colour, how an update is going (or else its
// summary) on hover, and a press that asks whether to update and reinstall.
export function VersionBadgeView(elements: ElementTable, version: CddVersionClient, actions: VersionActions) {
  const { Box } = elements
  return (
    <Box key="cdd-version" flexDirection="row" gap={1}>
      {GlyphButtonView(elements, 'cdd-version-badge', version.label, version.colour, actions.askToUpdate)}
      {TipView(elements, version.tip, '', BRAND.muted)}
    </Box>
  )
}

// Asked from the badge: update to the latest on origin main and reinstall, or leave it.
export function UpdateDialogView(elements: ElementTable, version: CddVersionClient, actions: VersionActions) {
  const { Box, Button, Text } = elements
  if (!version.isAsking) return null
  const target = version.latest && version.latest !== version.label ? `${version.latest}, the latest on origin main` : 'the latest on origin main'
  return (
    <Box key="update-dialog" flexDirection="column" paddingX={1} borderStyle="single" borderColor={version.colour} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Update CDD ${version.label} to ${target} and reinstall?`}</Text>
      <Text color={BRAND.muted}>Pulls origin main, stops every app and the hook server, restarts the cdd server, and installs every toolset. Other chats lose cdd for a few seconds.</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="update-cancel" label="Cancel" onPress={actions.cancelUpdate} />
        <Button key="update-confirm" label="Update and reinstall" variant="primary" onPress={actions.updateToLatest} />
      </Box>
    </Box>
  )
}
