/**
 * @name packages
 * @kind problem
 * @id cdd/clean_engineering/nodes/packages
 */

import python

string slash(string path) { result = path.replaceAll("\\", "/") }

from Class cls, string path, string package, string mod
where
  path = slash(cls.getLocation().getFile().getRelativePath()) and
  mod = path.regexpCapture("([^/]+)/([^/]+)/[^/]+$", 1) and
  package = path.regexpCapture("([^/]+)/([^/]+)/[^/]+$", 2)
select "clean_engineering:Package:" + mod + "/" + package + ":" + package, package, "Package",
  "clean_engineering", mod + "/" + package, 1, 1, "discovery"
