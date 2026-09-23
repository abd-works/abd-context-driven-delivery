import python

predicate specFile(File f) {
  f.getBaseName().matches("%_spec.py") or
  f.getBaseName().matches("%spec.py") or
  f.getBaseName().matches("%_test.py")
}

bindingset[name]
predicate privateMemberName(string name) {
  name.matches("\\_%") and not name.matches("\\_\\_%")
}

predicate expectCall(Call c) { c.getFunc().(Name).getId() = "expect" }

predicate privateAttr(Attribute attr) { privateMemberName(attr.getName()) }

predicate privateProbeInExpect(Attribute attr) {
  specFile(attr.getLocation().getFile()) and
  privateAttr(attr) and
  exists(Call c | expectCall(c) and attr.getParentNode*() = c)
}

predicate mockCall(Call c) {
  c.getFunc().(Name).getId() = "patch" or
  c.getFunc().(Name).getId() = "mock" or
  c.getFunc().(Attribute).getName() = "patch" or
  c.getFunc().(Attribute).getName() = "mock" or
  c.getFunc().(Attribute).getName() = "spyOn"
}

bindingset[text]
predicate internalHelperWord(string text) {
  text.regexpMatch("(?i).*(validate|calculate|process|format|parse|helper|util|transform|convert|normalize|sanitize|build|create|make|compose).*")
}

predicate relativeInternalMock(Call c, string target) {
  specFile(c.getLocation().getFile()) and
  mockCall(c) and
  target = c.getArg(0).(StrConst).getText() and
  (target.matches("./%") or internalHelperWord(target))
}
