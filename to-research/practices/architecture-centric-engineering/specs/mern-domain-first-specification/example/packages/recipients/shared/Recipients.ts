import { Recipient } from './Recipient';
import { RecipientStatusType } from './RecipientStatus';

export class Recipients {
  constructor(private readonly items: Recipient[]) {}

  filterByStatus(status: RecipientStatusType): Recipients {
    return new Recipients(this.items.filter(r => r.status.status === status));
  }

  filterByEnterprise(enterpriseId: string): Recipients {
    return new Recipients(this.items.filter(r => r.enterpriseId === enterpriseId));
  }

  search(query: string): Recipients {
    const lower = query.toLowerCase();
    return new Recipients(
      this.items.filter(
        r =>
          r.name.toLowerCase().includes(lower) ||
          r.beneficiaryBank.name.toLowerCase().includes(lower)
      )
    );
  }

  toArray(): Recipient[] {
    return [...this.items];
  }

  get length(): number {
    return this.items.length;
  }
}
