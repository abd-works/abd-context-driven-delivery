"""Yamale check that a story name is a base-form verb plus a noun."""

from yamale.validators import DefaultValidators, Validator

_VERB = {"VB"}
_NOUN_PHRASE = {"JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS"}
_NOUN = {"NN", "NNS", "NNP", "NNPS"}


class VerbNoun(Validator):
    """Accept 'Submit Order' and 'Manage Customer Orders'. Reject 'Orders' and 'Customer Submits Order'."""

    tag = "verbNoun"

    def _is_valid(self, value):
        if not isinstance(value, str):
            return False
        words = value.split()
        if len(words) < 2:
            return False
        tags = [tag for _, tag in _part_of_speech(words)]
        verb, *rest = tags
        return verb in _VERB and rest[-1] in _NOUN and all(tag in _NOUN_PHRASE for tag in rest)

    def fail(self, value):
        return "'%s' is not a base-form verb followed by a noun." % (value,)


def _part_of_speech(words):
    import nltk

    return nltk.pos_tag(words)


def validators():
    """Yamale's built-in validators plus verbNoun()."""
    registered = DefaultValidators.copy()
    registered[VerbNoun.tag] = VerbNoun
    return registered
