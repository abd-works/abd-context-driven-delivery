class Line {
  msisdn: string | null;
  // << association >>
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

class Subscription {
  // MavenirAgreement.id
  id: string;
  // active | suspended | terminated | pendingActive
  status: string;
  // << composition >>
  // number, simType, iccid, portability live on Line
  line: Line;
  // << composition >>
  // from Cart
  // same snapshot pickPlan wrote
  // agreementItem.product / productOffering
  bundle: Bundle;
  // << composition >>
  usage: Usage;
  // << association >>
  // from Porting
  // from Cart.portability when they brought a number
  portability: Portability | null;
  // << association >>
  // Cart.createOrder / PortalGateway.createProductOrder
  productOrder: MavenirProductOrder | null;
  // << association >>
  // cook: Vouchera.redeem on Cart.voucher
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

class Usage {

  constructor() {
  }

}

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

class MavenirProductOrder {
  id: string;

  constructor(id: string) {
    this.id = id;
  }

}

class MsisdnDataUsage {

  constructor() {
  }

}

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

class CcsGateway {

  constructor() {
  }

  readUsage(msisdn: string, planName: string): MsisdnDataUsage {
    // GET ccsGateway/subscriber/serviceUsage/.../subscribers/{msisdn}
  }
}

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
