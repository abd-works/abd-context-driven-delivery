/**
 * @name maintain-layer-purity
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node class
 * @id clean_engineering/code/maintain-layer-purity
 */

import javascript
import subject_filter
import model

from ImportDeclaration imp, string path, string message, AstNode contributor
where
  inSubject(imp) and
  importedPath(imp, path) and
  coreFile(imp.getFile()) and
  forbiddenFrameworkPath(path) and
  message = "Domain core has forbidden framework import: " + path and
  contributor = imp
select imp, message, contributor
