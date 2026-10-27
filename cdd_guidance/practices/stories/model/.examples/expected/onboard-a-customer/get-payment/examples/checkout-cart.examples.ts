import { type Cart } from '../../../../domain/cart/Cart';
import { SimType } from '../../../../domain/subscription/Subscription';
import { customerWithCart } from '../../get-number/examples/cart.examples';
import { enteredChosenAvailableNumber } from '../../get-number/examples/available-number.examples';
import { essentials } from '../../examples/purchasable-plans.examples';

/** Checkout cart ready for FAC $1 ON-BOARDING authorization. Pay-up-front is Place Order, not Enter Payment. */
export async function customerReadyForPayment(): Promise<Cart> {
  return customerWithCart('cus_1', {
    bundleId: essentials.id,
    msisdn: enteredChosenAvailableNumber,
    simType: SimType.Esim,
    idNumber: 'ID12345',
  });
}
