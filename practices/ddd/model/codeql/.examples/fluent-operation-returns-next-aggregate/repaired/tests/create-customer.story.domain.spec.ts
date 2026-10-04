declare function scenario(name: string, fn: () => void): void
const customerRepository = {
  create(): { id: string } {
    return { id: "1" }
  },
}
scenario("creates a customer", () => {
  const customer = customerRepository.create()
  return customer.id
})
