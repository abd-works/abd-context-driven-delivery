from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when
from examples import storedHeldAvailableNumber, enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart, stubBundle, expectedChosenAvailableNumber, reloadCart


# Epic: Get New Number
# Orders: 0.0.1.1

# Story: Determine Number
with story("Determine Number"):
    # typescript body to translate:
    # let listResourcesSpy: MockInstance<typeof mavenirMsisdnGateway.listResources>;
    # let searchResourcesSpy: MockInstance<typeof mavenirMsisdnGateway.searchResources>;
    #
    # beforeEach(() => {
    #   listResourcesSpy = vi.spyOn(mavenirMsisdnGateway, 'listResources');
    #   searchResourcesSpy = vi.spyOn(mavenirMsisdnGateway, 'searchResources');
    # });
        with scenario("View available numbers"):
            # typescript body to translate:
            # let cart: Cart;
            # let numbers: string[] | Error;
            # examples: storedHeldAvailableNumber, enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
            with given("a My Paradise customer with a Mavenir shopping cart and no MSISDN"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart();
                pass
            with when("the Customer loads available numbers"):
                # typescript body to translate:
                # numbers = cart.line!.getNumbers();
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                # typescript body to translate:
                # expect(listResourcesSpy).toHaveBeenCalledOnce();
                pass
            with when("Mavenir locks 20 MSISDN resources and returns the available number values"):
                pass
            with then("My Paradise returns the available numbers"):
                # typescript body to translate:
                # expect(numbers).toEqual(storedAvailableNumbers);
                pass
            with and_("${storedHeldAvailableNumber} and ${enteredChosenAvailableNumber} are in the Available Number list"):
                # typescript body to translate:
                # expect(numbers as string[]).toContain(storedHeldAvailableNumber);
                # expect(numbers as string[]).toContain(enteredChosenAvailableNumber);
                pass
        with scenario("View available numbers — MSISDN in cart"):
            # typescript body to translate:
            # let cart: Cart;
            # let numbers: string[] | Error;
            # examples: storedHeldAvailableNumber, storedAvailableNumbers, customerWithCart, stubBundle
            with given("MSISDN ${storedHeldAvailableNumber} is in the Mavenir shopping cart"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart('cus_1', { bundleId: stubBundle.id, msisdn: storedHeldAvailableNumber });
                pass
            with when("the Customer loads available numbers"):
                # typescript body to translate:
                # numbers = cart.line!.getNumbers();
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                # typescript body to translate:
                # expect(listResourcesSpy).toHaveBeenCalledOnce();
                pass
            with when("Mavenir locks 20 MSISDN resources and returns the available number values"):
                pass
            with then("the Customer sees their number is ${storedHeldAvailableNumber}"):
                # typescript body to translate:
                # expect(cart.line?.msisdn).toBe(storedHeldAvailableNumber);
                pass
            with and_("My Paradise returns the available numbers"):
                # typescript body to translate:
                # expect(numbers).toEqual(storedAvailableNumbers);
                pass
        with scenario("Refresh available numbers"):
            # typescript body to translate:
            # let cart: Cart;
            # let refreshedNumbers: string[] | Error;
            # examples: storedAvailableNumbers, customerWithCart
            with given("a My Paradise customer with a Mavenir shopping cart"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart();
                pass
            with when("the Customer refreshes the number list"):
                # typescript body to translate:
                # refreshedNumbers = cart.line!.getNumbers();
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                # typescript body to translate:
                # expect(listResourcesSpy).toHaveBeenCalledOnce();
                pass
            with when("Mavenir locks 20 MSISDN resources and returns the available numbers"):
                pass
            with then("My Paradise returns a fresh set of available numbers"):
                # typescript body to translate:
                # expect(refreshedNumbers).toEqual(storedAvailableNumbers);
                pass
        with scenario("Search for a number"):
            # typescript body to translate:
            # let cart: Cart;
            # let searchResults: string[] | Error;
            # const searchNumbers = ['5263712345', '5263798765'];
            # examples: customerWithCart
            with given("a My Paradise customer with a Mavenir shopping cart"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(searchNumbers);
                # cart = await customerWithCart();
                pass
            with when("the Customer searches for numbers matching JAMES (52637)"):
                # typescript body to translate:
                # searchResults = cart.line!.searchNumbers('52637');
                pass
            with then("My Paradise sends the search request to Mavenir with pattern 52637"):
                # typescript body to translate:
                # expect(searchResourcesSpy).toHaveBeenCalledWith('52637');
                pass
            with when("Mavenir locks MSISDN resources matching 52637 and returns matching values"):
                pass
            with then("My Paradise returns Available Numbers matching 52637"):
                # typescript body to translate:
                # expect(searchResults).toEqual(searchNumbers);
                pass
            with and_("the matching numbers are stored on the line for selection"):
                # typescript body to translate:
                # expect(cart.line?.availableNumbers).toEqual(searchNumbers);
                pass
        with scenario("Numbers locked by another customer are excluded from results"):
            # typescript body to translate:
            # let cart: Cart;
            # let numbers: string[] | Error;
            # const otherAvailableNumbers = ['4415550200', '4415550201'];
            # examples: storedHeldAvailableNumber, enteredChosenAvailableNumber, customerWithCart
            with given("another customer has already locked the standard available numbers in Mavenir"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(otherAvailableNumbers);
                # cart = await customerWithCart();
                pass
            with when("the Customer loads available numbers"):
                # typescript body to translate:
                # numbers = cart.line!.getNumbers();
                pass
            with then("My Paradise sends the list resources request to Mavenir"):
                # typescript body to translate:
                # expect(listResourcesSpy).toHaveBeenCalledOnce();
                pass
            with when("Mavenir returns only available numbers, excluding the locked ones"):
                pass
            with then("the locked numbers are not in the available numbers list"):
                # typescript body to translate:
                # expect(numbers).not.toContain(storedHeldAvailableNumber);
                # expect(numbers).not.toContain(enteredChosenAvailableNumber);
                pass
            with and_("only the currently available numbers are returned"):
                # typescript body to translate:
                # expect(numbers).toEqual(otherAvailableNumbers);
                pass

# Story: Choose a Number
with story("Choose a Number"):
    # typescript body to translate:
    # let reserveResourceSpy: MockInstance<typeof mavenirMsisdnGateway.reserveResource>;
    # let patchCartWithNumberSpy: MockInstance<typeof shoppingCartGateway.patchCartWithNumber>;
    #
    # beforeEach(() => {
    #   reserveResourceSpy = vi.spyOn(mavenirMsisdnGateway, 'reserveResource');
    #   patchCartWithNumberSpy = vi.spyOn(shoppingCartGateway, 'patchCartWithNumber');
    # });
        with scenario("Pick number"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: enteredChosenAvailableNumber, expectedChosenAvailableNumber, storedAvailableNumbers, customerWithCart, reloadCart, stubBundle
            with given("Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list and no MSISDN is in the cart"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart('cus_1', { bundleId: stubBundle.id });
                # cart.line!.availableNumbers = storedAvailableNumbers;
                pass
            with when("My Paradise reserves ${enteredChosenAvailableNumber} in Mavenir and patches the shopping cart"):
                # typescript body to translate:
                # cart.line!.reserveNumber(enteredChosenAvailableNumber);
                pass
            with then("My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber}"):
                # typescript body to translate:
                # expect(reserveResourceSpy).toHaveBeenCalledWith(enteredChosenAvailableNumber, undefined);
                pass
            with and_("My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber}"):
                # typescript body to translate:
                # expect(patchCartWithNumberSpy).toHaveBeenCalledWith('cus_1', enteredChosenAvailableNumber);
                pass
            with when("Mavenir confirms the reservation and patches the cart"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores ${expectedChosenAvailableNumber} on the line"):
                # typescript body to translate:
                # expect(cart.line?.msisdn).toBe(expectedChosenAvailableNumber);
                pass
            with and_("the Customer is forwarded to Select Sim"):
                # typescript body to translate:
                # expect(cart.onboardingStep).toBe(OnboardingStep.SelectSim);
                pass
        with scenario("Pick number — replace existing"):
            # typescript body to translate:
            # let cart: Cart;
            # examples: storedHeldAvailableNumber, enteredChosenAvailableNumber, expectedChosenAvailableNumber, storedAvailableNumbers, customerWithCart, reloadCart, stubBundle
            with given("MSISDN ${storedHeldAvailableNumber} is in the cart and Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart('cus_1', { bundleId: stubBundle.id, msisdn: storedHeldAvailableNumber });
                # cart.line!.availableNumbers = storedAvailableNumbers;
                pass
            with when("My Paradise reserves ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}"):
                # typescript body to translate:
                # cart.line!.reserveNumber(enteredChosenAvailableNumber);
                pass
            with then("My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}"):
                # typescript body to translate:
                # expect(reserveResourceSpy).toHaveBeenCalledWith(enteredChosenAvailableNumber, storedHeldAvailableNumber);
                pass
            with when("Mavenir releases ${storedHeldAvailableNumber} and reserves ${enteredChosenAvailableNumber}"):
                # typescript body to translate:
                # cart = await reloadCart(cart);
                pass
            with then("My Paradise stores ${expectedChosenAvailableNumber} on the line"):
                # typescript body to translate:
                # expect(cart.line?.msisdn).toBe(expectedChosenAvailableNumber);
                pass
        with scenario("Reserve number request fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: void | Error;
            # examples: enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
            with given("Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list but reserve returns an error"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart();
                # cart.line!.availableNumbers = storedAvailableNumbers;
                # mavenirMsisdnGateway.seedReserveError(new Error('Failed to reserve'));
                pass
            with when("My Paradise attempts to reserve ${enteredChosenAvailableNumber} but Mavenir returns an error"):
                # typescript body to translate:
                # result = cart.line!.reserveNumber(enteredChosenAvailableNumber);
                pass
            with then("My Paradise shows Failed to reserve your number."):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                pass
        with scenario("Patch cart with number fails"):
            # typescript body to translate:
            # let cart: Cart;
            # let result: void | Error;
            # examples: enteredChosenAvailableNumber, storedAvailableNumbers, customerWithCart
            with given("Mavenir has reserved ${enteredChosenAvailableNumber} but patching the cart returns an error"):
                # typescript body to translate:
                # mavenirMsisdnGateway.seedAvailableNumbers(storedAvailableNumbers);
                # cart = await customerWithCart();
                # cart.line!.availableNumbers = storedAvailableNumbers;
                # shoppingCartGateway.seedPatchCartWithNumberError(new Error('Failed to update cart'));
                pass
            with when("My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber} but Mavenir returns an error"):
                # typescript body to translate:
                # result = cart.line!.reserveNumber(enteredChosenAvailableNumber);
                pass
            with then("My Paradise shows Failed to update your cart."):
                # typescript body to translate:
                # expect(result).toBeInstanceOf(Error);
                pass
