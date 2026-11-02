import type { ElementTable } from 'claude-code'

import { BRAND, COLLAPSE_MARK, EXPAND_MARK, faded, OFF_BUTTON_LIGHT } from './brand'
import type { ViewContext } from './view-context'

// The canvas's orange button. A desktop draws a primary Button in its own colours, and a Button takes no background,
// so a plain one sits in an orange Box. A terminal marks a primary Button in the accent colour itself.
export function PrimaryButtonView({ Box, Button, Text }: ElementTable, key: string, label: string, onPress: (() => unknown) | null) {
  return (
    <Box
      key={`primary-${key}`}
      flexShrink={0}
      paddingX={1}
      borderStyle="single"
      borderColor={onPress ? BRAND.accent : faded(BRAND.accent, OFF_BUTTON_LIGHT)}
      backgroundColor={onPress ? BRAND.accent : faded(BRAND.accent, OFF_BUTTON_LIGHT)}
      hover={onPress ? { backgroundColor: BRAND.accentPressed, borderColor: BRAND.accentPressed } : {}}
    >
      <Button key={key} plain label={label} onPress={onPress ?? (() => undefined)}>
        <Text weight="semibold" color={onPress ? BRAND.onAccent : BRAND.muted}>
          {label}
        </Text>
      </Button>
    </Box>
  )
}

// Button has no disabled state: an action that is not allowed is drawn dim and does nothing.
export function ActionButtonView({ elements, hasPictures }: ViewContext, key: string, label: string, onPress: (() => unknown) | null, isMain = false) {
  const { Button } = elements
  if (isMain && hasPictures) return PrimaryButtonView(elements, key, label, onPress)
  return (
    <Button
      key={key}
      label={label}
      dimColor={!onPress}
      variant={isMain && onPress ? 'primary' : 'secondary'}
      onPress={onPress ?? (() => undefined)}
    />
  )
}

export function LinkButtonView({ elements: { Button, Text } }: ViewContext, key: string, label: string, color: string, onPress: () => unknown) {
  return (
    <Button key={key} plain onPress={onPress}>
      <Text mono size="caption" weight="semibold" underline color={color}>
        {label}
      </Text>
    </Button>
  )
}

export function ExpandToggleView({ elements: { Button } }: ViewContext, key: string, isExpanded: boolean, onPress: () => unknown) {
  return <Button key={key} label={isExpanded ? COLLAPSE_MARK : EXPAND_MARK} onPress={onPress} />
}

// A Button holds only text, so a switch's track and thumb are glyphs.
export function SwitchView({ elements: { Button, Text } }: ViewContext, key: string, isOn: boolean, onPress: (() => unknown) | null) {
  return (
    <Button key={key} plain dimColor={!onPress} onPress={onPress ?? (() => undefined)}>
      <Text color={isOn ? BRAND.accent : BRAND.idle}>{isOn ? '━●' : '●━'}</Text>
    </Button>
  )
}

// The bar a colored block carries down its left side: a Box has no border of one side.
export function ColorBarView({ elements: { Box } }: ViewContext, color: string) {
  return <Box width={1} flexShrink={0} backgroundColor={color} />
}

export function SectionTitleView({ elements: { Text } }: ViewContext, title: string) {
  return (
    <Text mono weight="semibold" size="footnote" color={BRAND.muted}>
      {title}
      <Text color={BRAND.accent}>_</Text>
    </Text>
  )
}
