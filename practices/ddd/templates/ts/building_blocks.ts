/**
 * fidelity: building_blocks
 * format: ts
 *
 * One class per building block. Keep only the operations this type is allowed to have.
 * {DomainName} is the aggregate or the concept the block is about.
 */

class {DomainName} {
  /** Identity stays the same when values change. Members change with it. */
  identity = "";
  isRoot = false;
}

class {DomainName}Value {
  /** No setters. create, clone, and mix each return a new instance. */
  create(): {DomainName}Value {
    return new {DomainName}Value();
  }

  clone(): {DomainName}Value {
    return new {DomainName}Value();
  }

  mix(other: {DomainName}Value): {DomainName}Value {
    return new {DomainName}Value();
  }
}

class {DomainName}Repository {
  /** A collection. Keep any of these. search may appear more than once; name it search plus what it searches. */
  create({domainName}: {DomainName}): {DomainName} {
    return {domainName};
  }

  read(identity: string): {DomainName} {
    return new {DomainName}();
  }

  update({domainName}: {DomainName}): {DomainName} {
    return {domainName};
  }

  delete(identity: string): void {}

  searchBy{Criterion}({criterion}: string): {DomainName}[] {
    return [];
  }
}

class {DomainName}Service {
  /** No state. The operation is one no domain object can perform. */
  {operation}(): void {}
}

class {DomainName}{EventName} {
  /** The subject is the state of the event. */
  producer: {DomainName} | {DomainName}Service | null = null;
  consumers: Array<{DomainName} | {DomainName}Service> = [];
  subject: unknown = null;
}

class {DomainName}Specification {
  /** True when the candidate matches this rule. */
  isSatisfiedBy(candidate: {DomainName}): boolean {
    return false;
  }
}

class {DomainName}Factory {
  /** Builds the aggregate in a valid state. */
  create(): {DomainName} {
    return new {DomainName}();
  }
}
