export class AccountCredentials {
  verify(): void {
    return
  }
}
export function activateAccount(account: AccountCredentials): void {
  account.verify()
}
