import type { ClientModule } from 'claude-code'

import type { TileHoverJson } from '../../types'

const HOVER_OPEN_DELAY = 400

type HoverState = { isInside: boolean; hasOpened: boolean }

// A tile's heading. Only a Client hears a pointer pass over it: a short hover opens the tile, leaving closes it, and
// a press keeps it open.
const TileHover: ClientModule<TileHoverJson, HoverState> = (tile, surface) => {
  const { Box, Text } = surface.elements
  const place = { place: tile.place, ticket: tile.ticket, stage: tile.stage, slugs: tile.slugs }
  if (surface.state === undefined) {
    surface.setState({ isInside: false, hasOpened: false })
    surface.every(HOVER_OPEN_DELAY, () => {
      const state = surface.state
      if (!state?.isInside || state.hasOpened) return
      surface.setState({ ...state, hasOpened: true })
      surface.post({ hoverTile: place })
    })
  }
  surface.onPointer(event => {
    if (event.type === 'enter') surface.setState({ isInside: true, hasOpened: false })
    if (event.type === 'leave') {
      surface.setState({ isInside: false, hasOpened: false })
      surface.post({ leaveTile: tile.place })
    }
    if (event.type === 'down' && event.button === 'left') surface.post({ pressTile: place })
  })
  return (
    <Box key="heading" flexDirection="row" justifyContent="space-between" width="100%">
      <Text color={tile.color}>{tile.label}</Text>
      <Text color={tile.color}>{tile.mark}</Text>
    </Box>
  )
}

export default TileHover
