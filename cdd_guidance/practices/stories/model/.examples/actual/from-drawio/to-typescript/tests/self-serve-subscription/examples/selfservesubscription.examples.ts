/**
 * Example domain aggregates for Self-Serve Subscription.
 */

export interface SelfServeSubscription {
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}

export const activeSelfServeSubscriptionExample: SelfServeSubscription = {
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
};

export const pendingSelfServeSubscriptionExample: SelfServeSubscription = {
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
};

export const suspendedSelfServeSubscriptionExample: SelfServeSubscription = {
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
};
