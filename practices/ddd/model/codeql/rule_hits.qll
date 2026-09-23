import python
import subject_filter
import model

predicate missingTacticalStereotype(Class cls) { none() }

predicate graphRuleHit(AstNode subject, string message, AstNode contributor, string slug) {
  slug = "screen-interface-not-a-domain-object" and
  exists(Class cls |
    inSubject(cls) and
    screenClass(cls) and
    subject = cls and
    contributor = cls and
    message = "Class '" + cls.getName() + "' looks like a screen driver, not a domain type."
  )
  or
  slug = "flaccid-data-object-no-behavior" and
  exists(Class bag |
    inSubject(bag) and
    bagClass(bag) and
    subject = bag and
    contributor = bag and
    message = "Class '" + bag.getName() + "' is a field bag with no operations."
  )
  or
  slug = "building-blocks-fidelity-requires-tactical-stereotype" and
  exists(Class cls |
    missingTacticalStereotype(cls) and
    subject = cls and
    contributor = cls and
    message =
      "Class '" + cls.getName() +
        "' is missing a tactical stereotype (Entity, ValueObject, Repository, …)."
  )
  or
  slug = "domain-concepts-not-technical-names" and
  exists(Class cls |
    inSubject(cls) and
    subject = cls and
    contributor = cls and
    message = cls.getName()
  )
  or
  slug = "load-with-identity-in-hand" and
  exists(Function f |
    inSubject(f) and
    loadWithoutIdentity(f) and
    subject = f and
    contributor = f and
    message = "Operation 'load' takes no identity."
  )
  or
  slug = "repository-is-collection-lifecycle" and
  exists(Class cls |
    inSubject(cls) and
    thinRepository(cls) and
    subject = cls and
    contributor = cls and
    message =
      "Class '" + cls.getName() +
        "' is named Repository without collection lifecycle operations."
  )
  or
  slug = "service-is-homeless" and
  exists(Class cls |
    inSubject(cls) and
    homelessService(cls) and
    subject = cls and
    contributor = cls and
    message = "Class '" + cls.getName() + "' parks verbs that belong on a domain object."
  )
  or
  slug = "no-orphaned-objects" and
  exists(Class cls |
    orphanClass(cls) and
    subject = cls and
    contributor = cls and
    message = "Class '" + cls.getName() + "' has no relationship to another type."
  )
  or
  slug = "private-method-naming" and
  exists(Function f, Call call |
    inSubject(f) and
    leakedPrivate(f, call) and
    subject = f and
    contributor = call and
    message = "Private operation '" + f.getName() + "' is called from outside its definition."
  )
}
