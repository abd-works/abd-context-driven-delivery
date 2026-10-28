// === Subscription ===

class Line {
  msisdn: string | null;
  // << association >>
  simType: SimType | null;
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
    throw new Error("not implemented");
  }

  attachIccid(iccid: string): void | Error {
    throw new Error("not implemented");
  }

  activateSim(iccid: string): void | Error {
    throw new Error("not implemented");
  }
}

class Subscription {
  id: string;
  status: string;
  // << composition >>
  line: Line;
  // << composition >>
  bundle: Bundle;
  // << composition >>
  usage: Usage;
  // << association >>
  portability: Portability | null;
  // << association >>
  productOrder: MavenirProductOrder | null;
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
    throw new Error("not implemented");
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
    throw new Error("not implemented");
  }
}

class MavenirAgreement {
  id: string;
  status: string;
  agreementType: string;
  initialDate: string;
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
    throw new Error("not implemented");
  }

  createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error {
    throw new Error("not implemented");
  }

  changePlan(mavenirCustomerId: string, plan: Plan): MavenirAgreement | Error {
    throw new Error("not implemented");
  }
}

class CcsGateway {
  constructor() {
  }

  readUsage(msisdn: string, planName: string): MsisdnDataUsage {
    throw new Error("not implemented");
  }
}

class VoucherRedemption {
  success: boolean;
  discountAmount: number;
  totalAmount: number;

  constructor(success: boolean, discountAmount: number, totalAmount: number) {
    this.success = success;
    this.discountAmount = discountAmount;
    this.totalAmount = totalAmount;
  }
}
