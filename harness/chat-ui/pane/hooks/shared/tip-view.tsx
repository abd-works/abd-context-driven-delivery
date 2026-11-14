import type { EngineInterface } from 'claude-code'

import { BRAND } from './brand'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// A label shown above an element while the pointer is on its keyed Box, as the canvas's hover tips. A tip given onPress
// is a button too: a see-through Button over its words takes the press.
export function TipView({ Box, Button, Text }: ElementTable, words: string, detail: string, detailColour: string, onPress?: () => unknown, key = '') {
  const tip = [
    <Text key="tip-words" color={BRAND.text}>{detail ? `${words} ` : words}</Text>,
    detail ? <Text key="tip-detail" color={detailColour}>{detail}</Text> : null,
  ]
  // A pressable tip is one whole Button holding its words: a see-through one laid over them takes no press.
  return (
    <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
      {onPress ? <Button key={key} plain onPress={onPress}>{tip}</Button> : tip}
    </Box>
  )
}
