"""NLTK-backed word/POS helpers for story and naming scanners.

Requires **nltk** (and downloads WordNet / punkt / tagger data on first use). Used by
**abd-story-mapping** scanners; keep imports explicit - not re-exported from
``scanner.__init__`` to avoid import-time NLTK side effects for unrelated code.
"""

from __future__ import annotations

import socket
import sys
from typing import List, Optional, Tuple

import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn

_original_timeout = socket.getdefaulttimeout()
socket.setdefaulttimeout(2)

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    try:
        nltk.download("wordnet", quiet=True)
    except Exception as e:
        print(f"Warning: Failed to download NLTK wordnet: {e}", file=sys.stderr)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    try:
        nltk.download("punkt_tab", quiet=True)
    except Exception as e:
        print(f"Warning: Failed to download NLTK punkt_tab: {e}", file=sys.stderr)

try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
except LookupError:
    try:
        nltk.download("averaged_perceptron_tagger_eng", quiet=True)
    except Exception as e:
        print(f"Warning: Failed to download NLTK averaged_perceptron_tagger_eng: {e}", file=sys.stderr)

socket.setdefaulttimeout(_original_timeout)


class VocabularyHelper:
    AGENT_SUFFIXES = ["er", "or", "ar", "ant", "ent"]
    GERUND_SUFFIX = "ing"

    def _has_synsets(self, word: str, pos) -> bool:
        try:
            word_lower = word.lower()
            synsets = wn.synsets(word_lower, pos=pos)
            return len(synsets) > 0
        except Exception as error:
            print(f"Warning: WordNet synsets failed for {word}: {error}", file=sys.stderr)
            return False

    def is_verb(self, word: str) -> bool:
        return self._has_synsets(word, wn.VERB)

    def is_noun(self, word: str) -> bool:
        return self._has_synsets(word, wn.NOUN)

    def is_agent_noun(self, word: str) -> Tuple[bool, Optional[str], Optional[str]]:
        word_lower = word.lower()

        for suffix in self.AGENT_SUFFIXES:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                base = word_lower[: -len(suffix)]

                if self.is_verb(base):
                    return (True, base, suffix)

                if suffix == "er" or suffix == "or":
                    base_with_e = base + "e"
                    if self.is_verb(base_with_e):
                        return (True, base_with_e, suffix)

        return (False, None, None)

    def is_gerund(self, word: str) -> Tuple[bool, Optional[str]]:
        word_lower = word.lower()

        if not word_lower.endswith(self.GERUND_SUFFIX):
            return (False, None)

        if len(word_lower) <= len(self.GERUND_SUFFIX) + 2:
            return (False, None)

        base = word_lower[: -len(self.GERUND_SUFFIX)]

        if self.is_verb(base):
            return (True, base)

        base_with_e = base + "e"
        if self.is_verb(base_with_e):
            return (True, base_with_e)

        if len(base) > 1 and base[-1] == base[-2]:
            base_single = base[:-1]
            if self.is_verb(base_single):
                return (True, base_single)

        return (False, None)

    def pos_tags(self, text: str) -> List[Tuple[str, str]]:
        try:
            tokens = word_tokenize(text)
            tokens = [t for t in tokens if t.isalnum() or any(c.isalnum() for c in t)]
            return pos_tag(tokens)
        except Exception as error:
            print(f"Warning: POS tagging failed: {error}", file=sys.stderr)
            return []

    def is_verb_tag(self, tag: str) -> bool:
        verb_tags = ["VB", "VBP", "VBZ", "VBD", "VBG", "VBN"]
        return tag in verb_tags

    def is_noun_tag(self, tag: str) -> bool:
        noun_tags = ["NN", "NNS", "NNP", "NNPS"]
        return tag in noun_tags

    def is_proper_noun_tag(self, tag: str) -> bool:
        proper_noun_tags = ["NNP", "NNPS"]
        return tag in proper_noun_tags

    def is_actor_or_role(self, word: str) -> bool:
        try:
            return self._hypernym_is_actor(word.lower())
        except Exception as error:
            print(f"Warning: actor check failed for {word}: {error}", file=sys.stderr)
            return False

    def _hypernym_is_actor(self, word_lower: str) -> bool:
        synsets = wn.synsets(word_lower)
        if not synsets:
            return False
        for synset in synsets:
            hypernyms = set()
            for path in synset.hypernym_paths():
                hypernyms.update(path)
            for hypernym in hypernyms:
                name = hypernym.name().split(".")[0]
                if name in ["person", "user", "system", "agent", "entity", "causal_agent"]:
                    return True
        return False
