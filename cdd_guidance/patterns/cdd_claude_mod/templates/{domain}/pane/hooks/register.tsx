import { read } from 'claude-code'
import type { Register } from 'claude-code'

import { {Domain}Client, {domain}State } from './{domain}/{domain}-client'
import { {Screen}View } from './{domain}/{screen}-view'

const PANE = 'cdd-{domain}'

// Boot: connects engine events to clients and views, and holds nothing else.
export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    void $.ui.open({ id: PANE, title: '{Domain}' })
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, ($, e, next) => {
    const json = read($, {domain}State)
    if (json === null) return next(e)
    return {Screen}View($.ui.resolve(e), new {Domain}Client($, json))
  })
}
