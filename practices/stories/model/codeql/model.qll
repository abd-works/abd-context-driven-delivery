import python

predicate storyCall(Call call, string name) {
  call.getFunc().(Name).getId() = "story" and
  name = call.getArg(0).(StrConst).getText()
}

predicate scenarioCall(Call call, string name) {
  call.getFunc().(Name).getId() = "scenario" and
  name = call.getArg(0).(StrConst).getText()
}

predicate withCall(With w, Call call) { call = w.getContextExpr() }

predicate storyWith(With w, string name) {
  exists(Call call | withCall(w, call) and storyCall(call, name))
}

predicate scenarioWith(With w, string name) {
  exists(Call call | withCall(w, call) and scenarioCall(call, name))
}

bindingset[name]
string firstToken(string name) {
  result = name.regexpCapture("\\s*([A-Za-z][A-Za-z\\-']*).*", 1).toLowerCase()
}

predicate knownVerb(string token) {
  token =
    [
      "add", "allow", "approve", "assign", "attach", "block", "build", "cancel",
      "capture", "check", "clear", "close", "collect", "compare", "complete",
      "confirm", "connect", "convert", "create", "delete", "deliver", "deny",
      "display", "download", "edit", "enable", "enter", "export", "fetch",
      "filter", "generate", "grant", "handle", "import", "invite", "issue",
      "list", "load", "lock", "manage", "merge", "move", "notify", "onboard",
      "open", "pay", "place", "post", "process", "publish", "read", "record",
      "refund", "register", "reject", "release", "remove", "rename", "reset",
      "resolve", "return", "review", "run", "save", "scan", "schedule", "search",
      "select", "send", "share", "show", "sign", "split", "start", "stop",
      "store", "submit", "subscribe", "sync", "unlock", "update", "upload",
      "validate", "verify", "view"
    ]
}

predicate actorNoun(string token) {
  token =
    [
      "customer", "user", "system", "admin", "operator", "treasurer", "approver",
      "auditor", "merchant", "partner", "service", "api", "backend", "frontend",
      "database", "browser", "client", "server"
    ]
}

bindingset[token]
predicate gerundToken(string token) { token.regexpMatch("[a-z]+ing") }

bindingset[token]
predicate nominalisationToken(string token) {
  token.regexpMatch("[a-z]+(?:tion|sion|ment|ance|ence|ity|ness)")
}

bindingset[name]
predicate verbWithoutNoun(string name) {
  knownVerb(firstToken(name)) and
  not name.regexpMatch("\\S+\\s+\\S.*")
}

bindingset[name]
predicate notVerbNounName(string name) {
  verbWithoutNoun(name)
  or
  gerundToken(firstToken(name))
  or
  nominalisationToken(firstToken(name))
  or
  actorNoun(firstToken(name))
  or
  not knownVerb(firstToken(name))
}

predicate nestedIn(With inner, With outer) {
  inner != outer and
  inner.getLocation().getFile() = outer.getLocation().getFile() and
  inner.getLocation().getStartLine() >= outer.getLocation().getStartLine() and
  inner.getLocation().getEndLine() <= outer.getLocation().getEndLine()
}

int scenarioCount(With story) {
  storyWith(story, _) and
  result = count(With sc | nestedIn(sc, story) and scenarioWith(sc, _))
}

predicate tooFewOrManyScenarios(With story) {
  exists(int n | n = scenarioCount(story) and n > 0 and (n < 4 or n > 9))
}

bindingset[a, b]
int charDiff(string a, string b) {
  a.length() = b.length() and
  result =
    count(int i |
      i in [0 .. a.length() - 1] and
      a.toLowerCase().charAt(i) != b.toLowerCase().charAt(i)
    )
}

bindingset[a, b]
predicate similarSiblingNames(string a, string b) {
  a.length() > 6 and
  b.length() > 6 and
  a.toLowerCase() != b.toLowerCase() and
  (
    exists(int d |
      d = charDiff(a, b) and
      d > 0 and
      d <= 2
    )
    or
    a.toLowerCase().prefix(a.length() - 1) = b.toLowerCase().prefix(b.length() - 1)
  )
}

predicate siblingStories(string a, string b, File file) {
  exists(With left, With right |
    storyWith(left, a) and
    storyWith(right, b) and
    left.getLocation().getFile() = file and
    right.getLocation().getFile() = file and
    a < b
  )
}

predicate domainIdent(string ident) {
  exists(Class cls |
    ident = cls.getName() and
    ident.length() > 2
  )
  or
  exists(Function f |
    ident = f.getName() and
    not ident.matches("\\_%") and
    ident.length() > 2
  )
}

bindingset[storyName, ident]
predicate storyMentionsIdent(string storyName, string ident) {
  storyName.toLowerCase().matches("%" + ident.toLowerCase() + "%")
}

bindingset[storyName]
predicate tracesToDomain(string storyName) {
  exists(string ident | domainIdent(ident) and storyMentionsIdent(storyName, ident))
}

predicate untracedStory(Call call, string name) {
  storyCall(call, name) and
  exists(Class cls) and
  not tracesToDomain(name)
}
