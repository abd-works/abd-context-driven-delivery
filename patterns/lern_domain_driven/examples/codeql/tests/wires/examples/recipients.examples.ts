import { recipientRepository } from "../../packages/wires/recipients/recipients";

export function seedRecipient() {
  return recipientRepository.new();
}
