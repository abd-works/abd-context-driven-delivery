import type { Register } from 'claude-code'

const SERVER = 'http://127.0.0.1:8777'
const POLL_MILLISECONDS = 1000
const FILL_DELAY_MILLISECONDS = 15000

export const register: Register = (on) => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    const chat = await $.session.id()
    const report = (mode: string, outcome: string) =>
      $.http.fetch(`${SERVER}/result`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, chat, outcome }),
      })
    $.clock.every(POLL_MILLISECONDS, () => {
      void $.http
        .fetch(`${SERVER}/next?chat=${encodeURIComponent(chat)}`)
        .then(async (response) => {
          const command = JSON.parse(response.text)
          if (command.mode === 'submit') {
            await report('submit', 'submitting')
            await $.prompt.submit({ text: command.text })
            await report('submit', 'turn finished')
          } else if (command.mode === 'fill') {
            // Waits so the fill lands while the chat is idle, after the turn that pressed the button.
            $.clock.after(FILL_DELAY_MILLISECONDS, () => {
              void $.prompt
                .fill({ text: command.text, mode: 'append' })
                .then(async (filled) => {
                  const box = await $.prompt.read()
                  await report('fill', `isFilled=${filled.isFilled} boxReadsBack=${JSON.stringify(box.text)}`)
                })
            })
          }
        })
        .catch(() => undefined)
    })
    return result
  })
}
