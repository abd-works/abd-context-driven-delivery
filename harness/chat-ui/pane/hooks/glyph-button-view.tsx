import type { EngineInterface } from 'claude-code'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// A coloured glyph a person can press. The desktop draws everything inside a Button in its own colour and padding, so
// the glyph is drawn as Text in its own colour and a see-through Button laid over it takes the press. The glyph's Box
// is keyed `<key>-mark`, the Button `<key>`.
export function GlyphButtonView({ Box, Button, Text }: ElementTable, key: string, glyph: string, colour: string, onPress: () => unknown, isUnderlined = false) {
  return (
    <Box key={`${key}-mark`}>
      <Text color={colour} underline={isUnderlined}>{glyph}</Text>
      <Box position="absolute" top={0} left={0}>
        <Button key={key} plain label=" " onPress={onPress} />
      </Box>
    </Box>
  )
}
