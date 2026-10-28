import { planRepository } from '../../../../domain/plans/PlanRepository';
import { purchasablePlansExamples } from '../../examples/purchasable-plans.examples';

export async function seedPurchasableCatalog(): Promise<void> {
  for (const plan of purchasablePlansExamples) {
    plan.isSellable = true;
  }
  await planRepository.seed(purchasablePlansExamples);
}
