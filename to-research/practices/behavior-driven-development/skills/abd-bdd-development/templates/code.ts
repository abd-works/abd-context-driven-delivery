// =============================================================================
// BDD Development Template — TypeScript Production Module
// =============================================================================
// Instructions (for skill maintainers — delete this block when generating):
//
//   1. Replace {DomainEntity} with the class name from the test.
//   2. Add only properties and methods that failing tests demand.
//   3. Start with a function if state is not required; add a class only when
//      tests require accumulated state or polymorphism.
//   4. No properties without a test asserting on them.
//   5. No methods without a test calling them.
//   6. Delete this instruction block before committing the file.
// =============================================================================

// Types — add only what tests reference
interface {DomainEntityProps} {
  // include only properties tests pass to the constructor
}

export class {DomainEntity} {
  readonly {readonlyProp}: {Type};
  {mutableProp}: {Type} = {initialValue};

  constructor({ {propA}, {propB} }: {DomainEntityProps}) {
    this.{readonlyProp} = {propA};
    // initialize only what tests assert on
  }

  {action}({param}: {ParamType}): void {
    // implement only what makes the failing test GREEN
    this.{mutableProp} += {param};
  }
}

// -------------------------------------------------------------------------
// Function alternative (prefer functions until state demands a class)
// -------------------------------------------------------------------------
// export function create{DomainEntity}(data: {DomainEntityProps}): {ReturnType} {
//   if (!data.{validationField}) throw new Error('{DomainEntity}: {field} is required');
//   return {
//     {prop}: data.{prop},
//     // return only what tests assert on
//   };
// }
