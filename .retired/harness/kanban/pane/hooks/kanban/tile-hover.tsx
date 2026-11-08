import type { ClientModule } from 'claude-code'

import type { TileHoverJson } from '../../types'

const HOVER_OPEN_DELAY = 400

type HoverState = { isInside: boolean; hasOpened: boolean }

// A tile's heading. Only a Client hears a pointer pass over it: a short hover opens the tile, leaving closes it, and
// a press keeps it open. On an opened card only a press opens one, because the card's action bar moves to the tile
// and the rows would slide out from under the pointer.
const TileHover: ClientModule<TileHoverJson, HoverState> = (tile, surface) => {
  const { Box, Text } = surface.elements
  const place = { place: tile.place, ticket: tile.ticket, stage: tile.stage, slugs: tile.slugs, menuSlugs: tile.menuSlugs }
  if (surface.state === undefined) {
    surface.setState({ isInside: false, hasOpened: false })
    surface.every(HOVER_OPEN_DELAY, () => {
      const state = surface.state
      if (!tile.opensOnHover || !state?.isInside || state.hasOpened) return
      surface.setState({ ...state, hasOpened: true })
      surface.post({ hoverTile: place })
    })
  }
  surface.onPointer(event => {
    if (event.type === 'enter') surface.setState({ isInside: true, hasOpened: false })
    if (event.type === 'leave') {
      surface.setState({ isInside: false, hasOpened: false })
      if (tile.opensOnHover) surface.post({ leaveTile: tile.place })
    }
    if (event.type === 'down' && event.button === 'left') surface.post({ pressTile: place })
  })
  return (
    <Box key="heading" flexDirection="row" width="100%">
      <Text size="footnote" weight="semibold" wrap="truncate-end" color={tile.color}>
        {tile.label}
      </Text>
    </Box>
  )
}

export default TileHover
