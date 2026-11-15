import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { TipView } from '../shared/tip-view'
import type { RepoClient } from './repo-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

export type PushActions = { ask: () => unknown; cancel: () => unknown; push: () => unknown }

const DOING: Record<string, string> = { running: 'pushing to main…', failed: 'not pushed to main' }

// Push to main, as an icon beside the session's other buttons, with how the last push went.
export function PushButtonView(elements: ElementTable, repo: RepoClient, actions: PushActions) {
  const { Box, Text } = elements
  const doing = repo.state === 'installed' ? repo.landed : DOING[repo.state]
  return (
    <Box key="push-to-main" flexDirection="row" gap={1}>
      <Box key="push-to-main-box">
        {GlyphButtonView(elements, 'push-to-main', '⇪', BRAND.muted, actions.ask)}
        {TipView(elements, 'push to main on origin', '', BRAND.muted)}
      </Box>
      {doing ? <Text key="push-to-main-state" color={repo.state === 'failed' ? BRAND.error : BRAND.muted}>{doing}</Text> : null}
    </Box>
  )
}

// Asked from the button: what pushing the session's work to main does, then Cancel or go ahead.
export function PushDialogView(elements: ElementTable, repo: RepoClient, session: string, actions: PushActions) {
  const { Box, Button, Text } = elements
  if (!repo.isAsking) return null
  return (
    <Box key="push-dialog" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Push ${session} to main on origin?`}</Text>
      <Text color={BRAND.muted}>Commits the work, pushes its branch, merges it into main and pushes main. The version is not raised; run /version first for a release.</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="push-cancel" label="Cancel" onPress={actions.cancel} />
        <Button key="push-confirm" label="Push to main" variant="primary" onPress={actions.push} />
      </Box>
    </Box>
  )
}
