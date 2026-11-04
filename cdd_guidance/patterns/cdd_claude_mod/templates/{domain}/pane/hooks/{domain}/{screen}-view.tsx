import type { ElementTable, EngineInterface } from 'claude-code'

import { moveNext } from './{object}-client'
import type { {Object}Client } from './{object}-client'

// Paints the client and hands presses to its actions. No rule, no MCP call, no atom write.
export function {Screen}View($: EngineInterface, { Box, Button, Text }: ElementTable, {object}: {Object}Client) {
  return (
    <Box flexDirection="column">
      <Text>{{object}.name}</Text>
      <Button key="move-next" label="Move next" onPress={() => moveNext($, {object})} />
    </Box>
  )
}
