import type { ClientModule } from 'claude-code'

import type { BoardScrollbarJson } from '../../types'

// The engine's window moves up and down only, so the board draws its own sideways bar. Only a Client hears a drag.
const BoardScrollbar: ClientModule<BoardScrollbarJson> = (bar, surface) => {
  const { Box } = surface.elements
  surface.onPointer(event => {
    if (surface.columns === 0 || !event.button || (event.type !== 'down' && event.type !== 'move')) return
    surface.post({ columnOffset: Math.round((event.x / surface.columns) * bar.limit) })
  })
  const thumb = Math.round(bar.shownShare * 100)
  const before = Math.round((bar.offset / bar.limit) * (100 - thumb))
  return (
    <Box key="track" flexDirection="row" width="100%" backgroundColor={bar.trackColor}>
      <Box key="before" width={`${before}%`} />
      <Box key="thumb" width={`${thumb}%`} height={1} backgroundColor={bar.thumbColor} hover={{ backgroundColor: bar.hoverColor }} />
    </Box>
  )
}

export default BoardScrollbar
