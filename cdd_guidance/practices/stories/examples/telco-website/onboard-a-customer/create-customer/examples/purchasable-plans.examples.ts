/**
 * ++Plan++ examples — Create Customer sub-epic background catalog.
 * Shared when several stories seed the same catalog.
 */

export const essentials = {
  id: '100000000014',
  name: 'Essentials',
  monthlyPrice: 70,
  purchasable: true,
};

export const purchasablePlansExamples = [
  essentials,
  { id: '100000000019', name: 'Data Freedom', monthlyPrice: 55, purchasable: true },
  { id: '100000000042', name: 'Ace', monthlyPrice: 99, purchasable: true },
];
