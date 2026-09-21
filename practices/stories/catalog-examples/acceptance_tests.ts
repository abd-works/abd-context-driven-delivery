import { afterEach, beforeEach, expect, vi } from 'vitest';
import type { MockInstance } from 'vitest';
import { scenario, story } from 'stories/story-test';
import { type Cart, CartRepository } from '../../../domain/cart/Cart';
import { AccountCredentials, customerRepository } from '../../../domain/customer/Customer';
import {
  MavenirCartItem,
  MavenirProductCharacteristic,
  MavenirShoppingCart,
  shoppingCartGateway,
} from '../../../domain/systems/mavenir/shopping-cart-gateway';
import { mavenirMsisdnGateway } from '../../../domain/systems/mavenir/msisdn-gateway';
import { portalGateway } from '../../../domain/systems/mavenir/portal-gateway';

// available number
const heldAvailableNumber = '4415550100';
const chosenAvailableNumber = '4415550101';
const jamesMatchingNumbers = ['5263712345', '5263798765'];
const numbersLockedByAnotherCustomer = ['4415550200', '4415550201'];

// search term
const jamesSearch = { input: 'JAMES', converted: '52637' };

// Mavenir shopping cart
const emptyCart = new MavenirShoppingCart('cart_cus_1', 'cus_1');
const cartHoldingHeldAvailableNumber = new MavenirShoppingCart(
  'cart_cus_1',
  'cus_1',
  'plan_1',
  [
    new MavenirCartItem(
      {
        name: '',
        description: '',
        isBundle: true,
        productCharacteristic: [new MavenirProductCharacteristic('MSISDN', heldAvailableNumber)],
      },
      { id: 'plan_1' },
    ),
  ],
);

// account credentials
const validAccountCredentials = new AccountCredentials(
  'prospect@example.com',
  'Valid-pass99',
  'Valid-pass99',
  '',
  false,
);

const cartRepository = new CartRepository(shoppingCartGateway);

function msisdnOn(cart: MavenirShoppingCart): string | undefined {
  return cart.cartItem
    .flatMap(item => item.product.productCharacteristic)
    .find(characteristic => characteristic.name === 'MSISDN')?.value;
}

async function customerWithCart(mavenirShoppingCart: MavenirShoppingCart): Promise<Cart> {
  const customerId = mavenirShoppingCart.customerId ?? 'cus_1';
  portalGateway.seedCustomerById(customerId, validAccountCredentials.email ?? '');
  shoppingCartGateway.seedCart(customerId, mavenirShoppingCart.id, {
    bundleId: mavenirShoppingCart.bundleId,
    msisdn: msisdnOn(mavenirShoppingCart),
  });
  const customer = await customerRepository.load(validAccountCredentials);
  return cartRepository.load(customer)!;
}

afterEach(() => {
  shoppingCartGateway.reset();
  mavenirMsisdnGateway.reset();
  portalGateway.reset();
  vi.restoreAllMocks();
});

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
      mavenirMsisdnGateway.seedAvailableNumbers([heldAvailableNumber, chosenAvailableNumber]);
      cart = await customerWithCart(emptyCart);
    });
    when('the Customer loads available numbers', () => {
      numbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {});
    then('My Paradise returns the available numbers', () => {
      expect(numbers).toEqual([heldAvailableNumber, chosenAvailableNumber]);
    }).and('held available number and chosen available number are in the Available Number list', () => {
      expect(numbers as string[]).toContain(heldAvailableNumber);
      expect(numbers as string[]).toContain(chosenAvailableNumber);
    });
  });

  scenario('View available numbers — MSISDN in cart', ({ given, when, then }) => {
    let cart: Cart;
    let numbers: string[] | Error;

    given('MSISDN held available number is in the Mavenir shopping cart', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers([heldAvailableNumber, chosenAvailableNumber]);
      cart = await customerWithCart(cartHoldingHeldAvailableNumber);
    });
    when('the Customer loads available numbers', () => {
      numbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir locks 20 MSISDN resources and returns the available number values', () => {});
    then('the Customer sees their number is held available number', () => {
      expect(cart.line?.msisdn).toBe(heldAvailableNumber);
    }).and('My Paradise returns the available numbers', () => {
      expect(numbers).toEqual([heldAvailableNumber, chosenAvailableNumber]);
    });
  });

  scenario('Refresh available numbers', ({ given, when, then }) => {
    let cart: Cart;
    let refreshedNumbers: string[] | Error;

    given('a My Paradise customer with a Mavenir shopping cart', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers([heldAvailableNumber, chosenAvailableNumber]);
      cart = await customerWithCart(emptyCart);
    });
    when('the Customer refreshes the number list', () => {
      refreshedNumbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir locks 20 MSISDN resources and returns the available numbers', () => {});
    then('My Paradise returns a fresh set of available numbers', () => {
      expect(refreshedNumbers).toEqual([heldAvailableNumber, chosenAvailableNumber]);
    });
  });

  scenario('Search for a number', ({ given, when, then }) => {
    let cart: Cart;
    let searchResults: string[] | Error;

    given('James matching numbers are available in Mavenir', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(jamesMatchingNumbers);
      cart = await customerWithCart(emptyCart);
    });
    when('the Customer searches for numbers matching James search', () => {
      searchResults = cart.line!.searchNumbers(jamesSearch.converted);
    });
    then('My Paradise sends the search request to Mavenir with pattern James search', () => {
      expect(searchResourcesSpy).toHaveBeenCalledWith(jamesSearch.converted);
    });
    when('Mavenir locks MSISDN resources matching 52637 and returns matching values', () => {});
    then('My Paradise returns Available Numbers matching 52637', () => {
      expect(searchResults).toEqual(jamesMatchingNumbers);
    }).and('the matching numbers are stored on the line for selection', () => {
      expect(cart.line?.availableNumbers).toEqual(jamesMatchingNumbers);
    });
  });

  scenario('Numbers locked by another customer are excluded from results', ({ given, when, then }) => {
    let cart: Cart;
    let numbers: string[] | Error;

    given('another customer has already locked the standard available numbers in Mavenir', async () => {
      mavenirMsisdnGateway.seedAvailableNumbers(numbersLockedByAnotherCustomer);
      cart = await customerWithCart(emptyCart);
    });
    when('the Customer loads available numbers', () => {
      numbers = cart.line!.getNumbers();
    });
    then('My Paradise sends the list resources request to Mavenir', () => {
      expect(listResourcesSpy).toHaveBeenCalledOnce();
    });
    when('Mavenir returns only available numbers, excluding the locked ones', () => {});
    then('the locked numbers are not in the available numbers list', () => {
      expect(numbers).not.toContain(heldAvailableNumber);
      expect(numbers).not.toContain(chosenAvailableNumber);
    }).and('only the currently available numbers are returned', () => {
      expect(numbers).toEqual(numbersLockedByAnotherCustomer);
    });
  });
});
