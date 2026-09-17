fidelity: engineer
scope: Increment 1 ? templates + instructions + format converters (py / js / md)

flow:
  status: ready-to-proceed
  recommend: ready-to-proceed
  next: done
  note: CE + Stories converters (py/js/md) done with thin tests. Review Increment 1.
  open: []
  done:
    - pass #eng-scope
    - pass #eng-formats-py-js-md
    - pass #gen-ce-spec
    - pass #gen-stories-spec
    - pass #eng-ce-conv
    - pass #eng-stories-conv
    - pass #eng-tests

=========
theme: Connect Story Examples  (epic)
---------
stories:
    Connect Story Examples
        Generate Interface Extensions
            Generator --> Generate Type Extending Interface
                pass #eng-ce-conv
        Generate Stories That Import Factories
            Generator --> Generate Epic That Imports Factories
                pass #eng-stories-conv
            Generator --> Generate Sub-Epic That Imports Factories
            Generator --> Generate Scenario Steps That Call Factory Methods
        Demonstrate Story Scenarios
            * approx later
    ~> Increment 1: CE + Stories converters py/js/md
---
ce:
    ensure_example_factory_family + companion_interface_name
    channels: python | javascript | markdown
    pass #eng-ce-conv
stories:
    Epic.example_factories ? helper imports (py/js) + MD Example factories line
    pass #eng-stories-conv
=========

## log
- engineer / grill / pass #eng-scope
- engineer / grill / pass #eng-formats-py-js-md
- engineer / generate / pass #eng-ce-conv
- engineer / generate / pass #eng-stories-conv
- engineer / generate / pass #eng-tests
