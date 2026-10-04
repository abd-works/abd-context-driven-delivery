import { recipientRepository } from "./recipient-repository";
export function seedRecipient() {
  return recipientRepository.new();
}
