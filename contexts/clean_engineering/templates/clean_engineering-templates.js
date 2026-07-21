/**
 * # @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
 * # invoke-edit: action satisfy | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering
 *
 * CleanEngineering JavaScript template — two files when Stories-bound:
 *
 *   {family_slug}.js                    — I{ClassName} + {ClassName} (+ subtypes)  PRODUCTION
 *   {type_slug}_example_factory.js      — I{ClassName}ExampleFactory + factory     SEPARATE
 *
 * Naming (substitute when generating):
 *   Interface       I{ClassName}
 *   Class           {ClassName}  // implements I{ClassName} — production
 *   ExampleFactory  {ClassName}ExampleFactory  (plain class; no Loader base)
 *   Modes (not subclasses): Fake | Isolated | Production
 *     Fake       — mocking framework creates I{ClassName}; feed examples[{example_key}]
 *     Isolated   — new {ClassName}(...mocks/stubs via constructor injection...)
 *     Production — new {ClassName}(...real collaborators...)
 *   Members         {ownedProperty}, {operationName}, {param}, {dep}  (camelCase)
 *   Factory method  load{ExampleKey}  — loads examples[{example_key}] multi-type bundle
 *
 * Fidelity tags: L = language · Mo = modules · S = specification · C = code
 * JS has no interface keyword — I{ClassName} is an empty class shell + // interface comment.
 * Do NOT generate Fake{ClassName} / Isolated{ClassName} / Production{ClassName} classes.
 * Do NOT put factories or fake-mode wiring in the production family file.
 */

// =============================================================================
// FILE: {family_slug}.js — production family only (cohesive-file)
// =============================================================================

// interface I{ClassName}                                              // Mo
class I{ClassName} {
  /** *{ClassName}* is — one sentence: what it is, its unique role. */  // L
  constructor({param}) { }                                             // Mo
  get {ownedProperty}() { }                                            // Mo
  get {plainProperty}() { }                                            // Mo
  {operationName}({param}) { }                                         // Mo
  {anotherOperation}() { }                                             // Mo
}

// implements I{ClassName}                                             // S
class {ClassName} {
  /** *{ClassName}* is — one sentence: what it is, its unique role. */  // L
  constructor({param}) {                                               // S
    this.{plainProperty} = {param};                                    // S
  }
  get {ownedProperty}() { }                                            // S
  get {plainProperty}() { }                                            // S
  {operationName}({param}) { }                                         // S / C
  {anotherOperation}() { }                                             // S / C
  #{privateHelper}({param}) { }                                        // S / C
}

// interface I{ChildClass} — delta only                                // Mo
class I{ChildClass} {
  {deltaOperation}({param}) { }                                        // Mo
}

// implements I{ChildClass}                                            // S
class {ChildClass} extends {ClassName} {
  {deltaOperation}({param}) { }                                        // S / C
}

// =============================================================================
// FILE: {type_slug}_example_factory.js — Stories factory (separate file)
// Import production {ClassName} from ./{family_slug}.js when needed.
// Pattern only — no ExampleLoader base.
// examples[{example_key}] is a multi-type bundle (not examples[{Type}][…]).
// Fake / Isolated / Production are modes — not subclasses of I{ClassName}.
// =============================================================================

import { {ClassName} } from "./{family_slug}.js";

const examples = {
  {example_key}: {
    // multi-type bundle payloads
  },
};

// interface I{ClassName}ExampleFactory                                // Mo
class I{ClassName}ExampleFactory {
  /** Loads examples[{example_key}] as Fake | Isolated | Production. */  // L
  load{ExampleKey}() { }                                               // Mo
}

// implements I{ClassName}ExampleFactory                               // S
class {ClassName}ExampleFactory {
  /**
   * Fake: mocking framework creates I{ClassName}; feed examples[{example_key}].
   * Isolated: new {ClassName}(...constructor-injected mocks/stubs...).
   * Production: new {ClassName}(...real collaborators...).
   */                                                                  // L
  load{ExampleKey}({ mode } = { mode: "fake" }) {                      // S
    // examples[{example_key}] -> I{ClassName} (+ peers)               // S
  }
}
