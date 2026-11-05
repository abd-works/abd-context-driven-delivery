// A slash command as $.command.run takes it: the name without its slash, and the rest of the words as its arguments.
export function commandOf(text: string): { command: string; args: string } {
  const [command = '', ...words] = text.slice(1).split(' ')
  return { command, args: words.join(' ') }
}
