/**
 * Example domain aggregates for Get Number.
 */

export interface Number {
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}

export const activeNumberExample: Number = {
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
};

export const pendingNumberExample: Number = {
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
};

export const suspendedNumberExample: Number = {
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
};
