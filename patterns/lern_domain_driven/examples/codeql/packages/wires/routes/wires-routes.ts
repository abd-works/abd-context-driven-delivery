import { Router } from "express";

const router = Router();

router.get("/next", (_req, res) => {
  res.redirect("/wires/start");
});

export default router;
