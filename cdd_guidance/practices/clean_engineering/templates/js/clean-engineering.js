/**
 * Conceptual Clean Engineering Reference (JavaScript style)
 * Refer to cdd_guidance/references/language-tools.md for tool recommendations.
 * =============================================================================
 * Put a class family in one file: the primary type, its subtypes, and
 * tightly connected peers that only make sense together (element +
 * collection, small aggregate + its part). Name the file after the family
 * concept (`abilities.js` for Ability + Abilities). Split into another
 * file only when a type is independently reused across families or the
 * file becomes a grab-bag. Do not default to one class per file.
 * The class is the seam. Private members start with `#`. Put
 * `{ClassName}ExampleFactory` in a sibling file — never in the production
 * family file. Write each file under the module folder
 * (`{module}/{family-slug}.js`), not beside the module, and import with the
 * file's extension.
 * Invariants, interactions, comments (model):
 *   Write each invariant as `//` on the class (or above the property /
 *   operation it constrains): a must / never / always / before / after
 *   that stays true when the object acts.
 *   Write each interaction as `-> {collaborator}.{operation}` nested
 *   under the calling operation. `-> ClassName` alone is not an interaction.
 *   State an invariant or a sequence with `//`. Leave every other line
 *   uncommented. Name each type in JSDoc where the code cannot.
 * =============================================================================
 */

// FILE: {family-slug}.js
import { {Collaborator} } from "./{collaborator-family-slug}.js";

/**
 * The *{ClassName}* is {what it is for}. The {ClassName} {how it works, and who does what to whom}.
 *
 * The {ClassName} {the states it moves through: created from, starting status, each way it ends}.
 *
 * - **{Responsibility}.** The {ClassName} {does this; it asks the *{OtherClass}* to do its part}.
 * - **{Responsibility}.** The {ClassName} has a *{PartClass}*, calculated from {what}.
 */
// {must / never / always / before / after that stays true of the object}
export class {ClassName} {
  /** @type {{Type}[]} */
  #{field} = [];
  #{collaborator};

  /** @param {{Collaborator}} {collaborator} */
  constructor({collaborator}) {
    this.#{collaborator} = {collaborator};
  }

  /** @returns {{Type}} */
  get {property}() {
    // {must / never / always / before / after about this property}
    return this.#{field}[0];
  }

  /** @param {{Type}} {param} @returns {{ReturnType}} */
  {operation}({param}) {
    // {must / never / always / before / after when this operation runs}
    // -> {collaborator}.{operation}
    return this.#{privateHelper}({param});
  }

  #{privateHelper}({param}) {
    return this.#{collaborator}.{operation}({param});
  }
}

// FILE: {type-slug}-example-factory.js
export class {ClassName}ExampleFactory {
  load{ExampleKey}(mode = "fake") {
    throw new Error("not implemented");
  }
}
