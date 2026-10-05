declare const customerRepository: { save(): void }
export class OrderRepository {
  complete(): void {
    customerRepository.save()
  }
}
