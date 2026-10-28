// === Numbers and SIMs ===

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
    throw new Error("not implemented");
  }

  search(searchTerm: SearchTerm): AvailableNumber[] {
    throw new Error("not implemented");
  }

  reserve(id: string, previousId: string | null, portin: boolean): void | Error {
    throw new Error("not implemented");
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
    throw new Error("not implemented");
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
    throw new Error("not implemented");
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
    throw new Error("not implemented");
  }

  search(pattern: string): MavenirMsisdnResource[] {
    throw new Error("not implemented");
  }

  reserve(id: string, previousId: string | null, portin: boolean): void | Error {
    throw new Error("not implemented");
  }

  read(id: string): MavenirSimResource | Error {
    throw new Error("not implemented");
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
