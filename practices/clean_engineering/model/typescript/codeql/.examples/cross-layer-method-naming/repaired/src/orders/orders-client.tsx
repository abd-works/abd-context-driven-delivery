import { Orders } from "./orders";
export class OrdersClient extends Orders {
  filterByStatus(status: string) {
    return super.filterByStatus(status);
  }
}
