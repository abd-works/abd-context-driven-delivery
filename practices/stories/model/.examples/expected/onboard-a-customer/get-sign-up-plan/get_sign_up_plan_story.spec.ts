import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { Plan } from '../../../domain/plans/Plan';
import { PlanErrorMessage, planRepository } from '../../../domain/plans/PlanRepository';
import { Voucher } from '../../../domain/cart/Voucher';
import { VoucherErrorMessage, voucheraGateway } from '../../../domain/systems/vouchera';
import { purchasablePlansExamples } from '../examples/purchasable-plans.examples';
import { seedPurchasableCatalog } from './examples/catalog.examples';
import {
  purchasablePlanIds,
  seedAppliedValidCatalogVoucher,
  seedUnusableCatalogVoucher,
  seedValidCatalogVoucher,
  shortCatalogVoucherCode,
  unknownPlanDeepLinkId,
  unusableCatalogVoucherOutlines,
  enteredValidCatalogVoucherCode,
  expectedValidCatalogVoucherCode,
  VoucherCodeRule,
} from './examples/catalog-voucher.examples';

afterEach(() => {
  planRepository.reset();
  voucheraGateway.reset();
  Voucher.remove();
  vi.restoreAllMocks();
});

// ─────────────────────────────────────────────────────────────────────────────

story('Open Plan Deep Link', () => {
  purchasablePlansExamples.forEach(plan => {
    scenario(`Open plan deep link: ${plan.name}`, ({ given, when, then }) => {
      let selected: Plan | Error;

      given('the plan catalog contains purchasable plans and the Customer arrived at sign-up from the Paradise Mobile website', async () => {
        await seedPurchasableCatalog();
      });
      when(`the Customer opens a plan deep link for ${plan.name}`, async () => {
        selected = await planRepository.get(plan.id);
      });
      then(`${plan.name} is selected`, () => {
        expect(selected).toBeInstanceOf(Plan);
        expect((selected as Plan).id).toBe(plan.id);
        expect((selected as Plan).name).toBe(plan.name);
      }).and('the Customer continues to Enter Account Credentials', () => {
        expect(selected).not.toBeInstanceOf(Error);
      });
    });
  });

  scenario('Unknown plan deep link', ({ given, when, then }) => {
    let selected: Plan | Error;

    given('the plan catalog contains purchasable plans', async () => {
      await seedPurchasableCatalog();
    }).but('the deep-link plan id is not in the catalog', () => {});
    when('the Customer opens a plan deep link', async () => {
      selected = await planRepository.get(unknownPlanDeepLinkId);
    });
    then('the plan is not found', () => {
      expect(selected).toBeInstanceOf(Error);
      expect((selected as Error).message).toBe(PlanErrorMessage.NotFound);
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────

story('Apply Catalog Voucher', () => {
  let getSpy: MockInstance<typeof voucheraGateway.get>;

  beforeEach(() => {
    getSpy = vi.spyOn(voucheraGateway, 'get');
  });

  scenario('Apply Catalog Voucher via deep link', ({ given, when, then }) => {
    let result: Voucher | Error;

    given('the plan catalog contains purchasable plans', async () => {
      await seedPurchasableCatalog();
    }).and('Vouchera has valid catalog voucher', () => {
      seedValidCatalogVoucher();
    });
    when('the Customer applies valid catalog voucher from a promotional voucher link', async () => {
      result = await Voucher.apply(enteredValidCatalogVoucherCode);
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      expect(getSpy).toHaveBeenCalledWith(enteredValidCatalogVoucherCode);
    });
    when('Vouchera returns the voucher view', () => {});
    then('the catalog voucher is applied', () => {
      expect(result).toBeInstanceOf(Voucher);
      expect(Voucher.applied).toBe(result);
      expect((result as Voucher).code).toBe(expectedValidCatalogVoucherCode);
    }).and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {
      const voucher = result as Voucher;
      expect(voucher.discount.percent_off).toBe(10);
      expect(voucher.metadata.planIds).toEqual(purchasablePlanIds);
    });
  });

  scenario('Apply Catalog Voucher manually', ({ given, when, then }) => {
    let result: Voucher | Error;

    given('the Customer is selecting a plan', async () => {
      await seedPurchasableCatalog();
    }).and('Vouchera has valid catalog voucher', () => {
      seedValidCatalogVoucher();
    });
    when('the Customer applies valid catalog voucher', async () => {
      result = await Voucher.apply(enteredValidCatalogVoucherCode);
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      expect(getSpy).toHaveBeenCalledWith(enteredValidCatalogVoucherCode);
    });
    when('Vouchera returns the voucher view', () => {});
    then('the catalog voucher is applied', () => {
      expect(result).toBeInstanceOf(Voucher);
      expect(Voucher.applied).toBe(result);
    }).and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {
      const voucher = result as Voucher;
      expect(voucher.discount.percent_off).toBe(10);
      expect(voucher.metadata.planIds).toEqual(purchasablePlanIds);
    });
  });

  scenario('Short catalog voucher code is rejected', ({ given, when, then }) => {
    let result: Voucher | Error;

    given('the Customer is selecting a plan', async () => {
      await seedPurchasableCatalog();
    });
    when(`the Customer applies a catalog voucher shorter than ${VoucherCodeRule.MinLength} characters`, async () => {
      try { result = await Voucher.apply(shortCatalogVoucherCode); } catch (e) { result = e as Error; }
    });
    then('the catalog voucher is rejected', () => {
      expect(result).toBeInstanceOf(Error);
      expect((result as Error).message).toBe(VoucherErrorMessage.TooShort);
      expect(Voucher.applied).toBeNull();
    }).and('Vouchera is not asked for the voucher', () => {
      expect(getSpy).not.toHaveBeenCalled();
    });
  });

  scenario('Remove Catalog Voucher', ({ given, when, then }) => {
    given('the Customer is selecting a plan with valid catalog voucher applied', async () => {
      await seedPurchasableCatalog();
      seedAppliedValidCatalogVoucher();
    });
    when('the Customer removes valid catalog voucher', () => {
      Voucher.remove();
    });
    then('the catalog has no catalog voucher', () => {
      expect(Voucher.applied).toBeNull();
    });
  });

  unusableCatalogVoucherOutlines.forEach(({ example, code, seed, voucheraReturns }) => {
    scenario(`Apply unusable catalog voucher: ${example}`, ({ given, when, then }) => {
      let result: Voucher | Error;

      given('the Customer is selecting a plan', async () => {
        await seedPurchasableCatalog();
      }).and(`Vouchera has ${example}`, () => {
        seedUnusableCatalogVoucher(seed);
      });
      when(`the Customer applies ${example}`, async () => {
        try { result = await Voucher.apply(code); } catch (e) { result = e as Error; }
      });
      then('My Paradise sends the voucher code to Vouchera', () => {
        expect(getSpy).toHaveBeenCalledWith(code);
      });
      when(voucheraReturns, () => {});
      then('the catalog voucher is rejected', () => {
        expect(result).toBeInstanceOf(Error);
        expect(Voucher.applied).toBeNull();
      });
    });
  });
});
