import type { ClientModule } from 'claude-code'

import type { TicketCardJson } from '../types'

// One board card. A surface module, because only a Client hears a press anywhere in its region: a Button can hold
// no Box, so a Button card could be pressed on its words alone.
const TicketCard: ClientModule<TicketCardJson> = (card, surface) => {
  const { Box, Button, Text } = surface.elements
  surface.onPointer(event => {
    if (event.type === 'down' && event.button === 'left') surface.post({ select: card.address })
  })
  const arrow = (direction: 'previous' | 'next', glyph: string, canMove: boolean) => (
    <Button
      key={direction}
      plain
      label={glyph}
      dimColor={!canMove}
      onPress={() => (canMove ? surface.post({ move: direction, ticket: card.name }) : undefined)}
    />
  )
  return (
    <Box
      key="card"
      flexDirection="column"
      width="100%"
      borderStyle="single"
      borderColor={card.borderColor}
      hover={{ borderColor: card.hoverColor }}
      backgroundColor={card.backgroundColor}
      paddingX={1}
    >
      <Text bold color={card.titleColor}>
        {card.title}
      </Text>
      <Text color={card.mutedColor}>{card.meta}</Text>
      <Box key="segments" flexDirection="row" columnGap={1}>
        {card.segments.map(segment => (
          <Box key={segment.scope} hover={{ scope: segment.scope }}>
            <Text color={segment.color}>▬▬</Text>
          </Box>
        ))}
      </Box>
      {/* In the card's own flow, so a neighbouring column can neither clip nor cover the name. */}
      {card.segments.map(segment => (
        <Box display="none" hover={{ scope: segment.scope, display: 'flex' }}>
          <Text color={card.titleColor}>{segment.skill}</Text>
        </Box>
      ))}
      {card.tail ? <Text color={card.tail.color}>{card.tail.text}</Text> : null}
      <Box key="moves" flexDirection="row" justifyContent="space-between">
        {arrow('previous', '←', card.canMovePrevious)}
        {arrow('next', '→', card.canMoveNext)}
      </Box>
    </Box>
  )
}

export default TicketCard
