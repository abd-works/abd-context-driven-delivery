import { expect, it } from 'vitest';
import { queryProgress } from './query-progress';

it('should keep the latest file count while a practice loads', () => {
  const progress = queryProgress([
    'load: clean_engineering · class names · 1/4 · src/customer/customer.ts',
    'load: clean_engineering · classes · 3/4 · src/account/account.ts',
    'load: clean_engineering · rule hide-inner-details · 2/18 · Account',
  ]);
  expect(progress.headline).toContain('rule hide-inner-details');
  expect(progress.headline).toContain('Account');
  expect(progress.index).toBe(2);
  expect(progress.total).toBe(18);
});
