class Order {}
function story(name: string, fn: () => void): void {
  fn()
}
story("Submit Order", () => {})
