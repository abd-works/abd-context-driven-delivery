from mamba import before, description, it
from expects import expect

with description("a resistance check against an effect"):
    with description("that uses a defense bonus"):
        with before.each:
            ...
        with it("should set difficulty class to ten plus effect rank"):
            ...
        with description("with degrees of failure"):
            with before.each:
                ...
            with it("should map each degree to the effect condition set"):
                ...
