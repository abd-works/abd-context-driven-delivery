import type { Cart } from '../../../../domain/cart/Cart';
import { Voucher, voucherRepository } from '../../../../domain/cart/Voucher';
import { purchasablePlansExamples, essentials } from '../../examples/purchasable-plans.examples';
import { VoucheraDiscountType } from '../../../../domain/systems/vouchera';

export const amountOffVoucherCode = 'SUMMER25';
export const percentOffVoucherCode = 'FIRST10';
export const anyPlanVoucherCode = 'WELCOME';

export const ace = purchasablePlansExamples.find(p => p.name === 'Ace')!;

export function amountOffVoucher(cart: Cart): Voucher {
  return new Voucher(
    amountOffVoucherCode,
    amountOffVoucherCode,
    false,
    false,
    { planIds: [essentials.id] },
    { amount_off: 25 },
    voucherRepository,
    cart,
  );
}

export function percentOffVoucher(cart: Cart): Voucher {
  return new Voucher(
    percentOffVoucherCode,
    percentOffVoucherCode,
    false,
    false,
    { planIds: [essentials.id] },
    { percent_off: 10 },
    voucherRepository,
    cart,
  );
}

export function anyPlanVoucher(cart: Cart): Voucher {
  return new Voucher(
    anyPlanVoucherCode,
    anyPlanVoucherCode,
    false,
    false,
    {},
    {},
    voucherRepository,
    cart,
  );
}

export const amountOffVoucheraSeed = {
  code: amountOffVoucherCode,
  campaign: amountOffVoucherCode,
  discountType: VoucheraDiscountType.Amount,
  discountValue: 25,
};

export const percentOffVoucheraSeed = {
  code: percentOffVoucherCode,
  campaign: percentOffVoucherCode,
  discountType: VoucheraDiscountType.Percentage,
  discountValue: 10,
};

export const anyPlanVoucheraSeed = {
  code: anyPlanVoucherCode,
  campaign: anyPlanVoucherCode,
  discountType: VoucheraDiscountType.Amount,
  discountValue: 0,
};
