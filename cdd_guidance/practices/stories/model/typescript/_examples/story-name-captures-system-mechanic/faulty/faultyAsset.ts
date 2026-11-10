function story(name: string, fn: () => void): void {
  fn()
}
story("Handle Request", () => {})
