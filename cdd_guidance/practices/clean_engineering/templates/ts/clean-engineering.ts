/**
 * Conceptual Clean Engineering Reference (TypeScript style)
 * Refer to cdd_guidance/references/language-tools.md for tool recommendations.
 * =============================================================================
 * Put a class family in one file: the primary type, its subtypes, and
 * tightly connected peers that only make sense together (element +
 * collection, small aggregate + its part). Name the file after the family
 * concept (`abilities.ts` for Ability + Abilities). Split into another
 * file only when a type is independently reused across families or the
 * file becomes a grab-bag. Do not default to one class per file.
 * Default: the class is the seam. An interface I{ClassName} is not the
 * default — add it in this same file when multiple implementations sit
 * behind one seam, or when the user asks. Public members only on
 * I{ClassName}; private members stay on {ClassName}. Put
 * `{ClassName}ExampleFactory` in a sibling file — never in the production
 * family file. Write each file under the module folder
 * (`{module}/{family-slug}.ts`), not beside the module.
 * Invariants, interactions, comments (model):
 *   Write each invariant as `//` on the class (or above the property /
 *   operation it constrains): a must / never / always / before / after
 *   that stays true when the object acts.
 *   Write each interaction as `-> {collaborator}.{operation}` nested
 *   under the calling operation. `-> ClassName` alone is not an interaction.
 *   State an invariant or a sequence with `//`. Leave every other line
 *   uncommented.
 * =============================================================================
 */

// FILE: {family-slug}.ts
import { {Collaborator} } from "./{collaborator-family-slug}";

// Optional — omit unless generating an interface:
export interface I{ClassName} {
  readonly {property}: {Type};
  {operation}({param}: {Type}): {ReturnType};
}

/**
 * The *{ClassName}* is {what it is for}. The {ClassName} {how it works, and who does what to whom}.
 *
 * The {ClassName} {the states it moves through: created from, starting status, each way it ends}.
 *
 * - **{Responsibility}.** The {ClassName} {does this; it asks the *{OtherClass}* to do its part}.
 * - **{Responsibility}.** The {ClassName} has a *{PartClass}*, calculated from {what}.
 */
// {must / never / always / before / after that stays true of the object}
export class {ClassName} { // or: export class {ClassName} implements I{ClassName} {
  private readonly {field}: {Type}[] = [];

  constructor(private readonly {collaborator}: {Collaborator}) {}

  get {property}(): {Type} {
    // {must / never / always / before / after about this property}
    return this.{field}[0];
  }

  {operation}({param}: {Type}): {ReturnType} {
    // {must / never / always / before / after when this operation runs}
    // -> {collaborator}.{operation}
    return this.{privateHelper}({param});
  }

  private {privateHelper}({param}: {Type}): {ReturnType} {
    return this.{collaborator}.{operation}({param});
  }
}

// FILE: {type-slug}-example-factory.ts
export class {ClassName}ExampleFactory {
  load{ExampleKey}(mode: "fake" | "real" = "fake"): {ClassName} {
    throw new Error("not implemented");
  }
}
