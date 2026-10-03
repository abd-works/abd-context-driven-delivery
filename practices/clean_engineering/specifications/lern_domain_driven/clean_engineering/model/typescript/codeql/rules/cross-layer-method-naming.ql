/**
 * @name cross-layer-method-naming
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node function
 * @id clean_engineering/code/cross-layer-method-naming
 */

import javascript
import subject_filter
import model

from Function httpFn, string message, AstNode contributor
where
  inSubject(httpFn) and
  clientFile(httpFn.getFile()) and
  httpFn.getName().matches("fetch%") and
  message =
    "Domain method has no matching HTTP client function. Client uses '" + httpFn.getName() + "'." and
  contributor = httpFn
select httpFn, message, contributor
