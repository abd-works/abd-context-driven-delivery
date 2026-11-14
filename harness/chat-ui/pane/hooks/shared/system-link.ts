import type { EngineInterface } from 'claude-code'

import { reasonOf } from '../error-display/failure-client'

// Each system's own way to hand a link to the program registered for it: a web page to the browser, a claude:// link to
// the Claude app. Mods have no call that opens a link, so the first opener this system has is run. No shell runs, so a
// link's & and quotes stay part of the link.
function openersOf(link: string): string[][] {
  return [['rundll32', 'url.dll,FileProtocolHandler', link], ['open', link], ['xdg-open', link]]
}

// Why no opener took the link, each opener's own reason; empty once one did.
export async function linkNotOpened($: EngineInterface, link: string): Promise<string> {
  const reasons: string[] = []
  for (const argv of openersOf(link)) {
    try {
      const opened = await $.process.run(argv)
      if (opened.exitCode === 0) return ''
      reasons.push(`${argv[0]} exited ${opened.exitCode}${opened.stderr.trim() ? `: ${opened.stderr.trim()}` : ''}`)
    } catch (failure) {
      reasons.push(`${argv[0]}: ${reasonOf(failure)}`)
    }
  }
  return reasons.join('; ')
}
