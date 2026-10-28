/**
 * ++Plan++ examples shared by Enter Account Credentials background.
 * Source: stories/onboard-a-customer/story-scenarios.md
 */

import { Plan } from '../../../domain/plans/Plan';

function catalogPlan(
  id: string,
  name: string,
  price: number,
  opts?: { isSellable?: boolean; tagName?: string | null; bypassVerified?: boolean },
): Plan {
  return new Plan(
    id,
    name,
    name,
    price,
    0,
    price,
    [],
    opts?.isSellable ?? true,
    opts?.tagName ?? null,
    opts?.bypassVerified ?? false,
  );
}

export const essentials = catalogPlan('100000000014', 'Essentials', 70);

export const purchasablePlansExamples: Plan[] = [
  essentials,
  catalogPlan('100000000019', 'Data Freedom', 55),
  catalogPlan('100000000042', 'Ace', 99, { tagName: 'Best value' }),
  catalogPlan('100000000041', 'Atlas', 129),
];

export const internalTestPlan = catalogPlan('100000000008', 'Internal Test Plan PROMO', 0, {
  isSellable: false,
});
