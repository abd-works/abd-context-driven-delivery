export class AccountCredentials {
  verify(): void {
    return
  }
}
export function given(name: string, fn: () => void): void {
  fn()
}
given("the account is verified", () => {
  new AccountCredentials().verify()
})
