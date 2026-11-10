import type { ClientModule } from 'claude-code'

import type { SplitGripJson } from '../../types'

// The bar between the board and the ticket's details. Only a Client hears a drag. The bar moves with the split, so
// a held pointer's row is always its distance from where the split now stands.
const SplitGrip: ClientModule<SplitGripJson> = (grip, surface) => {
  const { Box, Text } = surface.elements
  surface.onPointer(event => {
    if (event.type === 'move' && event.button === 'left' && event.y !== 0) {
      surface.post({ boardRows: grip.boardRows + event.y })
    }
  })
  return (
    <Box key="grip" width="100%" justifyContent="center">
      <Text color={grip.color} hover={{ color: grip.hoverColor }}>
        ━━━━━━━━
      </Text>
    </Box>
  )
}

export default SplitGrip
