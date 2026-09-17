"""Sub-agent decorator - non-blocking background sub-agent dispatch.

ToolsetExtensions registration is disconnected (``register`` is a no-op).
``@sub_agent`` still marks methods; they are not enrolled on a second walk.
"""
# from . import register as _register  # disconnected — installer extensions is gone
