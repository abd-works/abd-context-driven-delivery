import { RecipientStatus, RecipientStatusType } from './RecipientStatus';
import { RecipientDTO } from './recipient.schema';

export interface BeneficiaryBank {
  swiftBic: string;
  abaRouting?: string;
  name: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  country: string;
}

export interface IntermediateBank {
  swiftBic: string;
  name: string;
}

export class Recipient {
  constructor(
    public readonly id: string,
    public readonly enterpriseId: string,
    public readonly name: string,
    public readonly accountNumber: string,
    public readonly accountNumberFull: string,
    public readonly status: RecipientStatus,
    public readonly beneficiaryBank: BeneficiaryBank,
    public readonly intermediateBank: IntermediateBank | undefined,
    public readonly createdAt: Date,
    public readonly activatedAt: Date | undefined,
  ) {}

  isEligibleForPayment(): boolean {
    return this.status.isEligibleForPayment();
  }

  static fromDto(dto: RecipientDTO): Recipient {
    return new Recipient(
      dto.id,
      dto.enterpriseId,
      dto.name,
      dto.accountNumber,
      dto.accountNumberFull,
      new RecipientStatus(dto.status, dto.createdAt),
      dto.beneficiaryBank,
      dto.intermediateBank,
      dto.createdAt,
      dto.activatedAt,
    );
  }
}

export type { RecipientStatusType };
