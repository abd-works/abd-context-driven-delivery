class MsisdnInventoryRepository {
  // << aggregation >>
  availableNumbers: Collection<AvailableNumber>;
  // << association >>
  inventoryGateway: InventoryGateway;

  constructor(availableNumbers: Collection<AvailableNumber>, inventoryGateway: InventoryGateway) {
    this.availableNumbers = availableNumbers;
    this.inventoryGateway = inventoryGateway;
  }

  list(size: number, category: string): AvailableNumber[] {
    // always size 5 when picking a new number
    // always size 1 when bringing a number
    // new-number category always standard
    // listing premium inventory category always premium
    // always available to locked
    InventoryGateway.list();
  }
  search(searchTerm: SearchTerm): AvailableNumber[] {
    // when SearchTerm.converted is the pattern
    // always available to locked
    InventoryGateway.search();
  }
  reserve(id: string, previousId: string | null, portin: boolean): void | Error {
    // always locked to reserved
    // premium selected id: always locked to reserved
    // premium portin always false
    // category is always on list
    // when previousId is present, previousId must go reserved to available
    // when portin: kv_tempNumber
    InventoryGateway.reserve();
  }
}

class IccidInventoryRepository {
  // << aggregation >>
  availableSims: Collection<AvailableSim>;
  // << association >>
  inventoryGateway: InventoryGateway;

  constructor(availableSims: Collection<AvailableSim>, inventoryGateway: InventoryGateway) {
    this.availableSims = availableSims;
    this.inventoryGateway = inventoryGateway;
  }

  read(id: string): AvailableSim | Error {
    // available only
    // empty or not-available is miss
    InventoryGateway.read();
  }
}

class AvailableNumber {
  id: string;

  constructor(id: string) {
    this.id = id;
  }

}

class AvailableSim {
  id: string;

  constructor(id: string) {
    this.id = id;
  }

}

class SearchTerm {
  input: string;
  converted: string;

  constructor(input: string, converted: string) {
    this.input = input;
    this.converted = converted;
  }

  convert(): string {
    // when input is letters, converted is always keypad digits
  }
}

class MavenirMsisdnResource {
  id: string;
  // always available, locked, or reserved
  resourceStatus: string;

  constructor(id: string, resourceStatus: string) {
    this.id = id;
    this.resourceStatus = resourceStatus;
  }

}

class InventoryGateway {

  constructor() {
  }

  list(size: number, category: string): MavenirMsisdnResource[] {
    // always size 5 when picking a new number
    // always size 1 when bringing a number
    // new-number category always standard
    // listing premium inventory category always premium
    // always available to locked
  }
  search(pattern: string): MavenirMsisdnResource[] {
    // always available to locked
  }
  reserve(id: string, previousId: string | null, portin: boolean): void | Error {
    // always locked to reserved
    // premium selected id: always locked to reserved
    // premium portin always false
    // category is always on list
    // when previousId is present, previousId must go reserved to available
    // when portin: kv_tempNumber
  }
  read(id: string): MavenirSimResource | Error {
    // GET sim resource
    // when none: none
    // when not-available: none
  }
}

class MavenirSimResource {
  id: string;
  // available passes
  resourceStatus: string;

  constructor(id: string, resourceStatus: string) {
    this.id = id;
    this.resourceStatus = resourceStatus;
  }

}
