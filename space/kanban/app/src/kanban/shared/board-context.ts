import { createContext, useContext, useSyncExternalStore } from 'react'

import type { BoardPage } from '../board/board-page'
import type { BoardState } from './board-store'

export const BoardContext = createContext<BoardPage | null>(null)

export function useBoard(): { page: BoardPage; state: BoardState } {
  const page = useContext(BoardContext)!
  const state = useSyncExternalStore(page.store.subscribe, page.store.read, page.store.read)
  return { page, state }
}
