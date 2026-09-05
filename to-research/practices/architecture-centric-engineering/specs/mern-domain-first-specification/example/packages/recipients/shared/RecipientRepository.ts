import { Recipient } from './Recipient';

export interface RecipientRepository {
  findAll(): Promise<Recipient[]>;
  findByIds(ids: string[]): Promise<Recipient[]>;
  findByEnterprise(enterpriseId: string): Promise<Recipient[]>;
}
