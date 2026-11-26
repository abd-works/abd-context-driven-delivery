import express, { type Express, type NextFunction, type Request, type RequestHandler, type Response } from 'express'
import { randomUUID } from 'node:crypto'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { PAGE_FILES, STORY_DEMO_ROOT } from './files/files-paths'

const NOT_FOUND = 404

// The Story Demo scripts every generated UX mockup loads from /practices/ux/story-demo, kept in the CDD install this
// server runs from: harness/files_app/app sits three folders below it.
export const STORY_DEMO_FOLDER = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', 'cdd_guidance', 'practices', 'ux', 'story-demo')

// An HTML page shown in the Files app runs in a frame of no origin (the frame's sandbox allows scripts but never the
// page's own origin), so a module script it loads is a cross-origin request, read only with this header; a file that is
// not there carries it too, so the page's console says it was not found rather than blocked.
const anyOrigin = (_request: Request, response: Response, next: NextFunction): void => {
  response.setHeader('Access-Control-Allow-Origin', '*')
  next()
}

// The files an HTML page in the Files app's frame asks for: its own scripts, styles and images, from its project, and
// the Story Demo scripts of the CDD install. A project is reached only under a key this server made for it, handed to
// the Files app's own page through a post no other site can read, so no other page in the browser reads a project's
// files; a file outside the project or the Story Demo folder, or a dotfile such as .env, is never served.
export class PageFiles {
  private readonly keys = new Map<string, string>()
  private readonly served = new Map<string, RequestHandler>()

  constructor(private readonly storyDemo: string = STORY_DEMO_FOLDER) {}

  // Where a page of the project folder finds its files: its address, under the project's key, made once.
  baseOf(folder: string): string {
    let key = this.keys.get(folder)
    if (!key) {
      key = randomUUID()
      this.keys.set(folder, key)
      this.served.set(key, express.static(folder, { fallthrough: false }))
    }
    return `${PAGE_FILES}/${key}/`
  }

  // Serve a project's files under its key, and the Story Demo scripts; a key this server never made finds nothing.
  serveOn(app: Express): void {
    app.use(STORY_DEMO_ROOT, anyOrigin, express.static(this.storyDemo, { fallthrough: false }))
    app.use(`${PAGE_FILES}/:key`, anyOrigin, (request, response, next) => {
      const serve = this.served.get(request.params.key)
      if (!serve) return void response.status(NOT_FOUND).type('text/plain').send('No project is served under this key.')
      serve(request, response, next)
    })
  }
}
