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
  }
  search(searchTerm: SearchTerm): AvailableNumber[] {
  }
  reserve(id: string, previousId: string | null, portin: boolean): void | Error {
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
  }
}

class MavenirMsisdnResource {
  id: string;
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
  }
  search(pattern: string): MavenirMsisdnResource[] {
  }
  reserve(id: string, previousId: string | null, portin: boolean): void | Error {
  }
  read(id: string): MavenirSimResource | Error {
  }
}

class MavenirSimResource {
  id: string;
  resourceStatus: string;

  constructor(id: string, resourceStatus: string) {
    this.id = id;
    this.resourceStatus = resourceStatus;
  }

}
