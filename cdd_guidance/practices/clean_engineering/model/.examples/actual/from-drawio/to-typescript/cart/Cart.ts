class Cart {
  // << association >>
  customer: Customer;
  id: string;
  // << composition >>
  line: Line;
  // << composition >>
  bundle: Bundle | null;
  // << association >>
  portability: Portability | null;
  // << association >>
  voucher: Voucher | null;
  // << association >>
  growthBook: GrowthBook;
  defaultPayment: boolean;
  orderSuccess: boolean | null;
  payUpFront: boolean | null;

  constructor(customer: Customer, id: string, line: Line, bundle: Bundle | null, portability: Portability | null, voucher: Voucher | null, growthBook: GrowthBook, defaultPayment: boolean, orderSuccess: boolean | null, payUpFront: boolean | null) {
    this.customer = customer;
    this.id = id;
    this.line = line;
    this.bundle = bundle;
    this.portability = portability;
    this.voucher = voucher;
    this.growthBook = growthBook;
    this.defaultPayment = defaultPayment;
    this.orderSuccess = orderSuccess;
    this.payUpFront = payUpFront;
  }

  setupAccount(): Customer | null {
  }
  pickPlan(plan: Plan): Cart | CartErrors    //applyPlan {
  }
  pickNumber(availableNumber: AvailableNumber): Cart | CartErrors {
  }
  bringNumber(portability: Portability): Cart | CartErrors {
  }
  applyVoucher(code: string): Cart | VoucherErrors {
  }
  removeVoucher(): Cart | VoucherErrors {
  }
  checkout(payment: Payment): Cart | PaymentErrors {
  }
  createOrder(customer: Customer): Cart {
  }
  storeOrderResult(customer: Customer, success: boolean, payUpFront: boolean | null, verified: boolean): Cart {
  }
}

class OnboardingStep {
}

class Bundle {
  id: string;
  name: string;
  description: string;
  price: number;
  fees: number;
  totalPrice: number;
  features: any;
  // << association >>
  plan: Plan;

  constructor(id: string, name: string, description: string, price: number, fees: number, totalPrice: number, features: any, plan: Plan) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.price = price;
    this.fees = fees;
    this.totalPrice = totalPrice;
    this.features = features;
    this.plan = plan;
  }

}

class GrowthBook {
  DISABLEEsim: string;
  DISABLEPsim: string;
  PAYUpFront: string;
  PAYMENTAttempts: string;
  ROAMINGPlanTicket: string;

  constructor(DISABLEEsim: string, DISABLEPsim: string, PAYUpFront: string, PAYMENTAttempts: string, ROAMINGPlanTicket: string) {
    this.DISABLEEsim = DISABLEEsim;
    this.DISABLEPsim = DISABLEPsim;
    this.PAYUpFront = PAYUpFront;
    this.PAYMENTAttempts = PAYMENTAttempts;
    this.ROAMINGPlanTicket = ROAMINGPlanTicket;
  }

  evaluate(key: string): boolean {
  }
  value(key: string): number {
  }
}

class CartRepository {
  // << aggregation >>
  carts: Collection<Cart>;
  // << association >>
  portalGateway: PortalGateway;
  // << association >>
  customerRepository: CustomerRepository;

  constructor(carts: Collection<Cart>, portalGateway: PortalGateway, customerRepository: CustomerRepository) {
    this.carts = carts;
    this.portalGateway = portalGateway;
    this.customerRepository = customerRepository;
  }

  load(customer: Customer): Cart | null {
  }
  create(customer: Customer): Cart {
  }
}

class CartException {
  // << association >>
  operation: CartOperation;
  // << association >>
  customer: Customer;
  message: string;
  cause: Error;

  constructor(operation: CartOperation, customer: Customer, message: string, cause: Error) {
    this.operation = operation;
    this.customer = customer;
    this.message = message;
    this.cause = cause;
  }

}

class Voucher {
  code: string;
  campaign: string;
  expired: boolean;
  redeemed: boolean;

  constructor(code: string, campaign: string, expired: boolean, redeemed: boolean) {
    this.code = code;
    this.campaign = campaign;
    this.expired = expired;
    this.redeemed = redeemed;
  }

}

class Vouchera {

  constructor() {
  }

  read(code: string): Voucher | Error {
  }
  redeem(code: string, redeemerIdentifier: string, orderAmount: number): VoucherRedemption {
  }
}

class MavenirShoppingCart {
  id: string;
  customerId: string;
  lineCount: number;
  serviceProviderId: string;
  cartItem: bundle;
  // << composition >>
  productCharacteristic: ProductCharacteristic;
  // << composition >>
  channel: Channel;

  constructor(id: string, customerId: string, lineCount: number, serviceProviderId: string, cartItem: bundle, productCharacteristic: ProductCharacteristic, channel: Channel) {
    this.id = id;
    this.customerId = customerId;
    this.lineCount = lineCount;
    this.serviceProviderId = serviceProviderId;
    this.cartItem = cartItem;
    this.productCharacteristic = productCharacteristic;
    this.channel = channel;
  }

}

class PortalGateway {

  constructor() {
  }

  read(mavenirCustomerId: string): MavenirShoppingCart | Error {
  }
  create(mavenirCustomerId: string): MavenirShoppingCart | Error {
  }
  patchBundle(mavenirCustomerId: string, bundleId: string): MavenirShoppingCart | Error {
  }
  patchMsisdn(mavenirCustomerId: string, msisdn: string): MavenirShoppingCart | Error {
  }
  patchPortability(mavenirCustomerId: string, msisdn: string, characteristics: ProductCharacteristic[]): MavenirShoppingCart | Error {
  }
  patchSimType(mavenirCustomerId: string, simType: string): MavenirShoppingCart | Error {
  }
  patchIccid(mavenirCustomerId: string, iccid: string): MavenirShoppingCart | Error {
  }
  createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error {
  }
  patchSubmitOrder(mavenirCustomerId: string): MavenirShoppingCart | Error {
  }
}

class ProductCharacteristic {
  name: string;
  value: string;

  constructor(name: string, value: string) {
    this.name = name;
    this.value = value;
  }

}

class Channel {
  id: string;
  name: string;
  role: string;

  constructor(id: string, name: string, role: string) {
    this.id = id;
    this.name = name;
    this.role = role;
  }

}
