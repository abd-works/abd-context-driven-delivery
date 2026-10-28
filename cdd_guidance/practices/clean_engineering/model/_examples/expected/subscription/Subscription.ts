/**
 * The phone line on a Cart or Subscription. Owns number, SIM type, ICCID, and portability.
 */
class Line {
  msisdn: string | null;
  // SimType.Esim | SimType.Psim
  // null until selectSim or attachIccid
  simType: SimType | null;
  // null until attachIccid
  iccid: string | null;
  availableNumbers: string[];
  // << association >>
  portability: Portability | null;

  constructor(msisdn: string | null, simType: SimType | null, iccid: string | null, availableNumbers: string[], portability: Portability | null) {
    this.msisdn = msisdn;
    this.simType = simType;
    this.iccid = iccid;
    this.availableNumbers = availableNumbers;
    this.portability = portability;
  }

  selectSim(simType: SimType): void | Error {
    // when the line already has that SIM type: no patch
    // Request a Paradise SIM card: SimType.Psim, no ICCID
    // when patch fails: Error
    ShoppingCartGateway.patchCartWithSim();
  }
  attachIccid(iccid: string): void | Error {
    // always SimType.Psim
    // when whitespace: Error; no inventory or patch
    // when read miss: Error
    MsisdnRepository.read();
    ShoppingCartGateway.patchCartWithSim();
  }
  activateSim(iccid: string): void | Error {
    // waiting pSIM must already be Active
    // absent waiting pSIM: Error
    // waiting pSIM Cleared: Error
    Line.attachIccid();
    PortalGateway.createPsimDeliveredOrder();
  }
}

/**
 * Paradise view of one line. Self-care: `{ id, bundle, number, simType, status, usage }`. Onboarding thinner: `{ type, number, status }` until agreement is live. `<<represents>>` ++MavenirAgreement++ (`agreementManagement/agreement`).
 */
class Subscription {
  // MavenirAgreement.id
  id: string;
  // active | suspended | terminated | pendingActive
  status: string;
  // number, simType, iccid, portability live on Line
  // << composition >>
  line: Line;
  // from Cart
  // same snapshot pickPlan wrote
  // agreementItem.product / productOffering
  // << composition >>
  bundle: Bundle;
  // << composition >>
  usage: Usage;
  // from Porting
  // from Cart.portability when they brought a number
  // << association >>
  portability: Portability | null;
  // Cart.createOrder / PortalGateway.createProductOrder
  // << association >>
  productOrder: MavenirProductOrder | null;
  // cook: Vouchera.redeem on Cart.voucher
  // << association >>
  voucherRedemption: VoucherRedemption | null;

  constructor(id: string, status: string, line: Line, bundle: Bundle, usage: Usage, portability: Portability | null, productOrder: MavenirProductOrder | null, voucherRedemption: VoucherRedemption | null) {
    this.id = id;
    this.status = status;
    this.line = line;
    this.bundle = bundle;
    this.usage = usage;
    this.portability = portability;
    this.productOrder = productOrder;
    this.voucherRedemption = voucherRedemption;
  }

  changePlan(plan: Plan): Subscription | Error {
    PortalGateway.changePlan();
  }
}

/**
 * Local / roaming data on the line. Loaded with the subscription (`getUsageRequest`).
 */
class Usage {

  constructor() {
  }

}

/**
 * Owns `Collection<Subscription>`. Associates to `PortalGateway` for agreements / product order. Associates to `CcsGateway` for usage.
 */
class SubscriptionRepository {
  // << aggregation >>
  subscriptions: Collection<Subscription>;
  // << association >>
  portalGateway: PortalGateway;
  // << association >>
  ccsGateway: CcsGateway;

  constructor(subscriptions: Collection<Subscription>, portalGateway: PortalGateway, ccsGateway: CcsGateway) {
    this.subscriptions = subscriptions;
    this.portalGateway = portalGateway;
    this.ccsGateway = ccsGateway;
  }

  list(customer: Customer): Subscription[] {
    // sets Customer.subscriptions
    // active and suspended
    // bundle from latest agreementItem.product
    // number / simType from characteristics
    PortalGateway.listAgreements();
    CcsGateway.readUsage();
  }
}

/**
 * `agreementManagement/agreement?customerId=&productValues=true`. The wrap does not know Subscription.
 */
class MavenirAgreement {
  id: string;
  status: string;
  agreementType: string;
  initialDate: string;
  // MSISDN, SIM_TYPE
  characteristic: any;
  // << composition >>
  agreementItem: MavenirAgreementProduct[];

  constructor(id: string, status: string, agreementType: string, initialDate: string, characteristic: any, agreementItem: MavenirAgreementProduct[]) {
    this.id = id;
    this.status = status;
    this.agreementType = agreementType;
    this.initialDate = initialDate;
    this.characteristic = characteristic;
    this.agreementItem = agreementItem;
  }

}

/**
 * Product on the agreement. Latest `orderDate` is Paradise *Bundle* (`productOffering.id` is Plan.id).
 */
class MavenirAgreementProduct {
  id: string;
  name: string;
  description: string;
  orderDate: any;
  productPrice: any;

  constructor(id: string, name: string, description: string, orderDate: any, productPrice: any) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.orderDate = orderDate;
    this.productPrice = productPrice;
  }

}

/**
 * Cook: PATCH shoppingCart with billingAccount then `POST v2/productOrderFromCart`. Created by `Cart.createOrder`. Lives with the line after cook. The wrap does not know Cart.
 */
class MavenirProductOrder {
  id: string;

  constructor(id: string) {
    this.id = id;
  }

}

/**
 * CCS `subscriber/serviceUsage/.../subscribers/{msisdn}`.
 */
class MsisdnDataUsage {

  constructor() {
  }

}

/**
 * Agreements and product order on the Mavenir party. Party create / read / profile live in `# Customer`. Billing commits live in `# Billing`. Cart shopping-cart slice lives in `# Cart`.
 */
class PortalGateway {

  constructor() {
  }

  listAgreements(mavenirCustomerId: string): MavenirAgreement[] {
    // GET agreementManagement/agreement
  }
  createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error {
    // Create Product Order
    // always POST /customer/order
    // no body
    // 409 when done is truthy
    // when verified or portability or Plan.bypassVerified: cook
    // when cook: Vouchera.redeem then Billing.applyCredit then productOrderFromCart
    // when unverified no bypass no portability: patchSubmitOrder
    // always patchDone
    // waitingPsim true when pSIM no iccid
    // 201 { payUpFront, verified }
    GrowthBook.evaluate();
    Vouchera.redeem();
    Billing.applyCredit();
    PortalGateway.createProductOrder();
    PortalGateway.patchSubmitOrder();
    patchDone();
    patchWaitingPsim();
  }
  changePlan(mavenirCustomerId: string, plan: Plan): MavenirAgreement | Error {
  }
}

/**
 * Usage on the MSISDN. Midtier maps; it is not a type.
 */
class CcsGateway {

  constructor() {
  }

  readUsage(msisdn: string, planName: string): MsisdnDataUsage {
    // GET ccsGateway/subscriber/serviceUsage/.../subscribers/{msisdn}
  }
}

/**
 * Vouchera redeem at cook. Written on Subscription. Cart.voucher is the code.
 */
class VoucherRedemption {
  // flagged 5xx: false; cook continues
  success: boolean;
  discountAmount: number;
  totalAmount: number;

  constructor(success: boolean, discountAmount: number, totalAmount: number) {
    this.success = success;
    this.discountAmount = discountAmount;
    this.totalAmount = totalAmount;
  }

}
