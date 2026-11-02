// The browser and the server share these: a chat as the cdd-board mod reports it, and what it is sent.
export type ChatCommand = { kind: 'submit' | 'fill' | 'command'; text: string }
export type Chat = { id: string; isBusy: boolean }
