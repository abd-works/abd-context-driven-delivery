export interface OrdersRepository {
  load(id: string): void;
  create(): void;
  search(): void;
  update(): void;
}
