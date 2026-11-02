import type { ClientModule } from 'claude-code'

import type { PanelGripJson } from '../../types'

// The left edge of a side panel. The edge moves with the panel, so a held pointer's column is always its distance
// from where the edge now stands, and dragging left widens the panel.
const PanelGrip: ClientModule<PanelGripJson> = (grip, surface) => {
  const { Box, Text } = surface.elements
  surface.onPointer(event => {
    if (event.type === 'move' && event.button === 'left' && event.x !== 0) {
      surface.post({ panel: grip.panel, width: grip.width - event.x })
    }
  })
  return (
    <Box key="grip" height="100%">
      <Text color={grip.color} hover={{ color: grip.hoverColor }}>
        ║
      </Text>
    </Box>
  )
}

export default PanelGrip
