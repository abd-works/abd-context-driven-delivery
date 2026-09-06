import {
  Recipient,
  BeneficiaryBank,
  IntermediateBank,
  RecipientStatus,
} from '@channelone/recipients-shared';

/** Client-tier Recipient — extends shared entity with presentation behavior. */
export class RecipientClient extends Recipient {
  constructor(
    id: string,
    enterpriseId: string,
    name: string,
    accountNumber: string,
    accountNumberFull: string,
    status: RecipientStatus,
    beneficiaryBank: BeneficiaryBank,
    intermediateBank: IntermediateBank | undefined,
    createdAt: Date,
    activatedAt: Date | undefined,
  ) {
    super(
      id,
      enterpriseId,
      name,
      accountNumber,
      accountNumberFull,
      status,
      beneficiaryBank,
      intermediateBank,
      createdAt,
      activatedAt,
    );
  }

  static fromRecipient(recipient: Recipient): RecipientClient {
    return new RecipientClient(
      recipient.id,
      recipient.enterpriseId,
      recipient.name,
      recipient.accountNumber,
      recipient.accountNumberFull,
      recipient.status,
      recipient.beneficiaryBank,
      recipient.intermediateBank,
      recipient.createdAt,
      recipient.activatedAt,
    );
  }

  get bankName(): string {
    return this.beneficiaryBank.name;
  }

  cardCssClass(isSelected: boolean): string {
    return `recipient-card${isSelected ? ' selected' : ''}`;
  }

  static key(id: string): string {
    return `recipient-${id}`;
  }
}
