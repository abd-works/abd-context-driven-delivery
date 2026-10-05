import { JSONFilePreset } from "lowdb/node";
export async function open() {
  return JSONFilePreset("db.json", { orders: [] });
}
