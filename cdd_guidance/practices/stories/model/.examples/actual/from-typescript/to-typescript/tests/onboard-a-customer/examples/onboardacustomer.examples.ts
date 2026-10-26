/**
 * Example domain aggregates for Onboard A Customer.
 */

export interface OnboardACustomer {
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}

export const activeOnboardACustomerExample: OnboardACustomer = {
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
};

export const pendingOnboardACustomerExample: OnboardACustomer = {
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
};

export const suspendedOnboardACustomerExample: OnboardACustomer = {
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
};
