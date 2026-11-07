/**
 * Example domain aggregates for Onboard A Customer.
 */

export interface ACustomer {
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}

export const activeACustomerExample: ACustomer = {
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
};

export const pendingACustomerExample: ACustomer = {
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
};

export const suspendedACustomerExample: ACustomer = {
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
};
