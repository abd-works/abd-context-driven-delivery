import { useState } from 'react';
import extra from '@example/ghost';

export class RecipientManager {
  process() {
    return useState;
  }

  filterByStatus(status: string) {
    return status;
  }
}

export class Bag {
  x: number;
  beneficiary_bank: string;
  constructor(x: number) {
    this.x = x;
    this.beneficiary_bank = '';
  }
}

export interface Recipient_Data {
  beneficiary_bank: string;
}

export interface RecipientRepository {
  find(id: string): void;
}
