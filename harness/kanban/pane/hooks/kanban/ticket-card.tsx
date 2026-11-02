import type { ClientModule } from 'claude-code'

import type { TicketCardJson } from '../../types'

// One board card's words. A surface module, because only a Client hears a press anywhere in its region: a Button can
// hold no Box. The pane gives the region the rows the title wraps to.
const TicketCard: ClientModule<TicketCardJson> = (card, surface) => {
  const { Box, Text } = surface.elements
  surface.onPointer(event => {
    if (event.type === 'down' && event.button === 'left') surface.post({ select: card.address })
  })
  return (
    <Box key="words" flexDirection="column" width="100%">
      <Text weight="semibold" color={card.titleColor} hover={{ color: card.hoverColor }}>
        {card.title}
      </Text>
      <Text mono size="caption" wrap="truncate-end" color={card.mutedColor}>
        {card.meta}
      </Text>
    </Box>
  )
}

export default TicketCard
