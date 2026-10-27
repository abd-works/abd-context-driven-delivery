import { Voucher, seedAppliedCatalogVoucher } from '../../../../domain/cart/Voucher';
import {
  VoucherCodeRule,
  VoucheraDiscountType,
  VoucheraPlanBundleId,
  VoucheraPlanName,
  VoucheraVoucher,
  VoucheraVoucherStatus,
  voucheraGateway,
} from '../../../../domain/systems/vouchera';

export const enteredValidCatalogVoucherCode = 'STUBPORT10';
export const expectedValidCatalogVoucherCode = enteredValidCatalogVoucherCode;
export const enteredInvalidCatalogVoucherCode = 'NOPE';
export const expiredCatalogVoucherCode = 'EXPIRED';
export const redeemedCatalogVoucherCode = 'USED';
export const shortCatalogVoucherCode = 'ABC';
export const unknownPlanDeepLinkId = 'unknown-plan-id';

const purchasableVoucheraPlans = [
  { name: VoucheraPlanName.Essentials },
  { name: VoucheraPlanName.DataFreedom },
  { name: VoucheraPlanName.Ace },
  { name: VoucheraPlanName.Atlas },
] as const;

export const purchasablePlanIds = [
  VoucheraPlanBundleId[VoucheraPlanName.Essentials],
  VoucheraPlanBundleId[VoucheraPlanName.DataFreedom],
  VoucheraPlanBundleId[VoucheraPlanName.Ace],
  VoucheraPlanBundleId[VoucheraPlanName.Atlas],
];

export function validCatalogVoucher(): VoucheraVoucher {
  return new VoucheraVoucher(
    '11111111-1111-1111-1111-111111111111',
    true,
    enteredValidCatalogVoucherCode,
    { id: '22222222-2222-2222-2222-222222222222', name: 'Port 10' },
    VoucheraVoucherStatus.Active,
    { type: VoucheraDiscountType.Percentage, value: 10 },
    { count: 0, limit: null },
    null,
    null,
    null,
    [...purchasableVoucheraPlans],
    null,
    '2026-01-01T00:00:00.000Z',
  );
}

export function expiredCatalogVoucher(): VoucheraVoucher {
  return new VoucheraVoucher(
    '33333333-3333-3333-3333-333333333333',
    true,
    expiredCatalogVoucherCode,
    { id: '44444444-4444-4444-4444-444444444444', name: 'Expired Port' },
    VoucheraVoucherStatus.Expired,
    { type: VoucheraDiscountType.Percentage, value: 10 },
    { count: 0, limit: null },
    null,
    '2020-01-01T00:00:00.000Z',
    null,
    [...purchasableVoucheraPlans],
    null,
    '2020-01-01T00:00:00.000Z',
  );
}

export function redeemedCatalogVoucher(): VoucheraVoucher {
  return new VoucheraVoucher(
    '55555555-5555-5555-5555-555555555555',
    true,
    redeemedCatalogVoucherCode,
    { id: '66666666-6666-6666-6666-666666666666', name: 'Used Port' },
    VoucheraVoucherStatus.Redeemed,
    { type: VoucheraDiscountType.Percentage, value: 10 },
    { count: 1, limit: 1 },
    null,
    null,
    null,
    [...purchasableVoucheraPlans],
    null,
    '2026-01-01T00:00:00.000Z',
  );
}

export function appliedValidCatalogVoucher(): Voucher {
  return new Voucher(
    enteredValidCatalogVoucherCode,
    'Port10',
    false,
    false,
    { planIds: purchasablePlanIds },
    { percent_off: 10, amount_off: 0 },
  );
}

export function seedValidCatalogVoucher(): void {
  voucheraGateway.seedVoucher(validCatalogVoucher());
}

export function seedExpiredCatalogVoucher(): void {
  voucheraGateway.seedVoucher(expiredCatalogVoucher());
}

export function seedRedeemedCatalogVoucher(): void {
  voucheraGateway.seedVoucher(redeemedCatalogVoucher());
}

export function seedAppliedValidCatalogVoucher(): void {
  seedAppliedCatalogVoucher(appliedValidCatalogVoucher());
}

export const unusableCatalogVoucherOutlines = [
  {
    example: 'invalid catalog voucher',
    code: enteredInvalidCatalogVoucherCode,
    seed: 'none' as const,
    voucheraReturns: 'Vouchera returns not found',
  },
  {
    example: 'expired catalog voucher',
    code: expiredCatalogVoucherCode,
    seed: 'expired' as const,
    voucheraReturns: 'Vouchera returns the voucher view',
  },
  {
    example: 'redeemed catalog voucher',
    code: redeemedCatalogVoucherCode,
    seed: 'redeemed' as const,
    voucheraReturns: 'Vouchera returns the voucher view',
  },
];

export function seedUnusableCatalogVoucher(seed: 'none' | 'expired' | 'redeemed'): void {
  if (seed === 'expired') seedExpiredCatalogVoucher();
  if (seed === 'redeemed') seedRedeemedCatalogVoucher();
}

export { VoucherCodeRule };
