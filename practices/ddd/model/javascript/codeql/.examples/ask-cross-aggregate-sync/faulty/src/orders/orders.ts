import { Transfers } from "../transfers/transfers";

export class Orders {
  nextTransfer(): Transfers {
    return new Transfers();
  }
}
