import { z } from 'zod';

/**
 * recipients.ts — domain core (was shared/).
 *
 * Framework-free: no Express, no React, no MongoDB. Schema, entity, collection,
 * and persistence interface live here once; recipient-server.ts and
 * recipient-client.tsx both import from this file (share-domain-logic).
 */

export const BeneficiaryBankSchema = z.object({
  name: z.string().min(1, 'Bank name is required'),
  routingNumber: z.string().length(9, 'Routing number must be 9 digits'),
});

export const RecipientSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1, 'Beneficiary name is required').max(140),
  status: z.enum(['Active', 'Pending', 'Inactive']),
  beneficiaryBank: BeneficiaryBankSchema,
  createdAt: z.coerce.date(),
});

export type RecipientDto = z.infer<typeof RecipientSchema>;

export class Recipient {
  constructor(private readonly dto: RecipientDto) {}

  get id(): string {
    return this.dto.id;
  }

  get name(): string {
    return this.dto.name;
  }

  get bankName(): string {
    return this.dto.beneficiaryBank.name;
  }

  get status(): RecipientDto['status'] {
    return this.dto.status;
  }

  static fromDto(dto: RecipientDto): Recipient {
    return new Recipient(dto);
  }
}

export class Recipients {
  constructor(protected readonly items: Recipient[]) {}

  filterByStatus(status: Recipient['status']): Recipients {
    return new Recipients(this.items.filter((r) => r.status === status));
  }

  toArray(): Recipient[] {
    return [...this.items];
  }

  get length(): number {
    return this.items.length;
  }
}

export interface RecipientRepository {
  findByEnterprise(enterpriseId: string): Promise<Recipient[]>;
}
