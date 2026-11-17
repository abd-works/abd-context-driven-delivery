"""A code channel a practice keeps renders each class model it is given as that model alone, however many it rendered
before: a practice makes each format's adapter once (PracticeFormats.adapter) and every render goes through it."""

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.java.java_class_model import JavaCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel


def _model(module: str, *classes: str) -> CleanEngineeringModel:
    """A class model of one module holding classes, in order."""
    held = Module(module, 1)
    held.classes = [OoadClass(name, order) for order, name in enumerate(classes, 1)]
    model = CleanEngineeringModel(module)
    model.modules.append(held)
    return model


# Seed: two class models rendered one after the other, as two model files rendered in one session are: the first's
# classes, then the second's, more of them.
PROMPT_NOTIFY = _model("prompt_notify", "PromptNotify", "ToastFile")
ACCOUNTS = _model("accounts", "AccountCredentials", "CredentialsValidation", "Plan")


def _class_names(channel, text: str) -> list:
    return [oclass.name for oclass in channel.parse(text).every_class()]


# Seen 2026-11-17: rendering a second model file to Python in a session named its classes after the first file's.
with description("a code channel that rendered one class model and is given another"):
    with before.each:
        self.channels = [PythonCleanEngineeringModel(), TypeScriptCleanEngineeringModel(), JavaCleanEngineeringModel()]
        for channel in self.channels:
            channel.render(PROMPT_NOTIFY)

    with it("should write the second model's classes under their own names, none of the first's"):
        written = {type(channel).__name__: _class_names(type(channel)(), channel.render(ACCOUNTS)) for channel in self.channels}
        expect(written).to(equal({type(channel).__name__: ["AccountCredentials", "CredentialsValidation", "Plan"] for channel in self.channels}))
