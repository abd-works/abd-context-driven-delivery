import type { EngineInterface } from 'claude-code'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// A coloured glyph a person can press. The desktop draws everything inside a Button in its own colour and padding, so
// the glyph is drawn as Text in its own colour and a see-through Button laid over it takes the press. The glyph's Box
// is keyed `<key>-mark`, the Button `<key>`. The Button is as wide as the glyph, one blank per character, so a glyph
// wider than one cell, such as </> or a two-digit count, takes a press anywhere on it, not only on its first cell.
export function GlyphButtonView({ Box, Button, Text }: ElementTable, key: string, glyph: string, colour: string, onPress: () => unknown, isUnderlined = false) {
  return (
    <Box key={`${key}-mark`}>
      <Text color={colour} underline={isUnderlined}>{glyph}</Text>
      <Box position="absolute" top={0} left={0}>
        <Button key={key} plain label={blankOver(glyph)} onPress={onPress} />
      </Box>
    </Box>
  )
}

// One blank for each character of glyph, so the see-through Button covers all of it.
export const blankOver = (glyph: string): string => ' '.repeat(Math.max(1, [...glyph].length))
