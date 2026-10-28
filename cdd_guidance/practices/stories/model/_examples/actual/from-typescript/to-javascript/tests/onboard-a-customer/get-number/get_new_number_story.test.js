/**
 * Epic: Get New Number
 * Orders: 0.0.1.1
 */

import { background, scenario, story } from "../../story-test.js";
import { storedHeldAvailableNumber, enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart, stubBundle, expectedChosenAvailableNumber, reloadCart } from "./examples";

/**
 * Story: Determine Number
 */

story('Determine Number', () => {
  // typescript body to translate:
  // let listResourcesSpy: MockInstance<typeof mavenirMsisdnGateway.listResources>;
  // let searchResourcesSpy: MockInstance<typeof mavenirMsisdnGateway.searchResources>;
  //
  // beforeEach(() => {
  //   listResourcesSpy = vi.spyOn(mavenirMsisdnGateway, 'listResources');
  //   searchResourcesSpy = vi.spyOn(mavenirMsisdnGateway, 'searchResources');
  // });
  scenario('View available numbers', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let numbers: string[] | Error;
    // examples: storedHeldAvailableNumber, enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
    given('a My Paradise customer with a Mavenir shopping cart and no MSISDN', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart();
      // TODO: implement step
    });
    when('the Customer loads available numbers', () => {
      // typescript body to translate:
      // numbers = cart.line!.getNumbers();
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // typescript body to translate:
      // expect(listResourcesSpy).toHaveBeenCalledOnce();
      // TODO: implement step
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {
      // TODO: implement step
    });
    then('My Paradise returns the available numbers', () => {
      // typescript body to translate:
      // expect(numbers).toEqual(storedAvailableNumbers);
      // TODO: implement step
    })
      .and('${storedHeldAvailableNumber} and ${enteredChosenAvailableNumber} are in the Available Number list', () => {
        // typescript body to translate:
        // expect(numbers as string[]).toContain(storedHeldAvailableNumber);
        // expect(numbers as string[]).toContain(enteredChosenAvailableNumber);
        // TODO: implement step
      });
  });

  scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let numbers: string[] | Error;
    // examples: storedHeldAvailableNumber, storedAvailableNumbers, customerWithCart, stubBundle
    given('MSISDN ${storedHeldAvailableNumber} is in the Mavenir shopping cart', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart('cus_1', { bundleId: stubBundle.id, msisdn: storedHeldAvailableNumber });
      // TODO: implement step
    });
    when('the Customer loads available numbers', () => {
      // typescript body to translate:
      // numbers = cart.line!.getNumbers();
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // typescript body to translate:
      // expect(listResourcesSpy).toHaveBeenCalledOnce();
      // TODO: implement step
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {
      // TODO: implement step
    });
    then('the Customer sees their number is ${storedHeldAvailableNumber}', () => {
      // typescript body to translate:
      // expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
      // TODO: implement step
    })
      .and('My Paradise returns the available numbers', () => {
        // typescript body to translate:
        // expect(numbers).toEqual(storedAvailableNumbers);
        // TODO: implement step
      });
  });

  scenario('Refresh available numbers', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let refreshedNumbers: string[] | Error;
    // examples: storedAvailableNumbers, customerWithCart
    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart();
      // TODO: implement step
    });
    when('the Customer refreshes the number list', () => {
      // typescript body to translate:
      // refreshedNumbers = cart.line!.getNumbers();
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // typescript body to translate:
      // expect(listResourcesSpy).toHaveBeenCalledOnce();
      // TODO: implement step
    });
    when('Mavenir locks 20 MSISDN resources and returns the available numbers', () => {
      // TODO: implement step
    });
    then('My Paradise returns a fresh set of available numbers', () => {
      // typescript body to translate:
      // expect(refreshedNumbers).toEqual(storedAvailableNumbers);
      // TODO: implement step
    });
  });

  scenario('Search for a number', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let searchResults: string[] | Error;
    // const searchNumbers = ['5263712345', '5263798765'];
    // examples: customerWithCart
    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(searchNumbers);
      // cart = await customerWithCart();
      // TODO: implement step
    });
    when('the Customer searches for numbers matching JAMES (52637)', () => {
      // typescript body to translate:
      // searchResults = cart.line!.searchNumbers('52637');
      // TODO: implement step
    });
    then('My Paradise sends the search request to Mavenir with pattern 52637', () => {
      // typescript body to translate:
      // expect(searchResourcesSpy).toHaveBeenCalledWith('52637');
      // TODO: implement step
    });
    when('Mavenir locks MSISDN resources matching 52637 and returns matching values', () => {
      // TODO: implement step
    });
    then('My Paradise returns Available Numbers matching 52637', () => {
      // typescript body to translate:
      // expect(searchResults).toEqual(searchNumbers);
      // TODO: implement step
    })
      .and('the matching numbers are stored on the line for selection', () => {
        // typescript body to translate:
        // expect(cart.line?.availableNumbers).toEqual(searchNumbers);
        // TODO: implement step
      });
  });

  scenario('Numbers locked by another customer are excluded from results', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let numbers: string[] | Error;
    // const otherAvailableNumbers = ['4415550200', '4415550201'];
    // examples: storedHeldAvailableNumber, enteredChosenAvailableNumber, customerWithCart
    given('another customer has already locked the standard available numbers in Mavenir', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(otherAvailableNumbers);
      // cart = await customerWithCart();
      // TODO: implement step
    });
    when('the Customer loads available numbers', () => {
      // typescript body to translate:
      // numbers = cart.line!.getNumbers();
      // TODO: implement step
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      // typescript body to translate:
      // expect(listResourcesSpy).toHaveBeenCalledOnce();
      // TODO: implement step
    });
    when('Mavenir returns only available numbers, excluding the locked ones', () => {
      // TODO: implement step
    });
    then('the locked numbers are not in the available numbers list', () => {
      // typescript body to translate:
      // expect(numbers).not.toContain(storedHeldAvailableNumber);
      // expect(numbers).not.toContain(enteredChosenAvailableNumber);
      // TODO: implement step
    })
      .and('only the currently available numbers are returned', () => {
        // typescript body to translate:
        // expect(numbers).toEqual(otherAvailableNumbers);
        // TODO: implement step
      });
  });
});

/**
 * Story: Choose a Number
 */

story('Choose a Number', () => {
  // typescript body to translate:
  // let reserveResourceSpy: MockInstance<typeof mavenirMsisdnGateway.reserveResource>;
  // let patchCartWithNumberSpy: MockInstance<typeof shoppingCartGateway.patchCartWithNumber>;
  //
  // beforeEach(() => {
  //   reserveResourceSpy = vi.spyOn(mavenirMsisdnGateway, 'reserveResource');
  //   patchCartWithNumberSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithNumber');
  // });
  scenario('Pick number', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: enteredChosenAvailableNumber, expectedChosenAvailableNumber, storedAvailableNumbers, customerWithCart, reloadCart, stubBundle
    given('Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list and no MSISDN is in the cart', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
      // cart.line!.availableNumbers = storedAvailableNumbers;
      // TODO: implement step
    });
    when('My Paradise reserves ${enteredChosenAvailableNumber} in Mavenir and patches the shopping cart', () => {
      // typescript body to translate:
      // cart.line!.reserveNumber(enteredChosenAvailableNumber);
      // TODO: implement step
    });
    then('My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber}', () => {
      // typescript body to translate:
      // expect(reserveResourceSpy).toHaveBeenCalledWith(enteredChosenAvailableNumber, undefined);
      // TODO: implement step
    })
      .and('My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber}', () => {
        // typescript body to translate:
        // expect(patchCartWithNumberSpy).toHaveBeenCalledWith('cus_1', enteredChosenAvailableNumber);
        // TODO: implement step
      });
    when('Mavenir confirms the reservation and patches the cart', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores ${expectedChosenAvailableNumber} on the line', () => {
      // typescript body to translate:
      // expect(cart.line?.msisdn).toBe(expectedChosenAvailableNumber);
      // TODO: implement step
    })
      .and('the Customer is forwarded to Select Sim', () => {
        // typescript body to translate:
        // expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
        // TODO: implement step
      });
  });

  scenario('Pick number — replace existing', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // examples: storedHeldAvailableNumber, enteredChosenAvailableNumber, expectedChosenAvailableNumber, storedAvailableNumbers, customerWithCart, reloadCart, stubBundle
    given('MSISDN ${storedHeldAvailableNumber} is in the cart and Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart('cus_1', { bundleId: stubBundle.id, msisdn: storedHeldAvailableNumber });
      // cart.line!.availableNumbers = storedAvailableNumbers;
      // TODO: implement step
    });
    when('My Paradise reserves ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}', () => {
      // typescript body to translate:
      // cart.line!.reserveNumber(enteredChosenAvailableNumber);
      // TODO: implement step
    });
    then('My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}', () => {
      // typescript body to translate:
      // expect(reserveResourceSpy).toHaveBeenCalledWith(enteredChosenAvailableNumber, storedHeldAvailableNumber);
      // TODO: implement step
    });
    when('Mavenir releases ${storedHeldAvailableNumber} and reserves ${enteredChosenAvailableNumber}', async () => {
      // typescript body to translate:
      // cart = await reloadCart(cart);
      // TODO: implement step
    });
    then('My Paradise stores ${expectedChosenAvailableNumber} on the line', () => {
      // typescript body to translate:
      // expect(cart.line?.msisdn).toBe(expectedChosenAvailableNumber);
      // TODO: implement step
    });
  });

  scenario('Reserve number request fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: void | Error;
    // examples: enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
    given('Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list but reserve returns an error', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart();
      // cart.line!.availableNumbers = storedAvailableNumbers;
      // mavenirMsisdnGateway.seedReserveError(new Error('Failed to reserve'));
      // TODO: implement step
    });
    when('My Paradise attempts to reserve ${enteredChosenAvailableNumber} but Mavenir returns an error', () => {
      // typescript body to translate:
      // result = cart.line!.reserveNumber(enteredChosenAvailableNumber);
      // TODO: implement step
    });
    then('My Paradise shows Failed to reserve your number.', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // TODO: implement step
    });
  });

  scenario('Patch cart with number fails', ({ given, when, then }) => {
    // typescript body to translate:
    // let cart: Cart;
    // let result: void | Error;
    // examples: enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
    given('Mavenir has reserved ${enteredChosenAvailableNumber} but patching the cart returns an error', async () => {
      // typescript body to translate:
      // mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      // cart = await customerWithCart();
      // cart.line!.availableNumbers = storedAvailableNumbers;
      // shoppingCartGateway.seedPatchCartWithNumberError(new Error('Failed to update cart'));
      // TODO: implement step
    });
    when('My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber} but Mavenir returns an error', () => {
      // typescript body to translate:
      // result = cart.line!.reserveNumber(enteredChosenAvailableNumber);
      // TODO: implement step
    });
    then('My Paradise shows Failed to update your cart.', () => {
      // typescript body to translate:
      // expect(result).toBeInstanceOf(Error);
      // TODO: implement step
    });
  });
});
