import type { Cart } from '../../../../domain/cart/Cart';
import type { Voucher } from '../../../../domain/cart/Voucher';
import { VoucherRedemption } from '../../../../domain/cart/Voucher';
import {
  amountOffVoucher,
  amountOffVoucherCode,
  amountOffVoucheraSeed,
  percentOffVoucher,
  percentOffVoucherCode,
  percentOffVoucheraSeed,
} from './voucher.examples';

export const amountRedemption = new VoucherRedemption(true, 25, 45);
export const percentRedemption = new VoucherRedemption(true, 7, 63);
export const zeroRedemption = new VoucherRedemption(true, 0, 0);

export const redeemMatchOutlines: Array<{
  example: string;
  makeVoucher: (cart: Cart) => Voucher;
  seed: typeof amountOffVoucheraSeed;
  voucherCode: string;
  orderAmount: string;
  discountAmount: number;
  totalAmount: number;
  creditExample: string;
  creditAmount: number;
  remarks: string;
}> = [
  {
    example: 'amount-off voucher',
    makeVoucher: amountOffVoucher,
    seed: amountOffVoucheraSeed,
    voucherCode: amountOffVoucherCode,
    orderAmount: '70.00',
    discountAmount: 25,
    totalAmount: 45,
    creditExample: 'summer credit adjustment',
    creditAmount: 25,
    remarks: `$${amountOffVoucherCode}`,
  },
  {
    example: 'percent-off voucher',
    makeVoucher: percentOffVoucher,
    seed: percentOffVoucheraSeed,
    voucherCode: percentOffVoucherCode,
    orderAmount: '70.00',
    discountAmount: 7,
    totalAmount: 63,
    creditExample: 'percent credit adjustment',
    creditAmount: 7,
    remarks: `$${percentOffVoucherCode}`,
  },
];
