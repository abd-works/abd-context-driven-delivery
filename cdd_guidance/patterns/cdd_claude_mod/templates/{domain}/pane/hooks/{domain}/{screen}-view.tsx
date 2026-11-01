import type { ElementTable } from 'claude-code'

import type { {Domain}Client } from './{domain}-client'

// Paints the client and calls its operations. No rule, no MCP call, no atom write.
export function {Screen}View({ Box, Button, Text }: ElementTable, client: {Domain}Client) {
  return (
    <Box flexDirection="column">
      <Text>{client.name}</Text>
      <Button key="move-next" label="Move next" onPress={() => client.moveNext()} />
    </Box>
  )
}
