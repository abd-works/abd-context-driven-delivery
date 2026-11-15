import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { TipView } from '../shared/tip-view'
import type { RepoClient, ToMain } from './repo-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

export type ToMainActions = { ask: (taking: ToMain) => unknown; cancel: () => unknown; take: (taking: ToMain) => unknown }

const DOING: Record<string, string> = { running: 'taking to main…', failed: 'not taken to main' }

// Merge to main and Push to main, as icons beside the session's other buttons, with how the last one went.
export function ToMainButtonsView(elements: ElementTable, repo: RepoClient, actions: ToMainActions) {
  const { Box, Text } = elements
  const doing = repo.state === 'installed' ? repo.landed : DOING[repo.state]
  return (
    <Box key="to-main" flexDirection="row" gap={1}>
      <Box key="merge-to-main-box">
        {GlyphButtonView(elements, 'merge-to-main', '⤵', BRAND.muted, () => actions.ask('merge'))}
        {TipView(elements, 'merge into main', '', BRAND.muted)}
      </Box>
      <Box key="push-to-main-box">
        {GlyphButtonView(elements, 'push-to-main', '⇪', BRAND.muted, () => actions.ask('push'))}
        {TipView(elements, 'push to main on origin', '', BRAND.muted)}
      </Box>
      {doing ? <Text key="to-main-state" color={repo.state === 'failed' ? BRAND.error : BRAND.muted}>{doing}</Text> : null}
    </Box>
  )
}

// Asked from either button: what taking the session's work to main does, then Cancel or go ahead.
export function ToMainDialogView(elements: ElementTable, repo: RepoClient, session: string, actions: ToMainActions) {
  const { Box, Button, Text } = elements
  const taking = repo.asking
  if (taking === null) return null
  const isPush = taking === 'push'
  return (
    <Box key="to-main-dialog" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{isPush ? `Push ${session} to main on origin?` : `Merge ${session} into main?`}</Text>
      <Text color={BRAND.muted}>
        {isPush
          ? 'Commits the work, pushes its branch, merges it into main and pushes main. The version is not raised; run /version first for a release.'
          : 'Commits the work on its branch and merges it into main in the clone. Nothing is pushed.'}
      </Text>
      <Box flexDirection="row" gap={1}>
        <Button key="to-main-cancel" label="Cancel" onPress={actions.cancel} />
        <Button key="to-main-confirm" label={isPush ? 'Push to main' : 'Merge into main'} variant="primary" onPress={() => actions.take(taking)} />
      </Box>
    </Box>
  )
}
