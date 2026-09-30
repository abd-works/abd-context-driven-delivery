class Plan {
  id: string;
  name: string;
  price: number;
  isSellable: boolean;
  bypassVerified: boolean;

  constructor(id: string, name: string, price: number, isSellable: boolean, bypassVerified: boolean) {
    this.id = id;
    this.name = name;
    this.price = price;
    this.isSellable = isSellable;
    this.bypassVerified = bypassVerified;
  }

}

class PlanRepository {
  // << aggregation >>
  plans: Collection<Plan>;
  // << association >>
  portalGateway: PortalGateway;

  constructor(plans: Collection<Plan>, portalGateway: PortalGateway) {
    this.plans = plans;
    this.portalGateway = portalGateway;
  }

  list(): Plan[] {
  }
}

class MavenirProductOffering {
  id: string;
  name: string;
  isBundle: boolean;
  productOfferingPrice: any;
  bundledProductOffering: any;

  constructor(id: string, name: string, isBundle: boolean, productOfferingPrice: any, bundledProductOffering: any) {
    this.id = id;
    this.name = name;
    this.isBundle = isBundle;
    this.productOfferingPrice = productOfferingPrice;
    this.bundledProductOffering = bundledProductOffering;
  }

}

class PortalGateway {

  constructor() {
  }

  list(): MavenirProductOffering[] {
  }
}
