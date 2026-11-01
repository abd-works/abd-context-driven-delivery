import type { ClientModule } from 'claude-code'

import type { TicketCardJson } from '../../types'

// One board card's face. A surface module, because only a Client hears a press anywhere in its region: a Button can
// hold no Box. Each line truncates, so the height the pane gives the region is the height drawn: a region whose text
// wraps is measured wrongly and draws over the card's controls, which the pane's own tree holds.
const TicketCard: ClientModule<TicketCardJson> = (card, surface) => {
  const { Box, Text } = surface.elements
  surface.onPointer(event => {
    if (event.type === 'down' && event.button === 'left') surface.post({ select: card.address })
  })
  return (
    <Box key="card" flexDirection="column" width="100%">
      <Box key="face" flexDirection="row" justifyContent="space-between">
        <Box key="words" flexDirection="column" flexGrow={1}>
          <Text bold wrap="truncate-end" color={card.titleColor}>
            {card.title}
          </Text>
          <Text wrap="truncate-end" color={card.mutedColor}>
            {card.meta}
          </Text>
          {card.tail ? (
            <Text wrap="truncate-end" color={card.tail.color}>
              {card.tail.text}
            </Text>
          ) : null}
        </Box>
        <Box key="segments" flexDirection="column">
          {card.segments.map(segment => (
            <Box key={segment.scope} hover={{ scope: segment.scope }}>
              <Text color={segment.color} dimColor={segment.isDim}>
                ▬▬
              </Text>
            </Box>
          ))}
        </Box>
      </Box>
      {/* Over the card's words, because the face has a fixed height and a neighbouring column would clip anything outside it. */}
      {card.segments.map(segment => (
        <Box position="absolute" top={1} left={0} display="none" hover={{ scope: segment.scope, display: 'flex' }}>
          <Text wrap="truncate-end" color={card.titleColor}>
            {segment.skill}
          </Text>
        </Box>
      ))}
    </Box>
  )
}

export default TicketCard
