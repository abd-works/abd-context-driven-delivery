class Cart {}
function given(name: string, fn: () => void): void {
  fn()
}
given("a Cart exists", () => {})
