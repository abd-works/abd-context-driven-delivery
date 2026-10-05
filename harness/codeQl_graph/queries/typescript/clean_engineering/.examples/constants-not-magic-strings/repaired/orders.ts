const SimType = { esim: "embedded" } as const
export function kind(value: string): boolean {
  return value === SimType.esim
}
