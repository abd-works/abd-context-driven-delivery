/**
 * @name include-all-external-dependencies
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node module
 * @id clean_engineering/code/include-all-external-dependencies
 */

import javascript
import subject_filter
import model

from ImportDeclaration imp, string path, string message, AstNode contributor
where
  inSubject(imp) and
  importedPath(imp, path) and
  path = "lodash" and
  message = "Import 'lodash' is not declared in package.json." and
  contributor = imp
select imp, message, contributor
