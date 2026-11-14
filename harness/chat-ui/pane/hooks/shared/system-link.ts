import type { EngineInterface } from 'claude-code'

// Each system's own way to hand a link to the program registered for it: a web page to the browser, a claude:// link to
// the Claude app. Mods have no call that opens a link, so the first opener this system has is run. No shell runs, so a
// link's & and quotes stay part of the link.
function openersOf(link: string): string[][] {
  return [['rundll32', 'url.dll,FileProtocolHandler', link], ['open', link], ['xdg-open', link]]
}

export async function openedWithSystem($: EngineInterface, link: string): Promise<boolean> {
  for (const argv of openersOf(link)) {
    const opened = await $.process.run(argv).catch(() => null)
    if (opened?.exitCode === 0) return true
  }
  return false
}
