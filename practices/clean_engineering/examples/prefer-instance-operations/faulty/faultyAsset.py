class VocabularyHelper:
    @classmethod
    def instance(cls):
        return cls()

    @staticmethod
    def is_noun(word: str) -> bool:
        return len(word) > 0
