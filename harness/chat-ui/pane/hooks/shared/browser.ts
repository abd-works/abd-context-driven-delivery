import type { EngineInterface } from 'claude-code'

// Opens a page in the person's browser with the system's own opener, since mods have no call that opens a link.
export async function openInBrowser($: EngineInterface, url: string): Promise<boolean> {
  const openers = [['rundll32', 'url.dll,FileProtocolHandler', url], ['open', url], ['xdg-open', url]]
  for (const argv of openers) {
    const opened = await $.process.run(argv).catch(() => null)
    if (opened?.exitCode === 0) return true
  }
  return false
}
