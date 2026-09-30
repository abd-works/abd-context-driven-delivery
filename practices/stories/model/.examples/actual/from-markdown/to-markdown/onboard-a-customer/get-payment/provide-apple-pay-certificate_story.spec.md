## Story: Provide Apple Pay Certificate

### Scenario: Provide Apple Pay certificate

*Given* the Apple Pay merchant certificate is available
*When* My Paradise provides the Apple Pay certificate
*Then* My Paradise sends the certificate request to Apple
*When* Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
*Then* My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
