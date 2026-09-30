class Cart {
  // << association >>
  customer: Customer;
  id: string;
  // << composition >>
  line: Line;
  // << composition >>
  // snapshot of selected Plan
  // set by Cart.pickPlan
  // catalog Plan changes do not rewrite this snapshot
  bundle: Bundle | null;
  // << association >>
  // link to Porting
  // set by Cart.bringNumber
  // details and SMS live on Portability
  portability: Portability | null;
  // << association >>
  // selected code until cook
  // null until applyVoucher
  // always null after removeVoucher
  // cook reads this code for Vouchera.redeem
  voucher: Voucher | null;
  // << association >>
  // flags Cart consults (sim, pay-up-front, attempts, roaming ticket)
  growthBook: GrowthBook;
  // always true after storeOrderResult
  defaultPayment: boolean;
  // success from Store Order Result
  orderSuccess: boolean | null;
  // stored when present
  // null on fail
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
    // existing Cognito customer id: CustomerRepository.load through Midtier
    // missing Cognito customer id: CustomerRepository.create through Midtier, then AccountCredentials.storeCustomerId
    CustomerRepository.create();
  }
  pickPlan(plan: Plan): Cart | CartErrors    //applyPlan {
    // copies Plan onto Cart.bundle
    // Cart.bundle.plan is that Plan
    // first Select writes bundle onto empty cart
    // later Select replaces bundle
    // Get Data Freedom Upgrade is later Select
    // Get Review Plan is later Select
    // when the same Plan is already on cart: no patch
    // when portability is present: portability.planSelected is the Plan name
    // when patch fails: CartErrors.patch
    PortalGateway.patchBundle();
  }
  pickNumber(availableNumber: AvailableNumber): Cart | CartErrors {
    // previousId is always the current msisdn
    // portin is always false
    // premium selected id uses the same patchMsisdn hop
    // portability stays null
    // when reserve fails: CartErrors.reserve
    // when patch fails: CartErrors.patch
    MsisdnInventoryRepository.reserve();
    PortalGateway.patchMsisdn();
  }
  bringNumber(portability: Portability): Cart | CartErrors {
    // always list size 1
    // previousId is always the current msisdn
    // portin is always true
    // msisdn is always the reserved temporary number
    // when reserve fails: CartErrors.reserve
    // when patch fails: CartErrors.patch
    // when portability fails: CartErrors.portability
    // when porting-2fa is off: no SMS
    // when porting-2fa is on: Twilio after patch
    // Portability.verified is false
    // Line.portability is the link to that Portability
    MsisdnInventoryRepository.list();
    MsisdnInventoryRepository.reserve();
    PortalGateway.patchPortability();
  }
  applyVoucher(code: string): Cart | VoucherErrors {
    // POST /customer/voucher
    // sets Cart.voucher
    // skip when voucher is present
    // auto-apply after Customer.confirmIdentity
    // session storage clear after auto-apply is intended
    // trial voucher requires a trial plan on cart
    // trial without trial plan: VoucherErrors.trial (500)
    // unknown code: VoucherErrors.invalid
    // expired: VoucherErrors.expired
    // redeemed: VoucherErrors.redeemed
    // intended: expired and redeemed are typed; live 400 has no body
    // other request failure: VoucherErrors.request
    // auto-apply rejection: VoucherErrors.notWorking
    Vouchera.read();
    PortalGateway.patchVoucher();
  }
  removeVoucher(): Cart | VoucherErrors {
    // DELETE /customer/voucher
    // voucher always null after success
    PortalGateway.removeVoucher();
  }
  checkout(payment: Payment): Cart | PaymentErrors {
    // payment is on the cart (Authorize Card)
    // Payment is not on the order
    // always GET /customer/payment/status/:transactionId
    // when completed: PortalGateway.createBilling on the Customer then Cart.createOrder
    // when failed and attempts under PAYMENT_ATTEMPTS: PaymentErrors.unverified; Payment.enter again
    // when failed and attempts equal PAYMENT_ATTEMPTS: Payment.recordFailed then Cart.createOrder
    FAC.read();
    createOrder();
  }
  createOrder(customer: Customer): Cart {
    // writes MavenirProductOrder (lives on Subscription after cook)
    // always POST /customer/order
    // no body
    // Redeem Voucher when cook: Vouchera.redeem writes VoucherRedemption on Subscription
    // Apply Credit when cook: Billing / PortalGateway.applyCredit
    // Create Order Ticket: CaseRepository.open in # Care
    // Then hop Store Order Result
    PortalGateway.createProductOrder();
    CaseRepository.open();
    storeOrderResult();
  }
  storeOrderResult(customer: Customer, success: boolean, payUpFront: boolean | null, verified: boolean): Cart {
    // always defaultPayment true
    // orderSuccess = success
    // payUpFront stored when present; null on fail
    // success: overwrite Customer.verified from order-body verified
    // order-body verified is Midtier verifiedResponse = KYC | Portability.portNumber | Plan.bypassVerified
    // fail: does not write verified
    // Then View Order Result when allSet else View Almost There
    // banners: orderUnprocessed / paymentUnverified / SimBanner iccidRequired
  }
}

/**
 * Cart-module constants. Not open strings.
 * OnboardingStep.SelectPlan
 * OnboardingStep.PickNumber
 * OnboardingStep.VerifyPortedNumber
 * OnboardingStep.SelectSim
 * OnboardingStep.ProfileKyc
 * OnboardingStep.Checkout
 * OnboardingStep.Done
 */
class OnboardingStep {
}

/**
 * Snapshot of a `# Plans` *Plan* at pick time. Part of the Cart aggregate. PortalGateway cart read maps the Mavenir bundle cartItem onto `Cart.bundle` (`id`, `name`, `description`, `price`, `fees`, `totalPrice`, `features`). `id` is *Plan.id*. Catalog *Plan* changes do not rewrite a cart that already has a bundle.
 */
class Bundle {
  // Plan.id
  id: string;
  name: string;
  description: string;
  price: number;
  fees: number;
  totalPrice: number;
  // copied at pick time
  features: any;
  // << association >>
  // from Plans
  // where this snapshot came from
  // not composed; catalog Plan stays in Plans
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

/**
 * Flags Cart consults. Get Sim: `DISABLE_ESIM` / `DISABLE_PSIM`. `Cart.checkout` / `Payment.enter` read `PAY_UP_FRONT` and `PAYMENT_ATTEMPTS` from this type (Payment does not own GrowthBook). `Cart.createOrder` reads `PAY_UP_FRONT` and `ROAMING_PLAN_TICKET`. No Paradise types. No repository.
 */
class GrowthBook {
  // disable-esim
  DISABLEEsim: string;
  // disable-psim
  DISABLEPsim: string;
  // pay-up-front
  // when off: invoicePayment
  // when on: upfrontPayment
  PAYUpFront: string;
  // payment-attempts
  // always 3 on the scenario
  // live default is always 1
  PAYMENTAttempts: string;
  // roaming-plan-ticket
  ROAMINGPlanTicket: string;

  constructor(DISABLEEsim: string, DISABLEPsim: string, PAYUpFront: string, PAYMENTAttempts: string, ROAMINGPlanTicket: string) {
    this.DISABLEEsim = DISABLEEsim;
    this.DISABLEPsim = DISABLEPsim;
    this.PAYUpFront = PAYUpFront;
    this.PAYMENTAttempts = PAYMENTAttempts;
    this.ROAMINGPlanTicket = ROAMINGPlanTicket;
  }

  evaluate(key: string): boolean {
    // DISABLE_ESIM or DISABLE_PSIM or PAY_UP_FRONT or ROAMING_PLAN_TICKET
    // esimFlagOn / esimFlagOff / psimFlagOn / psimFlagOff
    // when DISABLE_ESIM is true: wizard starts at physical SIM
    // when DISABLE_PSIM is true: hide pSIM card and dialog Nope
    // Flagged: live also hides Yay
    // when PAY_UP_FRONT is off: invoicePayment Time to add your payment
    // when PAY_UP_FRONT is on: upfrontPayment Complete your payment
  }
  value(key: string): number {
    // always PAYMENT_ATTEMPTS
    // always 3 on the scenario
    // live default is always 1
  }
}

/**
 * Owns `Collection<Cart>`. Associates to `PortalGateway` to read and create ++MavenirShoppingCart++. Cart itself has no shopping-cart edge. The Customer already holds AccountCredentials.
 */
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
    // always sets Customer.cart when a Cart exists
    // customer.id is always the MavenirCustomer id
    // when none: null
    // when Mavenir is unreachable: throws CartException with operation load, Customer and cause
    PortalGateway.read();
  }
  create(customer: Customer): Cart {
    // always sets Customer.cart
    // customer.id is always the MavenirCustomer id
    // when find is null
    // never when a cart already exists for that Customer
    // when a Cart already exists or Mavenir is unreachable: throws CartException with operation create, Customer and cause
    PortalGateway.create();
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

/**
 * Wrap target. Vouchera ++Voucher++. No Paradise types. Cart wraps the selected code until cook.
 */
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

/**
 * Vouchera builds the ++Voucher++. Vouchera GET /vouchers/{code}. `read` is catalog `Voucher.apply` through `VoucherRepository.get`. `redeem` is Subscription cook and returns `# Subscription` *VoucherRedemption*.
 */
class Vouchera {

  constructor() {
  }

  read(code: string): Voucher | Error {
    // unknown code: none
  }
  redeem(code: string, redeemerIdentifier: string, orderAmount: number): VoucherRedemption {
    // Redeem Voucher
    // always POST vouchers/{code}/redeem
    // cook only
    // planIds match: orderAmount totalPrice then hop Apply Credit
    // no planIds: orderAmount 0.00 then cook
    // planIds miss: skip redeem then cook
    // flagged 5xx: success false; cook continues
    // writes Subscription.voucherRedemption
  }
}

/**
 * Wrap target. Empty at create (no cart items). Mavenir shoppingCart create: MavenirCustomer id, lineCount 1, empty cartItem, serviceProviderId, ON-BOARDING channel. *Get Plan On Cart* writes the bundle cartItem. *Get Data Freedom Upgrade* replaces that bundle. *Get Review Plan* replaces that bundle. Patch writes the MSISDN *ProductCharacteristic* and, on bring, ++portability++ characteristics. *Get Esim* writes the `SIM_TYPE` *ProductCharacteristic* (`'eSIM'`). *Get Paradise Sim Card* writes `SIM_TYPE` (`'pSIM'`); no ICCID characteristic. *Get Existing Iccid* writes `SIM_TYPE` (`'pSIM'`) and `ICCID` on the existing bundle cartItem. *Activate Sim From Almost There* PATCH shoppingCart billing then POST productOrderFromCart; SIM_TYPE `'pSIM'` and ICCID already on bundle. The wrap does not know Cart.
 */
class MavenirShoppingCart {
  id: string;
  customerId: string;
  lineCount: number;
  serviceProviderId: string;
  // Get Plan On Cart writes the bundle
  // Get Data Freedom Upgrade replaces the bundle
  // Get Review Plan replaces the bundle
  // always a bundle when patching MSISDN, ++portability++, SIM_TYPE, or ICCID
  // bundle cartItem already present for pickSim and pickIccid
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

/**
 * Mavenir `portalGateway` shopping cart.
 */
class PortalGateway {

  constructor() {
  }

  read(mavenirCustomerId: string): MavenirShoppingCart | Error {
    // when none for that MavenirCustomer: none
  }
  create(mavenirCustomerId: string): MavenirShoppingCart | Error {
    // always lineCount 1, empty cartItem, ON-BOARDING channel
    // never when a cart already exists for that MavenirCustomer
  }
  patchBundle(mavenirCustomerId: string, bundleId: string): MavenirShoppingCart | Error {
    // always fetches the catalog bundle
    // always builds the bundle cartItem
    // always PATCH shopping cart
    // first Select writes bundle onto empty cart
    // later Select replaces bundle
    // Get Data Freedom Upgrade is later Select
    // Get Review Plan is later Select
    // when portability is present: planName is the bundle name
    PortalGateway.list();
  }
  patchMsisdn(mavenirCustomerId: string, msisdn: string): MavenirShoppingCart | Error {
    // always writes MSISDN ProductCharacteristic on the bundle cartItem
    // premium ++MSISDN++ is the same MSISDN ProductCharacteristic (no premium variant)
  }
  patchPortability(mavenirCustomerId: string, msisdn: string, characteristics: ProductCharacteristic[]): MavenirShoppingCart | Error {
    // always writes MSISDN and ++portability++ ProductCharacteristic rows on the bundle cartItem
  }
  patchSimType(mavenirCustomerId: string, simType: string): MavenirShoppingCart | Error {
    // always writes SIM_TYPE ProductCharacteristic on the bundle cartItem
    // Get Esim: value always 'eSIM'
    // Get Paradise Sim Card: value always 'pSIM'
    // no ICCID characteristic
    // bundle cartItem already present
  }
  patchIccid(mavenirCustomerId: string, iccid: string): MavenirShoppingCart | Error {
    // always writes SIM_TYPE 'pSIM' and ICCID on the existing bundle cartItem
    // no sim-resource reserve
  }
  createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error {
    // PATCH shoppingCart billing (pre-cook) then POST productOrderFromCart
    // SIM_TYPE 'pSIM' and ICCID already on bundle
    // Create Product Order cook
  }
  patchSubmitOrder(mavenirCustomerId: string): MavenirShoppingCart | Error {
    // always writes submitOrder true on the bundle cartItem
    // when unverified no bypass no portability
  }
}

/**
 * MSISDN, ++portability++, SIM_TYPE, and ICCID characteristics on the bundle cartItem.
 */
class ProductCharacteristic {
  name: string;
  value: string;

  constructor(name: string, value: string) {
    this.name = name;
    this.value = value;
  }

}

/**
 * ON-BOARDING channel on shoppingCart create.
 */
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
