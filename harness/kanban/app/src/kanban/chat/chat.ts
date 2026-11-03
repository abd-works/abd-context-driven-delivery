// The browser and the server share these: a chat as the cdd-board mod reports it, and what it is sent.
// A chat is sent to by its id; its name is only what a person reads, and it can change as the chat goes on.
export type ChatCommand = { kind: 'submit' | 'fill' | 'command'; text: string }
export type Chat = { id: string; name: string; isBusy: boolean }
