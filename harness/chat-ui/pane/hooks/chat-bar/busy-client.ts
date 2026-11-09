import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BusyJson } from '../../types'

// A switch or close commits, pushes, merges, and moves the chat, which can take a while; the band shows what it is doing
// with a turning wheel until it is done.
const busy = atom({ plugin: 'cdd-board', key: 'busy' } as const, { doing: '', frame: 0 } as BusyJson)

const WHEEL = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
const TURN_MILLISECONDS = 120

// Atom busy, declared in pane/types/index.d.ts and kept in this file.
export async function currentBusy($: EngineInterface): Promise<{ doing: string; wheel: string }> {
  const { doing, frame } = await read($, busy)
  return { doing, wheel: WHEEL[frame % WHEEL.length] ?? WHEEL[0]! }
}

// Turns the wheel while doing still names this work.
async function turnWheel($: EngineInterface, doing: string): Promise<void> {
  while ((await read($, busy)).doing === doing) {
    await $.clock.sleep(TURN_MILLISECONDS)
    await update($, busy, shown => (shown.doing === doing ? { doing, frame: shown.frame + 1 } : shown))
  }
}

// Shows doing with a turning wheel while work runs, and clears it once the work ends, however it ends.
export async function whileBusy<T>($: EngineInterface, doing: string, work: () => Promise<T>): Promise<T> {
  await update($, busy, () => ({ doing, frame: 0 }))
  void turnWheel($, doing)
  try {
    return await work()
  } finally {
    await update($, busy, () => ({ doing: '', frame: 0 }))
  }
}
