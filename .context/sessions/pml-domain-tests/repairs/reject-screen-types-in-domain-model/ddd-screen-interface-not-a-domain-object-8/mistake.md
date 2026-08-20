# ddd-screen-interface-not-a-domain-object-8

- **entry_id:** f8192a08
- **artifact:** tests/domain/line-portability/line-portability.ts (LinePortability interface)
- **rule:** (ddd) screen-interface-not-a-domain-object
- **wrong:** LinePortability modeled as its own wizard interface with open(), isInfoStepShowing(), continueFromInfo(), isFormStepShowing(), port(), submitWithoutFilling(), validationMessage(), goBackToServices() — a screen driver. Post-purchase porting is an operation on Subscriber (port(info)). LinePortability should be removed; its port() operation belongs on Subscriber.
- **status:** fixed
