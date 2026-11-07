export class Orders {}

export class OrdersRepository {
  load(id: string): Orders {
    return new Orders()
  }
  create(): Orders {
    return new Orders()
  }
  search(): Orders[] {
    return []
  }
  update(orders: Orders): void {
    return
  }
}
