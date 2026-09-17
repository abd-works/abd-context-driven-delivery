/**
 * Example domain aggregates and reusable steps for {Sub-Epic Verb-Noun}.
 */

export interface {AggregateNoun} {
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}

// Example aggregates (aggs) that the steps refer to
export const active{AggregateNoun}Example: {AggregateNoun} = {
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
};

export const pending{AggregateNoun}Example: {AggregateNoun} = {
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
};

export const suspended{AggregateNoun}Example: {AggregateNoun} = {
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
};

/**
 * Reusable Given step referring to the aggregate examples
 */
export async function givenA{AggregateNoun}Exists(agg: {AggregateNoun}): Promise<void> {
  // TODO: implement reusable given step using the aggregate example
}

/**
 * Reusable When step referring to the aggregate examples
 */
export async function whenTheUserInteractsWithA{AggregateNoun}(agg: {AggregateNoun}): Promise<void> {
  // TODO: implement reusable when step using the aggregate example
}

/**
 * Reusable Then step referring to the aggregate examples
 */
export async function thenThe{AggregateNoun}IsUpdated(agg: {AggregateNoun}): Promise<void> {
  // TODO: implement reusable then step using the aggregate example
}
