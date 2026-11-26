// What + says when the prompt box is empty, since a card's new task is the prompt box's draft. While it shows, the
// message the person sends next becomes the card's task.
export const EMPTY_TASK_NOTICE = 'Type the task in the prompt box and send it, or press + again, to add it to this card.'

/** What the band says once the queue changed: a change clears what it said, except + waiting for a task, which stays
 * shown for as long as + waits, so the person never sends a message that is taken as a task without being told. */
export function noticeAfterChange(shown: string): string {
  return shown === EMPTY_TASK_NOTICE ? shown : ''
}

/** Whether + still waits for a task on the card awaited: only while the band says so and the queue is on. A wait the
 * person can no longer see, or one on a queue switched off, has ended, so the message goes to the chat. */
export function isTaskAwaited(awaited: string, shown: string, isOn: boolean): boolean {
  return awaited !== '' && shown === EMPTY_TASK_NOTICE && isOn
}
