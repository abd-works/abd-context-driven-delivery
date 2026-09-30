/**
 * Epic: Get Sign Up Plan
 * Orders: 0.0.0
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Open Plan Deep Link
 * Actor: Customer
 */

story('Open Plan Deep Link', () => {
    scenario('Open Plan Deep Link', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      // background-step: And | the Customer arrived at sign-up from the Paradise Mobile website
      when('the Customer opens a plan deep link for ++plan++ ++{scenario}++', () => {});
      then('++{scenario}++ is selected', () => {}).and('the Customer continues to Enter Account Credentials', () => {});
    });
    scenario('Unknown plan deep link', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      // background-step: And | the Customer arrived at sign-up from the Paradise Mobile website
      given('the plan catalog contains purchasable plans', () => {}).but('the deep-link plan id is not in the catalog', () => {});
      when('the Customer opens a plan deep link', () => {});
      then('the plan is not found', () => {});
    });
});

/**
 * Story: Apply Catalog Voucher
 * Actor: Customer
 */

story('Apply Catalog Voucher', () => {
    scenario('Apply Catalog Voucher via deep link', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      given('Vouchera has ++catalog voucher++ ++valid catalog voucher++', () => {});
      when('the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link', () => {});
      then('My Paradise sends the voucher code to Vouchera', () => {});
      when('Vouchera returns the voucher view', () => {});
      then('the catalog voucher is applied', () => {}).and('the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent', () => {});
    });
    scenario('Apply Catalog Voucher manually', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      given('the Customer is selecting a plan', () => {}).and('Vouchera has ++catalog voucher++ ++valid catalog voucher++', () => {});
      when('the Customer applies ++catalog voucher++ ++valid catalog voucher++', () => {});
      then('My Paradise sends the voucher code to Vouchera', () => {});
      when('Vouchera returns the voucher view', () => {});
      then('the catalog voucher is applied', () => {}).and('the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent', () => {});
    });
    scenario('Short catalog voucher code is rejected', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      given('the Customer is selecting a plan', () => {});
      when('the Customer applies a catalog voucher shorter than 4 characters', () => {});
      then('the catalog voucher is rejected', () => {}).and('Vouchera is not asked for the voucher', () => {});
    });
    scenario('Remove Catalog Voucher', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      given('the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied', () => {});
      when('the Customer removes ++catalog voucher++ ++valid catalog voucher++', () => {});
      then('the catalog has no catalog voucher', () => {});
    });
    scenario('Apply unusable catalog voucher', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      given('the Customer is selecting a plan', () => {}).and('Vouchera has ++catalog voucher++ ++{scenario}++', () => {});
      when('the Customer applies ++{scenario}++', () => {});
      then('My Paradise sends the voucher code to Vouchera', () => {});
      when('Vouchera returns', () => {});
      then('the catalog voucher is rejected', () => {});
    });
});
