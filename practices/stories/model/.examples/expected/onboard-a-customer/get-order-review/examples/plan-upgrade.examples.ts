import type { Plan } from '../../../../domain/plans/Plan';
import { purchasablePlansExamples } from '../../examples/purchasable-plans.examples';

const essentials = purchasablePlansExamples.find(p => p.name === 'Essentials')!;
const dataFreedom = purchasablePlansExamples.find(p => p.name === 'Data Freedom')!;
const ace = purchasablePlansExamples.find(p => p.name === 'Ace')!;
const atlas = purchasablePlansExamples.find(p => p.name === 'Atlas')!;

export { essentials, dataFreedom, ace, atlas };

export const upgradeOutlines: Array<{ example: string; currentPlan: Plan; newPlan: Plan }> = [
  { example: 'upgrade to Data Freedom', currentPlan: essentials, newPlan: dataFreedom },
  { example: 'upgrade to Ace',          currentPlan: dataFreedom, newPlan: ace },
  { example: 'upgrade to Atlas',        currentPlan: ace,         newPlan: atlas },
];
