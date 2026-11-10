function given(name: string, fn: () => void): void {
  fn()
}
given("a Customer exists", () => {})
