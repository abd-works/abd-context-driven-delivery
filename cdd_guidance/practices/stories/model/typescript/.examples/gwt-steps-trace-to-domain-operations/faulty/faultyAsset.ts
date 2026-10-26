function given(name: string, fn: () => void): void {
  fn()
}
given("validPayload", () => {})
