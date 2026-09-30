class Plan {
  id: string;
  // after Midtier map
  name: string;
  price: number;
  isSellable: boolean;
  // dataFreedom essentials trial
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
    // Midtier maps
    // Get Data Freedom Upgrade uses the same list
    // Get Review Plan uses the same list
    // valid bundle ids: essentials, dataFreedom, ace, atlas, hiddenPromo
    // isBundle in live
    // isSellable when price > 0
    // hiddenPromo not sellable
    // name without the PROMO token
    // list order: price descending
    // Ace Best value is presentation
    PortalGateway.list();
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
    // always service provider 100000000
    // always channelName CRM
  }
}
