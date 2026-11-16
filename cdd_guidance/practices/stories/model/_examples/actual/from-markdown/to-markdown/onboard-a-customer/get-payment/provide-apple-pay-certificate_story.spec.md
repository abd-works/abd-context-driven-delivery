## Story: Provide Apple Pay Certificate

### Examples

#### Apple Pay certificate

| example | Apple Pay certificate | keyIdentifier | group |
| --- | --- | --- | --- |
| Bermuda Apple Pay cert | Apple Pay certificate | CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b | Apple Pay certificate |

### Scenario: Provide Apple Pay certificate

*Given* the Apple Pay merchant certificate is available
*When* My Paradise provides the Apple Pay certificate
*Then* My Paradise sends the certificate request to Apple
*When* Apple returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
*Then* My Paradise returns ++Apple Pay certificate++ ++Bermuda Apple Pay cert++
