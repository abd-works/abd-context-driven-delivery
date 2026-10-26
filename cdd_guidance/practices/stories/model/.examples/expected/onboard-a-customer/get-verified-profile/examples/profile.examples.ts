import { Address, Identity } from '../../../../domain/customer/Customer';
import { profileRepository } from '../../../../domain/KYC/Profile';
import type { Cart } from '../../../../domain/cart/Cart';
import { shoppingCartGateway } from '../../../../domain/systems/mavenir/shopping-cart-gateway';
import { portalGateway, type SeedCustomerOpts } from '../../../../domain/systems/mavenir/portal-gateway';
import { enteredValidAccountCredentials, storedAccountCredentialsWithToken } from '../../examples/account-credentials.examples';
import { enteredChosenAvailableNumber } from '../../get-number/examples/available-number.examples';
import { loadCart, stubBundle } from '../../get-number/examples/cart.examples';

export const expectedValidIdentity = new Identity(
  enteredValidAccountCredentials.email,
  'JONATHAN',
  'WICK',
  'JONATHAN WICK',
  'Jonathan',
  '15/01/2030',
  '02/09/1964',
  'Bermuda',
  'I1234562',
  "Driver's License",
  '+44 1123 4567',
);
export const enteredValidIdentity = expectedValidIdentity;

export const expectedValidAddress = new Address(
  '82 Beaver St',
  '',
  'New York',
  'NY',
  'NY 10005',
  'US',
);
export const enteredValidAddress = expectedValidAddress;

export function validProfileSeed(opts?: { validated?: boolean; inquiryId?: string }): SeedCustomerOpts {
  return {
    idNumber: expectedValidIdentity.idNumber,
    givenName: expectedValidIdentity.name,
    familyName: expectedValidIdentity.lastName,
    preferredGivenName: expectedValidIdentity.preferredName,
    birthDate: expectedValidIdentity.dateOfBirth,
    idType: expectedValidIdentity.idType,
    issuingAuthority: expectedValidIdentity.idNationality,
    endDateTime: expectedValidIdentity.expiryDate,
    validated: opts?.validated ?? false,
    phoneNumber: expectedValidIdentity.otherPhoneNumber,
    street1: expectedValidAddress.street,
    street2: expectedValidAddress.complement,
    city: expectedValidAddress.city,
    stateOrProvince: expectedValidAddress.parish,
    postCode: expectedValidAddress.postalCode,
    country: expectedValidAddress.country,
    inquiryId: opts?.inquiryId,
  };
}

export async function customerWithProfile(seed?: SeedCustomerOpts): Promise<Cart> {
  const customerId = 'cus_1';
  const accountCredentials = storedAccountCredentialsWithToken(customerId);
  portalGateway.seedCustomerById(customerId, accountCredentials.email ?? '', seed);
  shoppingCartGateway.seedCart(customerId, `cart_${customerId}`, {
    bundleId: stubBundle.id,
    msisdn: enteredChosenAvailableNumber,
    simType: 'eSIM',
  });
  const cart = await loadCart(customerId);
  profileRepository.load(cart.customer);
  return cart;
}

export type IncompleteProfileOutline = {
  example: string;
  field: string;
  requirement: string;
  identity: Identity;
  address: Address;
};

function identityWith(overrides: Partial<Identity>): Identity {
  return new Identity(
    expectedValidIdentity.email,
    overrides.name ?? expectedValidIdentity.name,
    overrides.lastName ?? expectedValidIdentity.lastName,
    expectedValidIdentity.fullName,
    expectedValidIdentity.preferredName,
    overrides.expiryDate ?? expectedValidIdentity.expiryDate,
    overrides.dateOfBirth ?? expectedValidIdentity.dateOfBirth,
    overrides.idNationality ?? expectedValidIdentity.idNationality,
    overrides.idNumber ?? expectedValidIdentity.idNumber,
    overrides.idType ?? expectedValidIdentity.idType,
    expectedValidIdentity.otherPhoneNumber,
  );
}

function addressWith(overrides: Partial<Address>): Address {
  return new Address(
    overrides.street ?? expectedValidAddress.street,
    expectedValidAddress.complement,
    expectedValidAddress.city,
    overrides.parish ?? expectedValidAddress.parish,
    overrides.postalCode ?? expectedValidAddress.postalCode,
    expectedValidAddress.country,
  );
}

export const incompleteProfileOutlines: IncompleteProfileOutline[] = [
  { example: 'name required', field: 'name', requirement: 'Please provide a name.', identity: identityWith({ name: '' }), address: expectedValidAddress },
  { example: 'last name required', field: 'lastName', requirement: 'Please provide a last name.', identity: identityWith({ lastName: '' }), address: expectedValidAddress },
  { example: 'date of birth required', field: 'dateOfBirth', requirement: 'Date of Birth is required', identity: identityWith({ dateOfBirth: '' }), address: expectedValidAddress },
  { example: 'ID nationality required', field: 'idNationality', requirement: 'Please provide the nationality of your ID.', identity: identityWith({ idNationality: '' }), address: expectedValidAddress },
  { example: 'ID type required', field: 'idType', requirement: 'Please provide the type of your ID.', identity: identityWith({ idType: '' }), address: expectedValidAddress },
  { example: 'ID number required', field: 'idNumber', requirement: 'Please provide an ID Number.', identity: identityWith({ idNumber: '' }), address: expectedValidAddress },
  { example: 'expiry required', field: 'expiryDate', requirement: 'Please provide the document expiry date.', identity: identityWith({ expiryDate: '' }), address: expectedValidAddress },
  { example: 'street required', field: 'street', requirement: 'An address is required.', identity: expectedValidIdentity, address: addressWith({ street: '' }) },
  { example: 'parish required', field: 'parish', requirement: 'Parish is required.', identity: expectedValidIdentity, address: addressWith({ parish: '' }) },
  { example: 'postal code required', field: 'postalCode', requirement: 'Postal Code is required.', identity: expectedValidIdentity, address: addressWith({ postalCode: '' }) },
];
