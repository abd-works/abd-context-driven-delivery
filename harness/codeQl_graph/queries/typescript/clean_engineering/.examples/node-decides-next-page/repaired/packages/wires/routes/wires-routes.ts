import { Router } from "express";
import { OrdersNode } from "@src/orders/orders-node";
const router = Router();
router.get("next", (_req, res) => {
  res.json(new OrdersNode().destination());
});
export default router;
