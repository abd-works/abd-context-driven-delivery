import { useRef } from 'react'
import type { PointerEvent } from 'react'

type GripProps = {
  onPointerDown: (event: PointerEvent<HTMLElement>) => void
  onPointerMove: (event: PointerEvent<HTMLElement>) => void
  onPointerUp: () => void
}

// A grip keeps the pointer for the whole drag, so a fast drag cannot slip off it. `moved` gets how far the pointer has
// gone from where it was pressed, and `startValue` is read once, at the press.
export function useDragGrip(axis: 'x' | 'y', startValue: () => number, moved: (startValue: number, distance: number, grip: HTMLElement) => void): GripProps {
  const drag = useRef<{ start: number; value: number } | null>(null)
  const positionOf = (event: PointerEvent<HTMLElement>) => (axis === 'x' ? event.clientX : event.clientY)
  return {
    onPointerDown: event => {
      event.currentTarget.setPointerCapture(event.pointerId)
      drag.current = { start: positionOf(event), value: startValue() }
    },
    onPointerMove: event => {
      if (drag.current) moved(drag.current.value, positionOf(event) - drag.current.start, event.currentTarget)
    },
    onPointerUp: () => {
      drag.current = null
    },
  }
}
