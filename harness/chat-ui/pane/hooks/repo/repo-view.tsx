import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { TipView } from '../shared/tip-view'
import type { RepoClient } from './repo-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

export type PushActions = { pushWork: () => unknown; ask: () => unknown; cancel: () => unknown; pushToMain: () => unknown }

const DOING: Record<string, string> = { running: 'pushing…', failed: 'not pushed' }

// Push and Push & merge to origin/main, as icons among the session's buttons, with pushing… or not pushed while one runs or after one fails.
export function PushButtonsView(elements: ElementTable, repo: RepoClient, actions: PushActions) {
  const { Box, Text } = elements
  const doing = DOING[repo.state]
  return (
    <Box key="push-buttons" flexDirection="row" gap={1}>
      <Box key="push-work-box">
        {GlyphButtonView(elements, 'push-work', '⤴', BRAND.muted, actions.pushWork)}
        {TipView(elements, 'push', '', BRAND.muted)}
      </Box>
      <Box key="push-to-main-box">
        {GlyphButtonView(elements, 'push-to-main', '⇪', BRAND.muted, actions.ask)}
        {TipView(elements, 'push & merge to origin/main', '', BRAND.muted)}
      </Box>
      {doing ? <Text key="push-state" color={repo.state === 'failed' ? BRAND.error : BRAND.muted}>{doing}</Text> : null}
    </Box>
  )
}

// Asked from Push & merge: what pushing the session's work to main does, then Cancel or go ahead.
export function PushDialogView(elements: ElementTable, repo: RepoClient, session: string, actions: PushActions) {
  const { Box, Button, Text } = elements
  if (!repo.isAsking) return null
  return (
    <Box key="push-dialog" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Push ${session} and merge it to origin/main?`}</Text>
      <Text color={BRAND.muted}>Commits the work, pushes its branch, merges it into the default branch and pushes that. The version is not raised; run /version first for a release.</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="push-cancel" label="Cancel" onPress={actions.cancel} />
        <Button key="push-confirm" label="Push & merge" variant="primary" onPress={actions.pushToMain} />
      </Box>
    </Box>
  )
}
