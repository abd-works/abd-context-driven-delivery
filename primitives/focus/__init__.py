"""focus - @focus decorator for focus-group binding.

Public exports:
    focus   - @focus(focus="fidelities") on @action or @instruction

On @action: ActionExpander appends {module_dir}/{focus}/{filter_value}.md to prose.
On @instruction: sets group/filter_key so the slot resolves that same path.
"""
from focus._decorator import focus

__all__ = ["focus"]
