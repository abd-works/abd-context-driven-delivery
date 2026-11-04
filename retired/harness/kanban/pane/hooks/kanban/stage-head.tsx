import type { ElementTable } from 'claude-code'

import type { ColumnJson } from '../../types'
import { BRAND, scopeShape, STAGE_SCOPES } from './brand'
import type { ViewContext } from './view-context'

const MAXIMUM_HOVER_SCOPE = 64

function ScopeShapeView(view: ViewContext, stage: ColumnJson, hoverScope: string) {
  const { elements, hasPictures } = view
  const { Box, Text } = elements
  const scope = STAGE_SCOPES[stage.name]
  if (!scope) return null
  const Svg = hasPictures ? (elements as ElementTable<'desktop'>).Svg : null
  return (
    <Box flexShrink={0} hover={{ scope: hoverScope }}>
      {Svg ? <Svg source={scopeShape(scope.width, scope.height)} alt={scope.name} width={scope.width} height={scope.height} /> : <Text color={BRAND.accent}>▭</Text>}
    </Box>
  )
}

// Over the head, because a Box paints over only what was drawn before it, so a tip below would sit under the next line.
function ScopeTipView({ elements: { Box, Text } }: ViewContext, stage: ColumnJson, hoverScope: string) {
  const scope = STAGE_SCOPES[stage.name]
  if (!scope) return null
  return (
    <Box position="absolute" top={0} left={0} right={0} display="none" backgroundColor={BRAND.raised} hover={{ scope: hoverScope, display: 'flex' }}>
      <Text mono size="caption" wrap="truncate-end" color={BRAND.muted}>
        <Text weight="bold" color={BRAND.accentText}>
          {scope.name.toUpperCase()}
        </Text>{' '}
        {scope.reach} · {scope.covers}
      </Text>
    </Box>
  )
}

function StageTitleView(view: ViewContext, stage: ColumnJson) {
  const { Box, Link, Text } = view.elements
  const title = (
    <Text mono size="footnote" weight="bold" underline color={BRAND.text} hover={{ color: BRAND.accentText }}>
      {stage.name.toUpperCase()}
    </Text>
  )
  const href = STAGE_SCOPES[stage.name]?.href
  return (
    <Box key={`${stage.name}-title`} flexGrow={1}>
      {href ? <Link href={href}>{title}</Link> : title}
    </Box>
  )
}

// The raised head a stage has on the board and in the details: its scope, its name, and what the place adds at the end.
export function StageHeadBoxView(view: ViewContext, stage: ColumnJson, place: string, borderColor: string, trailing: unknown) {
  const { Box } = view.elements
  const hoverScope = `scope-${place}`.slice(0, MAXIMUM_HOVER_SCOPE)
  return (
    <Box
      key={`head-${place}`}
      flexDirection="row"
      alignItems="center"
      columnGap={1}
      paddingX={1}
      borderStyle="single"
      borderColor={borderColor}
      hover={{ borderColor: BRAND.accent }}
      backgroundColor={BRAND.raised}
    >
      {ScopeShapeView(view, stage, hoverScope)}
      {StageTitleView(view, stage)}
      {trailing}
      {ScopeTipView(view, stage, hoverScope)}
    </Box>
  )
}
