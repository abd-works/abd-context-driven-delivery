import { loadFake } from "./fakeAdapter.js";

export const title = "CheckoutScreen";

export function render() {
  loadFake();
  return "<div>checkout</div>";
}
