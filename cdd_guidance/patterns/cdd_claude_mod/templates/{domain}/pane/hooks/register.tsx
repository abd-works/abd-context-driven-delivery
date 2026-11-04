import type { Register } from 'claude-code'

import { current{Object} } from './{domain}/{object}-client'
import { {Screen}View } from './{domain}/{screen}-view'

const PANE = 'cdd-{domain}'

// Boot: connects engine events to clients and views, and holds nothing else.
export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    void $.ui.open({ id: PANE, title: '{Domain}' })
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e, next) => {
    const {object} = await current{Object}($)
    if ({object} === null) return next(e)
    return {Screen}View($, $.ui.resolve(e), {object})
  })
}
