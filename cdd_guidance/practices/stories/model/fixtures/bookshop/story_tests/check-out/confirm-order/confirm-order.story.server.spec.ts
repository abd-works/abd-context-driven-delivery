/** Confirm Order at the server tier: the shared scenarios through the Bookshop's server. */

import { OrderRepository } from "../../../src/bookshop/order";
import { confirmOrderStories } from "./confirm-order.story.shared";

// The server tier keeps its orders behind the Bookshop's HTTP server; this sandbox has none, so it replays on the repository.
confirmOrderStories(new OrderRepository());
