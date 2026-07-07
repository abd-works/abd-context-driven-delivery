# Story: `Register Vehicle for Fleet`

## Story: Register Vehicle for Fleet

### Scenario 1: `ElectraVan Model-7 missing navigation is accepted for fleet registration`

*Given* a **Vehicle** *ElectraVan Model-7* is submitted for fleet registration  
  *And* the **Vehicle** has means of propulsion *electric motor 150 kW*  
*When* the **Fleet Manager** *Jane Doe* registers the **Vehicle** *ElectraVan Model-7*  
*Then* the **Vehicle** *ElectraVan Model-7* is added to the fleet registry  
  *And* the registration status is *Active*  
