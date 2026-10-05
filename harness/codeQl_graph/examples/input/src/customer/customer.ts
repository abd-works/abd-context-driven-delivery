import { AccountCredentials, AccountToken } from '../account-credentials/account-credentials';


export class Identity {
  constructor(
    public email: string,
    public name = '',
    public lastName = '',
    public fullName = '',
    public preferredName = '',
    public expiryDate = '',
    public dateOfBirth = '',
    public idNationality = '',
    public idNumber = '',
    public idType = '',
    public otherPhoneNumber = '',
  ) {}
}

export class Address {
  constructor(
    public street = '',
    public complement = '',
    public city = '',
    public parish = '',
    public postalCode = '',
    public country = '',
  ) {}
}

export type CustomerBilling = {
  id: string;
  state: string;
};

export class Customer {
  static readonly messages = {
    createFailed: 'Could not create customer.',
    loadFailed: 'Something went wrong when loading your account',
    terminated: 'Your account has been terminated.',
  };

  public id: string;
  //invariant
  public identity: Identity;
  //invariant
  public address: Address;
  public verified = false;
  public done = false;
  _repository?: CustomerRepository;

  /** Canonical: `new Customer(accountCredentials)`. id, identity, and address are derived unless the repository passes them. */
  constructor(
    //foreign AccountCredentials
    public accountCredentials: AccountCredentials,
    id?: string,
    identity?: Identity,
    address?: Address,
    //foreign Billing
    public billing: CustomerBilling | null = null,
  ) {
    this.id = id ?? accountCredentials.customerId ?? '';
    this.identity = identity ?? new Identity(accountCredentials.email ?? '');
    this.address = address ?? new Address();
  }

  terminated(): boolean {
    return this.billing?.state === 'terminated';
  }
}

export const CustomerOperation = {
  ConfirmIdentity: 'confirmIdentity',
  Create: 'create',
  Load: 'load',
  StoreCustomerId: 'storeCustomerId',
} as const;
export type CustomerOperation = (typeof CustomerOperation)[keyof typeof CustomerOperation];

export class CustomerException extends Error {
  constructor(
    public readonly operation: CustomerOperation,
    public readonly accountCredentials: AccountCredentials,
    message: string,
    public readonly cause: Error,
  ) {
    super(message);
    this.name = 'CustomerException';
  }
}


type StoredCustomer = {
  id: string;
  accountEmail: string;
  identity: Identity;
  address: Address;
  verified: boolean;
  done: boolean;
  billingId: string | null;
  billingState: string | null;
};

export class CustomerRepository {
  private readonly customers = new Map<string, StoredCustomer>();
  private nextCustomerId = 0;

  /** @testControl */
  reset(): void {
    this.customers.clear();
    this.nextCustomerId = 0;
  }

  new(customer: Customer): Customer {
    return this.attach(customer);
  }

  /** @testControl Empty customer the test fills, then stores with `_seedCustomer`. */
  _emptyCustomer(accountCredentials: AccountCredentials): Customer {
    return this.attach(new Customer(accountCredentials));
  }

  /** @testControl Persist a customer the test already filled. */
  _seedCustomer(customer: Customer): void {
    this.save(customer);
  }

  /** @testControl */
  seed(customer: Customer): Customer {
    this.save(this.attach(customer));
    return customer;
  }

  save(customer: Customer): void {
    this.customers.set(customer.id, {
      id: customer.id,
      accountEmail: customer.accountCredentials.email,
      identity: this.copyIdentity(customer.identity),
      address: this.copyAddress(customer.address),
      verified: customer.verified,
      done: customer.done,
      billingId: customer.billing?.id ?? null,
      billingState: customer.billing?.state ?? null,
    });
  }

  async create(accountCredentials: AccountCredentials): Promise<Customer> {
    const created = await this.persistCustomer(accountCredentials);
    if (!created) {
      throw this.exception(CustomerOperation.Create, accountCredentials, Customer.messages.createFailed, 'Customer already exists');
    }
    return created;
  }

  async load(accountCredentials: AccountCredentials): Promise<Customer> {
    const customerId = accountCredentials.customerId ?? accountCredentials.token?.customerId;
    if (!accountCredentials.token || !customerId)
      throw this.exception(CustomerOperation.Load, accountCredentials, Customer.messages.loadFailed, 'Invalid token');
    const email = this.validateToken(accountCredentials.token);
    if (email instanceof Error || !accountCredentials.token.customerId)
      throw this.exception(CustomerOperation.Load, accountCredentials, Customer.messages.loadFailed, 'Invalid token');
    const customer = await this.read(accountCredentials.token.customerId, accountCredentials);
    if (customer.terminated()) {
      await accountCredentials.signOut();
      throw this.exception(
        CustomerOperation.Load,
        accountCredentials,
        Customer.messages.terminated,
        'Billing account is terminated',
      );
    }
    return customer;
  }

  private async persistCustomer(accountCredentials: AccountCredentials): Promise<Customer | null> {
    if (!accountCredentials.verified)
      throw this.exception(CustomerOperation.Create, accountCredentials, Customer.messages.createFailed, 'Account is not verified');
    if (accountCredentials.customer) return null;
    return this.persistNewCustomer(accountCredentials.email, accountCredentials);
  }

  private async persistNewCustomer(email: string, accountCredentials: AccountCredentials): Promise<Customer> {
    for (const existing of this.customers.values()) {
      if (existing.identity.email === email) {
        throw new CustomerException(
          CustomerOperation.Create,
          accountCredentials,
          Customer.messages.createFailed,
          new Error('Customer already exists'),
        );
      }
    }
    this.nextCustomerId += 1;
    const customer = this.attach(
      new Customer(accountCredentials, `cus_${this.nextCustomerId}`),
    );
    this.save(customer);
    return customer;
  }

  private async read(customerId: string, accountCredentials: AccountCredentials): Promise<Customer> {
    const stored = this.customers.get(customerId);
    if (!stored) {
      await accountCredentials.signOut();
      throw new CustomerException(
        CustomerOperation.Load,
        accountCredentials,
        Customer.messages.loadFailed,
        new Error('Customer not found'),
      );
    }
    const customer = this.attach(new Customer(
      accountCredentials,
      stored.id,
      this.copyIdentity(stored.identity),
      this.copyAddress(stored.address),
    ));
    customer.verified = stored.verified;
    customer.done = stored.done;
    if (stored.billingId) {
      customer.billing = { id: stored.billingId, state: stored.billingState ?? 'active' };
    }
    accountCredentials.customer = customer;
    return customer;
  }

  private attach(customer: Customer): Customer {
    customer._repository = this;
    return customer;
  }

  private validateToken(token: AccountToken): string | Error {
    return token.jwt?.startsWith('token:') ? token.email : new Error('Invalid token');
  }

  private exception(
    operation: CustomerOperation,
    accountCredentials: AccountCredentials,
    message: string,
    cause: string,
  ): CustomerException {
    return new CustomerException(operation, accountCredentials, message, new Error(cause));
  }

  private copyIdentity(identity: Identity): Identity {
    return new Identity(
      identity.email,
      identity.name,
      identity.lastName,
      identity.fullName,
      identity.preferredName,
      identity.expiryDate,
      identity.dateOfBirth,
      identity.idNationality,
      identity.idNumber,
      identity.idType,
      identity.otherPhoneNumber,
    );
  }

  private copyAddress(address: Address): Address {
    return new Address(
      address.street,
      address.complement,
      address.city,
      address.parish,
      address.postalCode,
      address.country,
    );
  }
}

