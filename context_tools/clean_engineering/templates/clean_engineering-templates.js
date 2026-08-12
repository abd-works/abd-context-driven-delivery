/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 *
 * CleanEngineering JavaScript template — two files when Stories-bound:
 *
 *   {family_slug}.js                    — (I{ClassName} +) {ClassName} (+ subtypes)  PRODUCTION
 *   {type_slug}_example_factory.js      — (I{ClassName}ExampleFactory +) factory     SEPARATE
 *
 * INTERFACES ARE OPTIONAL (see clean_engineering.md § Interfaces). I{ClassName} and
 * I{ClassName}ExampleFactory below are shown because this is the richer case to
 * document — default to OMITTING both and stubbing {ClassName} / {ClassName}ExampleFactory
 * directly (empty bodies at Md, filled at S/C) unless the user asked for an interface,
 * or the module genuinely has multiple layers/implementations behind one seam.
 *
 * Naming (substitute when generating):
 *   Interface       I{ClassName}  (OPTIONAL — only when requested/needed)
 *   Class           {ClassName}  // implements I{ClassName} when one exists — production
 *   ExampleFactory  {ClassName}ExampleFactory  (plain class; no Loader base)
 *   Modes (not subclasses): Fake | Isolated | Production
 *     Fake       — mocking framework creates I{ClassName}; feed examples[{example_key}]
 *     Isolated   — new {ClassName}(...mocks/stubs via constructor injection...)
 *     Production — new {ClassName}(...real collaborators...)
 *   Members         {ownedProperty}, {operationName}, {param}, {dep}  (camelCase)
 *   Factory method  load{ExampleKey}  — loads examples[{example_key}] multi-type bundle
 *
 * Fidelity tags: L = language companion · Mu = modules · Md = model · S = specification · C = code
 * JS has no interface keyword — I{ClassName} is an empty class shell + // interface comment.
 * Do NOT generate Fake{ClassName} / Isolated{ClassName} / Production{ClassName} classes.
 * Do NOT put factories or fake-mode wiring in the production family file.
 */

// =============================================================================
// FILE: {family_slug}.js — production family only (cohesive-file)
// =============================================================================

// OPTIONAL — omit this whole class by default (see note above). Only add it
// when an interface was requested or {ClassName} has multiple implementations
// behind one seam; otherwise skip straight to `class {ClassName}` below with
// the same empty (// Md) bodies.
// interface I{ClassName}                                              // Md
class I{ClassName} {
  /** *{ClassName}* is — one sentence: what it is, its unique role. */  // L
  constructor({param}) { }                                             // Md
  get {ownedProperty}() { }                                            // Md
  get {plainProperty}() { }                                            // Md
  {operationName}({param}) { }                                         // Md
  {anotherOperation}() { }                                             // Md
}

// implements I{ClassName} — omit this comment when no interface exists     // S
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

// interface I{ChildClass} — delta only                                // Md
class I{ChildClass} {
  {deltaOperation}({param}) { }                                        // Md
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

// OPTIONAL — same opt-in rule as I{ClassName} above.
// interface I{ClassName}ExampleFactory                                // Md
class I{ClassName}ExampleFactory {
  /** Loads examples[{example_key}] as Fake | Isolated | Production. */  // L
  load{ExampleKey}() { }                                               // Md
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
