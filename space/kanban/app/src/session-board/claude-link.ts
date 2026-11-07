import { spawn } from 'node:child_process'

import { HttpException } from './http-exception'

const BAD_REQUEST = 400
// Only the link that opens a new chat in the Claude app, so the page cannot ask this server to open anything else.
const NEW_CHAT_LINK = 'claude://code/new?'

export type Launch = (command: string, args: string[]) => void

// Each system's own way to hand a link to the app registered for its scheme. No shell runs, so the link's & and quotes
// stay part of the link.
const systemOpener = (link: string): [string, string[]] => {
  if (process.platform === 'win32') return ['rundll32', ['url.dll,FileProtocolHandler', link]]
  if (process.platform === 'darwin') return ['open', [link]]
  return ['xdg-open', [link]]
}

const launchDetached: Launch = (command, args) => {
  spawn(command, args, { detached: true, stdio: 'ignore' }).unref()
}

// A page in the Claude app's Browser pane cannot hand a claude:// link to the app, so the board server opens it through
// the system, which passes it to the Claude app on this computer.
export class ClaudeLink {
  constructor(private readonly launch: Launch = launchDetached) {}

  open(link: unknown): void {
    if (typeof link !== 'string' || !link.startsWith(NEW_CHAT_LINK)) throw new HttpException(BAD_REQUEST, `Refused: the board opens only ${NEW_CHAT_LINK} links.`)
    this.launch(...systemOpener(link))
  }
}
