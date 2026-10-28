/**
 * Epic: Get Sign Up Plan
 * Orders: 0.0.5
 */

import { background, scenario, story } from "../story-test.js";
import { seedPurchasableCatalog, unknownPlanDeepLinkId, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode, expectedValidCatalogVoucherCode, shortCatalogVoucherCode, VoucherCodeRule, seedAppliedValidCatalogVoucher, seedUnusableCatalogVoucher } from "./examples";

/**
 * Story: Open Plan Deep Link
 */

story('Open Plan Deep Link', () => {
  // typescript body to translate:
  // purchasablePlansExamples.forEach(plan => {
  // });
  scenario('Open plan deep link: ${plan.name}', ({ given, when, then }) => {
    // typescript body to translate:
    // let selected: Plan | Error;
    // examples: seedPurchasableCatalog
    given('the plan catalog contains purchasable plans and the Customer arrived at sign-up from the Paradise Mobile website', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // TODO: implement step
    });
    when('the Customer opens a plan deep link for ${plan.name}', async () => {
      // typescript body to translate:
      // selected = await planRepository.get(plan.id);
      // TODO: implement step
    });
    then('${plan.name} is selected', () => {
      // typescript body to translate:
      // expect(selected).toBeInstanceOf(Plan);
      // expect((selected as Plan).id).toBe(plan.id);
      // expect((selected as Plan).name).toBe(plan.name);
      // TODO: implement step
    })
      .and('the Customer continues to Enter Account Credentials', () => {
        // typescript body to translate:
        // expect(selected).not.toBeInstanceOf(Error);
        // TODO: implement step
      });
  });

  scenario('Unknown plan deep link', ({ given, when, then }) => {
    // typescript body to translate:
    // let selected: Plan | Error;
    // examples: seedPurchasableCatalog, unknownPlanDeepLinkId
    given('the plan catalog contains purchasable plans', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // TODO: implement step
    })
      .but('the deep-link plan id is not in the catalog', () => {
        // TODO: implement step
      });
    when('the Customer opens a plan deep link', async () => {
      // typescript body to translate:
      // selected = await planRepository.get(unknownPlanDeepLinkId);
      // TODO: implement step
    });
    then('the plan is not found', () => {
      // typescript body to translate:
      // expect(selected).toBeInstanceOf(Error);
      // expect((selected as Error).message).toBe(PlanErrorMessage.NotFound);
      // TODO: implement step
    });
  });
});

/**
 * Story: Apply Catalog Voucher
 */

story('Apply Catalog Voucher', () => {
  // typescript body to translate:
  // let getSpy: MockInstance<typeof voucheraGateway.get>;
  //
  // beforeEach(() => {
  //   getSpy = vi.spyOn(voucheraGateway, 'get');
  // });
  //
  // unusableCatalogVoucherOutlines.forEach(({ example, code, seed, voucheraReturns }) => {
  // });
  scenario('Apply Catalog Voucher via deep link', ({ given, when, then }) => {
    // typescript body to translate:
    // let result: Voucher | Error;
    // examples: seedPurchasableCatalog, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode, expectedValidCatalogVoucherCode
    given('the plan catalog contains purchasable plans', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // TODO: implement step
    })
      .and('Vouchera has valid catalog voucher', () => {
        // typescript body to translate:
        // seedValidCatalogVoucher();
        // TODO: implement step
      });
    when('the Customer applies valid catalog voucher from a promotional voucher link', async () => {
      // typescript body to translate:
      // result = await Voucher.apply(enteredValidCatalogVoucherCode);
      // TODO: implement step
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      // typescript body to translate:
      // expect(getSpy).toHaveBeenCalledWith(enteredValidCatalogVoucherCode);
      // TODO: implement step
    });
    when('Vouchera returns the voucher view', () => {
      // TODO: implement step
    });
    then('the catalog voucher is applied', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Voucher);
      // expect(Voucher.applied).toBe(result);
      // expect((result as Voucher).code).toBe(expectedValidCatalogVoucherCode);
      // TODO: implement step
    })
      .and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {
        // typescript body to translate:
        // const voucher = result as Voucher;
        // expect(voucher.discount.percent_off).toBe(10);
        // expect(voucher.metadata.planIds).toEqual(purchasablePlanIds);
        // TODO: implement step
      });
  });

  scenario('Apply Catalog Voucher manually', ({ given, when, then }) => {
    // typescript body to translate:
    // let result: Voucher | Error;
    // examples: seedPurchasableCatalog, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode
    given('the Customer is selecting a plan', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // TODO: implement step
    })
      .and('Vouchera has valid catalog voucher', () => {
        // typescript body to translate:
        // seedValidCatalogVoucher();
        // TODO: implement step
      });
    when('the Customer applies valid catalog voucher', async () => {
      // typescript body to translate:
      // result = await Voucher.apply(enteredValidCatalogVoucherCode);
      // TODO: implement step
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      // typescript body to translate:
      // expect(getSpy).toHaveBeenCalledWith(enteredValidCatalogVoucherCode);
      // TODO: implement step
    });
    when('Vouchera returns the voucher view', () => {
      // TODO: implement step
    });
    then('the catalog voucher is applied', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Voucher);
      // expect(Voucher.applied).toBe(result);
      // TODO: implement step
    })
      .and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {
        // typescript body to translate:
        // const voucher = result as Voucher;
        // expect(voucher.discount.percent_off).toBe(10);
        // expect(voucher.metadata.planIds).toEqual(purchasablePlanIds);
        // TODO: implement step
      });
  });

  scenario('Short catalog voucher code is rejected', ({ given, when, then }) => {
    // typescript body to translate:
    // let result: Voucher | Error;
    // examples: seedPurchasableCatalog, shortCatalogVoucherCode, VoucherCodeRule
    given('the Customer is selecting a plan', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // TODO: implement step
    });
    when('the Customer applies a catalog voucher shorter than ${VoucherCodeRule.MinLength} characters', async () => {
      // typescript body to translate:
      // try { result = await Voucher.apply(shortCatalogVoucherCode); } catch (e) { result = e as Error; }
      // TODO: implement step
    });
    then('the catalog voucher is rejected', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // expect((result as Error).message).toBe(VoucherErrorMessage.TooShort);
      // expect(Voucher.applied).toBeNull();
      // TODO: implement step
    })
      .and('Vouchera is not asked for the voucher', () => {
        // typescript body to translate:
        // expect(getSpy).not.toHaveBeenCalled();
        // TODO: implement step
      });
  });

  scenario('Remove Catalog Voucher', ({ given, when, then }) => {
    // examples: seedPurchasableCatalog, seedAppliedValidCatalogVoucher
    given('the Customer is selecting a plan with valid catalog voucher applied', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // seedAppliedValidCatalogVoucher();
      // TODO: implement step
    });
    when('the Customer removes valid catalog voucher', () => {
      // typescript body to translate:
      // Voucher.remove();
      // TODO: implement step
    });
    then('the catalog has no catalog voucher', () => {
      // typescript body to translate:
      // expect(Voucher.applied).toBeNull();
      // TODO: implement step
    });
  });

  scenario('Apply unusable catalog voucher: ${example}', ({ given, when, then }) => {
    // typescript body to translate:
    // let result: Voucher | Error;
    //
    // when(voucheraReturns, () => {});
    // examples: seedPurchasableCatalog, seedUnusableCatalogVoucher
    given('the Customer is selecting a plan', async () => {
      // typescript body to translate:
      // await seedPurchasableCatalog();
      // TODO: implement step
    })
      .and('Vouchera has ${example}', () => {
        // typescript body to translate:
        // seedUnusableCatalogVoucher(seed);
        // TODO: implement step
      });
    when('the Customer applies ${example}', async () => {
      // typescript body to translate:
      // try { result = await Voucher.apply(code); } catch (e) { result = e as Error; }
      // TODO: implement step
    });
    then('My Paradise sends the voucher code to Vouchera', () => {
      // typescript body to translate:
      // expect(getSpy).toHaveBeenCalledWith(code);
      // TODO: implement step
    })
      .and('the catalog voucher is rejected', () => {
        // typescript body to translate:
        // expect(result).toBeInstanceOf(Error);
        // expect(Voucher.applied).toBeNull();
        // TODO: implement step
      });
  });
});
