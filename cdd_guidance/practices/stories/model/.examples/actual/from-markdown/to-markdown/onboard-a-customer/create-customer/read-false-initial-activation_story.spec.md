## Story: Read False Initial Activation

### Scenario: Read False Initial Activation

### Background

*Given* Mavenir has a ++Mavenir customer++
*And* that ++Mavenir customer++ has a ++Mavenir shopping cart++
*But* that ++Mavenir customer++ has no ++billing account++

*When* Care is asked to read the ++Mavenir customer++ in DEP
*Then* Care sees Initial Activation
