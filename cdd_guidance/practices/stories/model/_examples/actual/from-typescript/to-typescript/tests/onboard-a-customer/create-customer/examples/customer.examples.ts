/**
 * Example domain aggregates for Create Customer.
 */

export interface Customer {
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}

export const activeCustomerExample: Customer = {
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
};

export const pendingCustomerExample: Customer = {
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
};

export const suspendedCustomerExample: Customer = {
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
};
