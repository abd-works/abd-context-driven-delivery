# ddd-ubiquitous-language

- **entry_id:** 2c6bd516
- **artifact:** tests/domain/.context/domain-model.drawio
- **rule:** (ddd) ubiquitous-language
- **wrong:** PortabilityRequest is not a valid DDD domain concept — it is service-oriented architecture terminology. The real concept is a telephone number that has been ported, carrying PortingInformation (donorOperator, accountNumber, portNumber, etc.). The aggregate should be PhoneNumber or TelephoneNumber with a PortingInformation value object, and the method on Subscription should be port() not requestPortability().
- **status:** fixed