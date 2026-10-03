/**
 * @name property-casing-transform
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node property
 * @id clean_engineering/code/property-casing-transform
 */

import javascript
import subject_filter
import model

from VarAccess acc, string message, AstNode contributor
where
  inSubject(acc) and
  acc.getName().regexpMatch("[a-z]+_[a-z]+") and
  message = "Property '" + acc.getName() + "' uses snake_case. TypeScript properties must be camelCase." and
  contributor = acc
select acc, message, contributor
