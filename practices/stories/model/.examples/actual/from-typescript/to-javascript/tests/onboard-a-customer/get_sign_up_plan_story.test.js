/**
 * Epic: Get Sign Up Plan
 * Orders: 0.0.5
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Open Plan Deep Link
 */

story('Open Plan Deep Link', () => {
    scenario('Unknown plan deep link', ({ given, when, then }) => {
      given('the plan catalog contains purchasable plans', () => {}).but('the deep-link plan id is not in the catalog', () => {});
      when('the Customer opens a plan deep link', () => {});
      then('the plan is not found', () => {});
    });
});

/**
 * Story: Apply Catalog Voucher
 */

story('Apply Catalog Voucher', () => {
    scenario('Apply Catalog Voucher via deep link', ({ given, when, then }) => {
      given('the plan catalog contains purchasable plans', () => {}).and('Vouchera has valid catalog voucher', () => {});
      when('the Customer applies valid catalog voucher from a promotional voucher link', () => {});
      then('My Paradise sends the voucher code to Vouchera', () => {});
      when('Vouchera returns the voucher view', () => {});
      then('the catalog voucher is applied', () => {}).and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {});
    });
    scenario('Apply Catalog Voucher manually', ({ given, when, then }) => {
      given('the Customer is selecting a plan', () => {}).and('Vouchera has valid catalog voucher', () => {});
      when('the Customer applies valid catalog voucher', () => {});
      then('My Paradise sends the voucher code to Vouchera', () => {});
      when('Vouchera returns the voucher view', () => {});
      then('the catalog voucher is applied', () => {}).and('the voucher discounts Essentials, Data Freedom, Ace, and Atlas by 10 percent', () => {});
    });
    scenario('Short catalog voucher code is rejected', ({ given, when, then }) => {
      given('the Customer is selecting a plan', () => {});
      then('the catalog voucher is rejected', () => {}).and('Vouchera is not asked for the voucher', () => {});
    });
    scenario('Remove Catalog Voucher', ({ given, when, then }) => {
      given('the Customer is selecting a plan with valid catalog voucher applied', () => {});
      when('the Customer removes valid catalog voucher', () => {});
      then('the catalog has no catalog voucher', () => {});
    });
});
