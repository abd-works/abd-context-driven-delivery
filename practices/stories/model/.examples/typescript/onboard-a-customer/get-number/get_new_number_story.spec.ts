import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { type Cart, OnboardingStep } from '../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { mavenirMsisdnGateway } from '../../../domain/systems/mavenir/msisdn-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';
import {
  storedHeldAvailableNumber,
  enteredChosenAvailableNumber,
  expectedChosenAvailableNumber,
  storedAvailableNumbers,
} from './examples/available-number.examples';
import { customerWithCart, reloadCart, stubBundle } from './examples/cart.examples';

afterEach(() => {
  shoppingCartGateway.reset();
  mavenirMsisdnGateway.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------

story('Determine Number', () => {
  let listResourcesSpy: MockInstance<typeof mavenirMsisdnGateway.listResources>;
  let searchResourcesSpy: MockInstance<typeof mavenirMsisdnGateway.searchResources>;

  beforeEach(() => {
    listResourcesSpy = vi.spyOn(mavenirMsisdnGateway, 'listResources');
    searchResourcesSpy = vi.spyOn(mavenirMsisdnGateway, 'searchResources');
  });

  scenario('View available numbers', ({ given, when, then }) => {
    let cart: Cart;
    let numbers: string[] | Error;

    given('a My Paradise customer with a Mavenir shopping cart and no MSISDN', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      cart = await customerWithCart();
    });
    when('the Customer loads available numbers', () => {
      numbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {});
    then('My Paradise returns the available numbers', () => {
      expect(numbers).toEqual(storedAvailableNumbers);
    }).and(
      `${storedHeldAvailableNumber} and ${enteredChosenAvailableNumber} are in the Available Number list`,
      () => {
        expect(numbers as string[]).toContain(storedHeldAvailableNumber);
        expect(numbers as string[]).toContain(enteredChosenAvailableNumber);
      },
    );
  });

  scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
    let cart: Cart;
    let numbers: string[] | Error;

    given(`MSISDN ${storedHeldAvailableNumber} is in the Mavenir shopping cart`, async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      cart = await customerWithCart('cus_1', { bundleId: stubBundle.id, msisdn: storedHeldAvailableNumber });
    });
    when('the Customer loads available numbers', () => {
      numbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {});
    then(`the Customer sees their number is ${storedHeldAvailableNumber}`, () => {
      expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
    }).and('My Paradise returns the available numbers', () => {
      expect(numbers).toEqual(storedAvailableNumbers);
    });
  });

  scenario('Refresh available numbers', ({ given, when, then }) => {
    let cart: Cart;
    let refreshedNumbers: string[] | Error;

    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      cart = await customerWithCart();
    });
    when('the Customer refreshes the number list', () => {
      refreshedNumbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir locks 20 MSISDN resources and returns the available numbers', () => {});
    then('My Paradise returns a fresh set of available numbers', () => {
      expect(refreshedNumbers).toEqual(storedAvailableNumbers);
    });
  });

  scenario('Search for a number', ({ given, when, then }) => {
    let cart: Cart;
    let searchResults: string[] | Error;
    const searchNumbers = ['5263712345', '5263798765'];

    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(searchNumbers);
      cart = await customerWithCart();
    });
    when('the Customer searches for numbers matching JAMES (52637)', () => {
      searchResults = cart.line!.searchNumbers('52637');
    });
    then('My Paradise sends the search request to Mavenir with pattern 52637', () => {
      expect(searchResourcesSpy).toHaveBeenCalledWith('52637');
    });
    when('Mavenir locks MSISDN resources matching 52637 and returns matching values', () => {});
    then('My Paradise returns Available Numbers matching 52637', () => {
      expect(searchResults).toEqual(searchNumbers);
    }).and('the matching numbers are stored on the line for selection', () => {
      expect(cart.line?.availableNumbers).toEqual(searchNumbers);
    });
  });

  scenario('Numbers locked by another customer are excluded from results', ({ given, when, then }) => {
    let cart: Cart;
    let numbers: string[] | Error;
    const otherAvailableNumbers = ['4415550200', '4415550201'];

    given('another customer has already locked the standard available numbers in Mavenir', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(otherAvailableNumbers);
      cart = await customerWithCart();
    });
    when('the Customer loads available numbers', () => {
      numbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir returns only available numbers, excluding the locked ones', () => {});
    then('the locked numbers are not in the available numbers list', () => {
      expect(numbers).not.toContain(storedHeldAvailableNumber);
      expect(numbers).not.toContain(enteredChosenAvailableNumber);
    }).and('only the currently available numbers are returned', () => {
      expect(numbers).toEqual(otherAvailableNumbers);
    });
  });
});

// ---------------------------------------------------------------------------

story('Choose a Number', () => {
  let reserveResourceSpy: MockInstance<typeof mavenirMsisdnGateway.reserveResource>;
  let patchCartWithNumberSpy: MockInstance<typeof shoppingCartGateway.patchCartWithNumber>;

  beforeEach(() => {
    reserveResourceSpy = vi.spyOn(mavenirMsisdnGateway, 'reserveResource');
    patchCartWithNumberSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithNumber');
  });

  scenario('Pick number', ({ given, when, then }) => {
    let cart: Cart;

    given(
      `Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list and no MSISDN is in the cart`,
      async () => {
        mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
        cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
        cart.line!.availableNumbers = storedAvailableNumbers;
      },
    );
    when(
      `My Paradise reserves ${enteredChosenAvailableNumber} in Mavenir and patches the shopping cart`,
      () => {
        cart.line!.reserveNumber(enteredChosenAvailableNumber);
      },
    );
    then(`My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber}`, () => {
      expect(reserveResourceSpy).toHaveBeenCalledWith(enteredChosenAvailableNumber, undefined);
    }).and(
      `My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber}`,
      () => {
        expect(patchCartWithNumberSpy).toHaveBeenCalledWith('cus_1', enteredChosenAvailableNumber);
      },
    );
    when('Mavenir confirms the reservation and patches the cart', async () => {
      cart = await reloadCart(cart);
    });
    then(`My Paradise stores ${expectedChosenAvailableNumber} on the line`, () => {
      expect(cart.line?.msisdn).toBe(expectedChosenAvailableNumber);
    }).and('the Customer is forwarded to Select Sim', () => {
      expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
    });
  });

  scenario('Pick number — replace existing', ({ given, when, then }) => {
    let cart: Cart;

    given(
      `MSISDN ${storedHeldAvailableNumber} is in the cart and Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list`,
      async () => {
        mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
        cart = await customerWithCart('cus_1', { bundleId: stubBundle.id, msisdn: storedHeldAvailableNumber });
        cart.line!.availableNumbers = storedAvailableNumbers;
      },
    );
    when(
      `My Paradise reserves ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}`,
      () => {
        cart.line!.reserveNumber(enteredChosenAvailableNumber);
      },
    );
    then(
      `My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}`,
      () => {
        expect(reserveResourceSpy).toHaveBeenCalledWith(enteredChosenAvailableNumber, storedHeldAvailableNumber);
      },
    );
    when(
      `Mavenir releases ${storedHeldAvailableNumber} and reserves ${enteredChosenAvailableNumber}`,
      async () => {
        cart = await reloadCart(cart);
      },
    );
    then(`My Paradise stores ${expectedChosenAvailableNumber} on the line`, () => {
      expect(cart.line?.msisdn).toBe(expectedChosenAvailableNumber);
    });
  });

  scenario('Reserve number request fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: void | Error;

    given(`Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list but reserve returns an error`, async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      cart = await customerWithCart();
      cart.line!.availableNumbers = storedAvailableNumbers;
      mavenirMsisdnGateway.seedReserveError(new Error('Failed to reserve'));
    });
    when(
      `My Paradise attempts to reserve ${enteredChosenAvailableNumber} but Mavenir returns an error`,
      () => {
        result = cart.line!.reserveNumber(enteredChosenAvailableNumber);
      },
    );
    then('My Paradise shows Failed to reserve your number.', () => {
      expect(result).toBeInstanceOf(Error);
    });
  });

  scenario('Patch cart with number fails', ({ given, when, then }) => {
    let cart: Cart;
    let result: void | Error;

    given(`Mavenir has reserved ${enteredChosenAvailableNumber} but patching the cart returns an error`, async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
      cart = await customerWithCart();
      cart.line!.availableNumbers = storedAvailableNumbers;
      shoppingCartGateway.seedPatchCartWithNumberError(new Error('Failed to update cart'));
    });
    when(
      `My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber} but Mavenir returns an error`,
      () => {
        result = cart.line!.reserveNumber(enteredChosenAvailableNumber);
      },
    );
    then('My Paradise shows Failed to update your cart.', () => {
      expect(result).toBeInstanceOf(Error);
    });
  });
});
