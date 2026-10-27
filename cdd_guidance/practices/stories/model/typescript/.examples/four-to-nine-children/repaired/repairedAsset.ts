function story(name: string, fn: () => void): void {
  fn()
}
function scenario(name: string, fn: () => void): void {
  fn()
}
story("Submit Order", () => {
  scenario("accepted", () => {})
  scenario("rejected", () => {})
  scenario("expired", () => {})
  scenario("duplicate", () => {})
})
