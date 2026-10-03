/**
 * @name use-valid-package-names
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node module
 * @id clean_engineering/code/use-valid-package-names
 */

import javascript
import subject_filter
import model

from ImportDeclaration imp, string path, string message, AstNode contributor
where
  inSubject(imp) and
  importedPath(imp, path) and
  placeholderScope(path) and
  message = "Import '" + path + "' uses a placeholder npm scope." and
  contributor = imp
select imp, message, contributor
