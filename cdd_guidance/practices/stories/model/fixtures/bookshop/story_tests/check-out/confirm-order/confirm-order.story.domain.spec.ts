/** Confirm Order at the domain tier: the shared scenarios on Order itself. */

import { OrderRepository } from "../../../src/bookshop/order";
import { confirmOrderStories } from "./confirm-order.story.shared";

confirmOrderStories(new OrderRepository());
