---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Check Clean Engineering Code Through The Graph

Story map: [Check Clean Engineering Code Through The Graph](../../../../.context/story-map.md#e-check-clean-engineering-code-through-the-graph). Session release-1-2-fixes.

**Evidence mode.** Every scenario here is *Observed*: it holds today and names the code that runs it, `cdd_guidance/practices/clean_engineering/rules/code_use.py` and `code_use_rules.py`, with each rule's failing and repaired shop in `rules/code_use_examples.py`. Built on 2026-11-22 from the person's decisions in `.sessions/_backlog/check-clean-engineering-across-files.md`.

### Domain terms

- ++use++ — an edge between a class and another class (it extends, holds, creates, calls, reads, or is handed the other), a call from another class's member or from a module's function into one of its members, or a way the project reaches code besides calls and imports, as its `.context/config.json` names them under `code_reach`. A call from a spec or test code is no use: code only its own spec keeps alive is deleted with that spec.
- ++member++ — an operation, a private operation, or a property, of a class or of a module (a module's function). A module's constant is not read as a member, so no rule asks whether it is used.
- ++unseen call++ — a call the read could join to no class, because the value it is made on has no type the code says (an untyped parameter, `Any`) or for another reason (a hint naming no class read). Calls on objects from outside the code read cannot reach the project's own classes, so they do not count.

> In steps: the shop project's shop module (`shop/`) holds `cart.py`, whose class Cart adds lines and totals them, and `till.py`, whose class Till holds a cart and rings a line up on it; its orders module starts the shop from `main`, the entry point its config names.

## Story: Report Unused Class For Deletion

### Evidence

Observed (`code_use_rules.py` `DeleteUnusedClasses`, `DeleteUnusedOperations`, `CheckUseTheGraphCannotSee`).

#### Scenario: Report a class nothing uses for deletion

*Given* `cart.py` also holds the class Coupon, which no class uses and which uses no class
*When* the graph rules run
*Then* delete-unused-classes reports Coupon as no use, to delete with its specs
  *And* delete-unused-operations reports none of Coupon's operations, which go with it

#### Scenario: Pass a class another class uses

*Given* the till takes a Coupon off each line it rings up
*When* the graph rules run
*Then* delete-unused-classes reports nothing

#### Scenario: Report an operation, a private operation, a property and a module function nothing uses for deletion

*Given* Cart also has the operation clear, the private operation recount and the property empty, which nothing calls or reads
  *And* `cart.py` holds the function count_lines, which Cart's total calls, and the function count_twice, which nothing calls
*When* the graph rules run
*Then* delete-unused-operations reports clear, recount, empty and count_twice as no use, to delete with their specs
  *And* it does not report count_lines, which its own file uses

#### Scenario: Pass operations, private operations and properties that are used

*Given* count_twice is deleted, the cart's clear calls its own recount, and the till clears the cart once it has rung a line up, when the cart is not empty
*When* the graph rules run
*Then* delete-unused-operations reports nothing

#### Scenario: Count a use from example code only when production imports it

*Given* the class Printer, which only the receipt examples use, a file named as example code that nothing in production imports
*When* the graph rules run
*Then* delete-unused-classes reports Printer as no use
  *But* once the till rings up the receipt example, so production imports the example code and runs it, delete-unused-classes reports nothing

#### Scenario: Count no use from spec support the project's config names as test code

*Given* the class Printer, which only the print checks use, spec support kept under a production name
*When* the graph rules run
*Then* delete-unused-classes reports nothing, since the print checks read as production code
  *But* once the shop's config names the print checks as test code under `test_code`, delete-unused-classes reports Printer as no use

#### Scenario: List a member a library outside the code read may call as a candidate, not a violation

*Given* the shop's start builds a ShopFormatter, which extends a formatter from a library outside the code read
  *And* nothing the read sees calls ShopFormatter's example_passed
*When* the graph rules run
*Then* check-use-the-graph-cannot-see lists example_passed as a candidate for a reading
  *And* delete-unused-operations does not report it, since the library may call it as an override

#### Scenario: Count a call through a protocol as a use of each class that satisfies it

*Given* Book has price and label, and nothing calls them
*When* the graph rules run
*Then* delete-unused-operations reports price and label as no use
  *But* once the till prices whatever satisfies the protocol Priced, which Book satisfies by shape, delete-unused-operations reports nothing

#### Scenario: List a class an unseen call may use as a candidate, not a violation

*Given* `cart.py` also holds the classes Coupon and Voucher, which no class uses, and which each have value
  *And* the till takes value off an offer whose class no hint says
*When* the graph rules run
*Then* check-use-the-graph-cannot-see lists Coupon and Voucher as candidates for a reading
  *And* delete-unused-classes reports nothing

## Story: Report Operation Used Only Inside Its Module

### Evidence

Observed (`code_use_rules.py` `MakeModuleOnlyOperationsPrivate`).

#### Scenario: List a public operation only its own module calls

*Given* only the till, in the shop module, calls the cart's add and total
*When* the graph rules run
*Then* make-module-only-operations-private lists add and total as candidates for a reading

#### Scenario: Pass a public operation another module calls

*Given* the till sits in the orders module, and an app folder starts the shop
*When* the graph rules run
*Then* make-module-only-operations-private lists nothing

## Story: Report Disconnected Class

### Evidence

Observed (`code_use_rules.py` `ConnectDisconnectedClasses`).

#### Scenario: List a class joined to others only by inheritance

*Given* `receipt.py` holds Receipt, which extends Printable, and no class holds, creates or calls either
*When* the graph rules run
*Then* connect-disconnected-classes lists Printable and Receipt as candidates, each naming the relationship that may be missing

#### Scenario: Pass a class a way the project reaches code holds, such as a registry or a publishing decorator

*Given* Receipt is registered with the printers registry, which holds it
*When* the graph rules run
*Then* connect-disconnected-classes lists neither Receipt nor Printable, which the registry connects

#### Scenario: Pass a class another class holds

*Given* the till holds the receipt it prints
*When* the graph rules run
*Then* connect-disconnected-classes lists nothing

## Story: Report One-Class Package

### Evidence

Observed (`code_use_rules.py` `MergeOneClassPackages`).

#### Scenario: List a package that holds one class

*Given* the shop module's coupons package, a folder with no module card, holds only Coupon
*When* the graph rules run
*Then* merge-one-class-packages lists coupons as a candidate to merge, delete or model

#### Scenario: Pass a package that holds several classes

*Given* the coupons package holds Coupon and Voucher
*When* the graph rules run
*Then* merge-one-class-packages lists nothing
