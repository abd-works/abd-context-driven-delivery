from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import seedPurchasableCatalog, unknownPlanDeepLinkId, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode, expectedValidCatalogVoucherCode, shortCatalogVoucherCode, VoucherCodeRule, seedAppliedValidCatalogVoucher, seedUnusableCatalogVoucher


# Epic: Get Sign Up Plan
# Orders: 0.0.5

# Story: Open Plan Deep Link
with story("Open Plan Deep Link"):
    # typescript body to translate:
    # purchasablePlansExamples.forEach(plan => {
    # });
        with scenario("Open plan deep link: ${plan.name}"):
            # typescript body to translate:
            # let selected: Plan | Error;
            # examples: seedPurchasableCatalog
            with given("the plan catalog contains purchasable plans and the Customer arrived at sign-up from the Paradise Mobile website"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                pass
            with when("the Customer opens a plan deep link for ${plan.name}"):
                # typescript body to translate:
                # selected = await planRepository.get(plan.id);
                pass
            with then("${plan.name} is selected"):
                # typescript body to translate:
                # expect(selected).toBeInstanceOf(Plan);
                # expect((selected as Plan).id).toBe(plan.id);
                # expect((selected as Plan).name).toBe(plan.name);
                pass
            with and_("the Customer continues to Enter Account Credentials"):
                # typescript body to translate:
                # expect(selected).not.toBeInstanceOf(Error);
                pass
        with scenario("Unknown plan deep link"):
            # typescript body to translate:
            # let selected: Plan | Error;
            # examples: seedPurchasableCatalog, unknownPlanDeepLinkId
            with given("the plan catalog contains purchasable plans"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                pass
            with but_("the deep-link plan id is not in the catalog"):
                pass
            with when("the Customer opens a plan deep link"):
                # typescript body to translate:
                # selected = await planRepository.get(unknownPlanDeepLinkId);
                pass
            with then("the plan is not found"):
                # typescript body to translate:
                # expect(selected).toBeInstanceOf(Error);
                # expect((selected as Error).message).toBe(PlanErrorMessage.NotFound);
                pass

# Story: Apply Catalog Voucher
with story("Apply Catalog Voucher"):
    # typescript body to translate:
    # let getSpy: MockInstance<typeof voucheraGateway.get>;
    #
    # beforeEach(() => {
    #   getSpy = vi.spyOn(voucheraGateway, 'get');
    # });
    #
    # unusableCatalogVoucherOutlines.forEach(({ example, code, seed, voucheraReturns }) => {
    # });
        with scenario("Apply Catalog Voucher via deep link"):
            # typescript body to translate:
            # let result: Voucher | Error;
            # examples: seedPurchasableCatalog, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode, expectedValidCatalogVoucherCode
            with given("the plan catalog contains purchasable plans"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                pass
            with and_("Vouchera has valid catalog voucher"):
                # typescript body to translate:
                # seedValidCatalogVoucher();
                pass
            with when("the Customer applies valid catalog voucher from a promotional voucher link"):
                # typescript body to translate:
                # result = await Voucher.apply(enteredValidCatalogVoucherCode);
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                # typescript body to translate:
                # expect(getSpy).toHaveBeenCalledWith(enteredValidCatalogVoucherCode);
                pass
            with when("Vouchera returns the voucher view"):
                pass
            with then("the catalog voucher is applied"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Voucher);
                # expect(Voucher.applied).toBe(result);
                # expect((result as Voucher).code).toBe(expectedValidCatalogVoucherCode);
                pass
            with and_("the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent"):
                # typescript body to translate:
                # const voucher = result as Voucher;
                # expect(voucher.discount.percent_off).toBe(10);
                # expect(voucher.metadata.planIds).toEqual(purchasablePlanIds);
                pass
        with scenario("Apply Catalog Voucher manually"):
            # typescript body to translate:
            # let result: Voucher | Error;
            # examples: seedPurchasableCatalog, purchasablePlanIds, seedValidCatalogVoucher, enteredValidCatalogVoucherCode
            with given("the Customer is selecting a plan"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                pass
            with and_("Vouchera has valid catalog voucher"):
                # typescript body to translate:
                # seedValidCatalogVoucher();
                pass
            with when("the Customer applies valid catalog voucher"):
                # typescript body to translate:
                # result = await Voucher.apply(enteredValidCatalogVoucherCode);
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                # typescript body to translate:
                # expect(getSpy).toHaveBeenCalledWith(enteredValidCatalogVoucherCode);
                pass
            with when("Vouchera returns the voucher view"):
                pass
            with then("the catalog voucher is applied"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Voucher);
                # expect(Voucher.applied).toBe(result);
                pass
            with and_("the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent"):
                # typescript body to translate:
                # const voucher = result as Voucher;
                # expect(voucher.discount.percent_off).toBe(10);
                # expect(voucher.metadata.planIds).toEqual(purchasablePlanIds);
                pass
        with scenario("Short catalog voucher code is rejected"):
            # typescript body to translate:
            # let result: Voucher | Error;
            # examples: seedPurchasableCatalog, shortCatalogVoucherCode, VoucherCodeRule
            with given("the Customer is selecting a plan"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                pass
            with when("the Customer applies a catalog voucher shorter than ${VoucherCodeRule.MinLength} characters"):
                # typescript body to translate:
                # try { result = await Voucher.apply(shortCatalogVoucherCode); } catch (e) { result = e as Error; }
                pass
            with then("the catalog voucher is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect((result as Error).message).toBe(VoucherErrorMessage.TooShort);
                # expect(Voucher.applied).toBeNull();
                pass
            with and_("Vouchera is not asked for the voucher"):
                # typescript body to translate:
                # expect(getSpy).not.toHaveBeenCalled();
                pass
        with scenario("Remove Catalog Voucher"):
            # examples: seedPurchasableCatalog, seedAppliedValidCatalogVoucher
            with given("the Customer is selecting a plan with valid catalog voucher applied"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                # seedAppliedValidCatalogVoucher();
                pass
            with when("the Customer removes valid catalog voucher"):
                # typescript body to translate:
                # Voucher.remove();
                pass
            with then("the catalog has no catalog voucher"):
                # typescript body to translate:
                # expect(Voucher.applied).toBeNull();
                pass
        with scenario("Apply unusable catalog voucher: ${example}"):
            # typescript body to translate:
            # let result: Voucher | Error;
            #
            # when(voucheraReturns, () => {});
            # examples: seedPurchasableCatalog, seedUnusableCatalogVoucher
            with given("the Customer is selecting a plan"):
                # typescript body to translate:
                # await seedPurchasableCatalog();
                pass
            with and_("Vouchera has ${example}"):
                # typescript body to translate:
                # seedUnusableCatalogVoucher(seed);
                pass
            with when("the Customer applies ${example}"):
                # typescript body to translate:
                # try { result = await Voucher.apply(code); } catch (e) { result = e as Error; }
                pass
            with then("My Paradise sends the voucher code to Vouchera"):
                # typescript body to translate:
                # expect(getSpy).toHaveBeenCalledWith(code);
                pass
            with then("the catalog voucher is rejected"):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                # expect(Voucher.applied).toBeNull();
                pass
