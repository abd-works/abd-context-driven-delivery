export class Transfer {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
}

export interface TransferRepository {
  find(id: string): void;
}
