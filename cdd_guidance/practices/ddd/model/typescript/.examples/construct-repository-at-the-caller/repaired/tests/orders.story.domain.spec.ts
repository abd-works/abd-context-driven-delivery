export class OrderRepository {}
export function scenario(): OrderRepository {
  return new OrderRepository()
}
