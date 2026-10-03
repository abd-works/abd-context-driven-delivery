/**
 * @name consistent-view-naming
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node function
 * @id clean_engineering/code/consistent-view-naming
 */

import javascript
import subject_filter
import model

from Function f, string message, AstNode contributor
where
  inSubject(f) and
  clientFile(f.getFile()) and
  f.getName().matches("%Page") and
  message = "Component '" + f.getName() + "' does not end with 'View'." and
  contributor = f
select f, message, contributor
