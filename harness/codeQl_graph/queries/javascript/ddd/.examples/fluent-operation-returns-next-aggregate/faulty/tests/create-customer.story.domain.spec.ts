declare function scenario(name: string, fn: () => void): void
const customerRepository = {
  create(): { id: string } {
    return { id: "1" }
  },
}
const account = {
  storeCustomerId(): void {
    return
  },
}
scenario("creates a customer", () => {
  customerRepository.create()
  account.storeCustomerId()
})
